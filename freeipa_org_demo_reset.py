#!/usr/bin/env python3
import sys
import time
import tempfile
import os
import subprocess
import logging
import logging.handlers
import traceback
import click

import boto3

"""
Docs:
- http://boto3.readthedocs.io/en/latest/guide/ec2-example-managing-instances.html
- http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
"""

logger = logging.getLogger('demo1.freeipa.org')
logger.setLevel(logging.WARNING)

EC2_REGION = 'eu-central-1'

INSTANCE_IMAGE_NAME = 'freeipa-demo-*'
INSTANCE_TYPE = 't2.small'
INSTANCE_SECURITY_GROUPS = ['FreeIPA']
INSTANCE_SSH_KEY = 'id_rsa_freeipa_demo'
INSTANCE_ELASTIC_IP = '52.57.162.88'

# FreeIPA settings
USERS = ['admin', 'employee', 'manager', 'helpdesk']
USER_PASSWORD = 'Secret123'

krb5_conf = """
includedir /var/lib/sss/pubconf/krb5.include.d/

[libdefaults]
  default_realm = DEMO1.FREEIPA.ORG
  dns_lookup_realm = true
  dns_lookup_kdc = true
  rdns = false
  ticket_lifetime = 24h
  forwardable = yes
  default_ccache_name = KEYRING:persistent:%{uid}

[realms]
  DEMO1.FREEIPA.ORG = {
    pkinit_anchors = FILE:/etc/ipa/ca.crt
  }

[domain_realm]
  .demo1.freeipa.org = DEMO1.FREEIPA.ORG
  demo1.freeipa.org = DEMO1.FREEIPA.ORG
"""

def print_log(text):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print("%s: %s" % (str_time, text))

def yes_no(question, unattended, default='y'):
    if unattended:
        reply = default
    else:
        reply = str(input('{} (y/n): '.format(question))).lower().strip()
    if reply[0] == 'y':
        return True
    return False

@click.command()
@click.option('--debug', is_flag=True,
              help='Print debugging information')
@click.option("--unattended", is_flag=True,
              help="Run unattended")
@click.option("--no-rebuild", 'rebuild', flag_value=False, default=True,
              help="Do not rebuild the demo instance")
@click.option("--no-eip", 'eip', flag_value=False, default=True,
              help="Do not update EIP of the demo instance")
@click.option("--instance-type", type=str, default=INSTANCE_TYPE,
              help="Instance type (defaults to {})".format(INSTANCE_TYPE))
def cli(debug, unattended, rebuild, eip, instance_type):
    reset_demo(debug, unattended, rebuild, eip, instance_type)

def reset_demo(debug=False, unattended=False, rebuild=True, eip=True, instance_type=INSTANCE_TYPE):
    print("Called with", debug, unattended, rebuild, eip, instance_type)
    if debug:
        logger.setLevel(logging.DEBUG)
        level = logging.DEBUG
    else:
        level = logging.WARNING

    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    ec2 = boto3.resource('ec2', region_name=EC2_REGION)
    ec2_client = boto3.client('ec2', region_name=EC2_REGION)
    sts = boto3.client('sts')
    ec2_client_id = sts.get_caller_identity().get('Account')

    instances = ec2.instances.all()
    logger.debug("INSTANCES")
    for instance in instances:
        logger.debug("- {} [{}]: AMI {}, key {}, state {}".format(
            instance.id,
            instance.instance_type,
            instance.image_id,
            instance.key_name,
            instance.state,
            ))

    images = ec2.images.filter(Owners=[ec2_client_id])
    logger.debug("Available images")
    for image in images:
        logger.debug("- {}: {}".format(image.id, image.name))

    # Select source image
    images = list(ec2.images.filter(
        Owners=[ec2_client_id],
        Filters=[{'Name': 'name', 'Values':[INSTANCE_IMAGE_NAME]}]))

    if not images:
        logger.critical("Cannot find instance with filter '{}'".format(INSTANCE_IMAGE_NAME))
        sys.exit(1)
    image_map = dict((i.name, i) for i in images)
    image_map_names = list(image_map.keys())
    image_map_names.sort()
    logger.debug("Filtered images (last one will be selected): {}".format(image_map_names))
    instance_image = image_map[image_map_names[-1]]
    logger.debug("TARGET IMAGE: {} ({})".format(instance_image.id, instance_image.name))

    response = ec2_client.run_instances(
        ImageId=instance_image.id,
        InstanceType=instance_type,
        MaxCount=1,
        MinCount=1,
        Monitoring={'Enabled': False},
        SecurityGroups=INSTANCE_SECURITY_GROUPS,
        KeyName=INSTANCE_SSH_KEY,
        IamInstanceProfile={'Name': 'freeipa-org-demo-iam'},
        )

    new_instance_id = response['Instances'][0]['InstanceId']
    logger.debug("NEW INSTANCE: {}".format(new_instance_id))
    instance = ec2.Instance(new_instance_id)

    try:
        logger.debug("Waiting on public IP...")
        while True:
            if instance.public_ip_address:
                logger.debug("Public IP: {}".format(instance.public_ip_address))
                break
            instance.reload()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("... continue, interrupted")

    if eip:
        logger.debug("Allocate Elastic IP address")
        eip_addrs = ec2_client.describe_addresses(PublicIps=[INSTANCE_ELASTIC_IP])
        old_instance_id = eip_addrs['Addresses'][0].get('InstanceId')

        if old_instance_id:
            logger.info("Instance {} is pointing at EIP {}".format(old_instance_id, INSTANCE_ELASTIC_IP))
            logger.debug("Remove old instance pointed from EIP?")
            reply = yes_no('Terminate {}?'.format(old_instance_id), unattended)
            if reply:
                ec2_client.disassociate_address(PublicIp=INSTANCE_ELASTIC_IP)
                ec2_client.terminate_instances(InstanceIds=[old_instance_id])
            else:
                logger.debug("Skipping")

        # FIXME: can fail with botocore.exceptions.ClientError: An error
        # occurred (InvalidInstanceID) when calling the AssociateAddress
        # operation: The pending instance 'i-07b9d9187311e650d' is not in
        # a valid state for this operation.
        response = ec2_client.associate_address(
            InstanceId=new_instance_id,
            PublicIp=INSTANCE_ELASTIC_IP,
            AllowReassociation=False,
        )
        logger.debug("New public (elastic) IP: {}".format(INSTANCE_ELASTIC_IP))
        instance.reload()
    else:
        logger.debug("Skipping EIP allocation")

    try:
        logger.debug("Waiting on fully initialized")
        while True:
            instance_status_obj = ec2_client.describe_instance_status(InstanceIds=[new_instance_id])
            instance_status = instance_status_obj['InstanceStatuses'][0]['InstanceStatus']['Status']
            if instance_status == 'initializing':
                pass
            elif instance_status == 'ok':
                logger.debug("Instance ready")
                break
            else:
                raise RuntimeError("Instance health check failed!")

            time.sleep(5)
    except KeyboardInterrupt:
        logger.debug("... continue, interrupted")

    reply = yes_no('Start FreeIPA?', unattended)
    if reply:
        logger.debug("Starting FreeIPA")
        ssm_client = boto3.client('ssm')
        commands = ['systemctl start ipa.service']
        resp = ssm_client.send_command(
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': commands},
            InstanceIds=[new_instance_id],
            TimeoutSeconds=60,
            Comment="Starting FreeIPA"
        )
        logger.debug("Result: {}".format(resp))

    else:
        logger.debug("Skipping")

    reply = yes_no('Terminate current instance?', unattended, default='n')
    if reply:
        logger.debug("Terminating")
        ec2_client.terminate_instances(InstanceIds=[instance.id])
    else:
        logger.debug("Skipping instance termination")

if __name__ == '__main__':
    cli()

# Triggered by Amazon AWS
def handler(event, context):
    print("Run FreeIPA Demo Lambda", event, context)
    reset_demo(unattended=True,
               eip=True,
               debug=True)
    print("FreeIPA Demo Lambda finished")
    return {'message': "FreeIPA Demo sucessfully (re)started"}
