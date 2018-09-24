#!/usr/bin/env python3
import click
import boto3

from freeipa_org_demo.clean import purge_old_instances
from freeipa_org_demo.config import ec2_configuration

@click.command()
@click.option('--debug', is_flag=True,
              help='Print debugging information')
@click.option('--dry-run', is_flag=True,
              help='Dry run - instance is not really removed')
@click.option("--instance-name", type=str, default=ec2_configuration['instance_instance_name'],
              help="Instance name (defaults to {})".format(ec2_configuration['instance_instance_name']))
@click.option("--instance-min-age", type=int, default=ec2_configuration['instance_purge_min_age'],
              help="Instance min age in seconds (defaults to {})".format(ec2_configuration['instance_purge_min_age']))
def cli(debug, instance_name, instance_min_age, dry_run):
    purge_old_instances(debug=debug,
                        instance_name=instance_name,
                        min_age=instance_min_age,
                        dry_run=dry_run)

if __name__ == '__main__':
    cli()

# Triggered by Amazon AWS
def handler(event, context):
    print("Run FreeIPA Demo Cleanup Lambda", event, context)
    purge_old_instances(
            debug=False,
            instance_name=ec2_configuration['instance_instance_name'],
            min_age=ec2_configuration['instance_purge_min_age'],
            dry_run=False)
    print("FreeIPA Demo Check Lambda finished")
    return {'message': "FreeIPA Demo Cleanup sucessful"}

