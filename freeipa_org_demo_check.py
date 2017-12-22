#!/usr/bin/env python3
import click
import boto3

from freeipa_org_demo.check import check as demo_check

@click.command()
@click.option('--debug', is_flag=True,
              help='Print debugging information')
def cli(debug):
    demo_check(debug)

if __name__ == '__main__':
    cli()

# Triggered by Amazon AWS
def handler(event, context):
    print("Run FreeIPA Demo Check Lambda", event, context)
    demo_check(debug=False)
    print("FreeIPA Demo Check Lambda finished")
    return {'message': "FreeIPA Demo check sucessful"}

