ec2_configuration = {
    'ec2_region': 'eu-central-1',
    'instance_image_name': 'freeipa-demo-*',
    'instance_instance_name': 'freeipa-org-demo',
    'instance_type': 't2.small',
    'instance_security_groups': ['FreeIPA'],
    'instance_ssh_key': 'id_rsa_freeipa_demo',
    'instance_elastic_ip': '52.57.162.88',
}

demo_configuration = {
    'dns_zone': 'demo1.freeipa.org',
    'dns_demo_hostname': 'ipa.demo1.freeipa.org',
    'users': ['admin', 'employee', 'manager', 'helpdesk'],
    'user_password': 'Secret123',
}
