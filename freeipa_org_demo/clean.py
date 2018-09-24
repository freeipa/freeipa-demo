import datetime
import boto3

from .utils import yes_no, configure_logger
from .config import ec2_configuration, demo_configuration

def purge_old_instances(debug, instance_name, min_age=0):
    print("Called with", debug, instance_name, min_age)
    logger = configure_logger(debug)

    ec2 = boto3.resource('ec2', region_name=ec2_configuration['ec2_region'])
    ec2_client = boto3.client('ec2', region_name=ec2_configuration['ec2_region'])
    sts = boto3.client('sts')
    ec2_client_id = sts.get_caller_identity().get('Account')

    logger.debug("Looking for instances with name {}".format(instance_name))
    instances = list(ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}]))

    count = len(instances)

    if count <= 1:
        logger.info("Found {} instance --> OK".format(count))
        return

    logger.debug("Found {} instances --> check!".format(count))

    eip_addrs = ec2_client.describe_addresses(
        PublicIps=[ec2_configuration['instance_elastic_ip']])
    live_instance_id = eip_addrs['Addresses'][0].get('InstanceId')
    logger.debug("Live instance demo: {}".format(live_instance_id))

    instances_to_purge = [i for i in instances if i.id != live_instance_id]

    if len(instances_to_purge) == len(instances):
        error = "Something is wrong, trying to purge all live instances!"
        logger.error(error)
        raise RuntimeError(error)

    for instance in instances_to_purge:
        current_time = datetime.datetime.now(instance.launch_time.tzinfo)
        instance_age = (current_time - instance.launch_time).total_seconds()
        logger.debug("Instance {}: age {:.0f} seconds".format(instance.id, instance_age))

        if instance_age > min_age:
            logger.info("Instance {}: age {:.0f} is bigger than limit --> PURGE".format(
                instance.id, instance_age))

            ec2_client.terminate_instances(InstanceIds=[instance.id])
