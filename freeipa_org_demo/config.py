ec2_configuration = {
    'ec2_region': 'eu-central-1',
    'instance_image_name': 'freeipa-demo-*',
    'instance_type': 't2.small',
    'instance_security_groups': ['FreeIPA'],
    'instance_ssh_key': 'id_rsa_freeipa_demo',
    'instance_elastic_ip': '52.57.162.88',
}

demo_configuration = {
    'users': ['admin', 'employee', 'manager', 'helpdesk'],
    'user_password': 'Secret123',
}
