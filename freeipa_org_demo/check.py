import time
import boto3
import dns.resolver
import dns.name
import requests

from .config import ec2_configuration, demo_configuration
from .utils import configure_logger

class CheckError(Exception):
    pass

def check(debug):
    logger = configure_logger(debug)
    logger.info("Start FreeIPA check")

    logger.info("Check DNS")
    soa = dns.resolver.query(demo_configuration['dns_zone'], 'SOA')

    demo_check_name = dns.name.from_text(demo_configuration['dns_demo_hostname'])
    if soa[0].mname != demo_check_name:
        raise CheckError("DNS error: SOA MNAME does not match")

    a = dns.resolver.query(demo_check_name, 'A')
    if len(a) > 1:
        raise CheckError("DNS error: too many A records")

    if a[0].address != ec2_configuration['instance_elastic_ip']:
        raise CheckError("DNS error: A name does not match: {}".format(a[0].address))

    logger.info("Check web availability")
    demo_index_url = 'https://{}'.format(demo_configuration['dns_demo_hostname'])
    r = requests.get(demo_index_url)

    if r.status_code != requests.codes.ok:
        raise CheckError("Web error: index page does not load")

    logger.info("Check user login")
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html',
    }
    demo_login_url = 'https://{}/ipa/session/login_password'.format(demo_configuration['dns_demo_hostname'])

    for user_name in demo_configuration['users']:
        logger.debug("Check login of user {}".format(user_name))
        data = {
            'user': user_name,
            'password': demo_configuration['user_password'],
        }
        s = requests.Session()
        r = s.post(demo_login_url,
               headers=headers,
               data=data)

        if r.status_code != requests.codes.ok:
            raise CheckError("Web error: user {} could not authenticate".format(user_name))

        if 'ipa_session' not in s.cookies:
            raise CheckError("Web error: session did not store for user {}".format(user_name))
