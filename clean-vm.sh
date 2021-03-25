#!/bin/bash
ipactl stop
truncate -s0 /var/log/audit/audit.log
truncate -s0 /var/log/httpd/error_log
truncate -s0 /var/log/httpd/access_log
truncate -s0 /var/log/krb5kdc.log
rm /var/log/dirsrv/slapd-DEMO1-FREEIPA-ORG/*
