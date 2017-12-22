#!/usr/bin/env python3
import click
import boto3

from freeipa_org_demo.reset import reset as demo_reset
from freeipa_org_demo.config import ec2_configuration

@click.command()
@click.option('--debug', is_flag=True,
              help='Print debugging information')
@click.option("--unattended", is_flag=True,
              help="Run unattended")
@click.option("--no-rebuild", 'rebuild', flag_value=False, default=True,
              help="Do not rebuild the demo instance")
@click.option("--no-eip", 'eip', flag_value=False, default=True,
              help="Do not update EIP of the demo instance")
@click.option("--instance-type", type=str, default=ec2_configuration['instance_type'],
              help="Instance type (defaults to {})".format(ec2_configuration['instance_type']))
def cli(debug, unattended, rebuild, eip, instance_type):
    demo_reset(debug, unattended, rebuild, eip, instance_type)

if __name__ == '__main__':
    cli()

# Triggered by Amazon AWS
def handler(event, context):
    print("Run FreeIPA Demo Lambda", event, context)
    demo_reset(debug=True,
               unattended=True,
               rebuild=True,
               eip=True,
               instance_type=ec2_configuration['instance_type'])
    print("FreeIPA Demo Lambda finished")
    return {'message': "FreeIPA Demo sucessfully (re)started"}
