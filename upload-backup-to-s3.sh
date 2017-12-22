#!/bin/bash
set -e

S3_BUCKET="freeipa-org-backups"
S3_BUCKET_BACKUP_PATH="freeipa-org-demo"

BACKUP_LIST="/var/log/httpd/error_log /var/log/httpd/access_log /var/log/dirsrv/slapd-DEMO1-FREEIPA-ORG/access /var/log/dirsrv/slapd-DEMO1-FREEIPA-ORG/errors /var/log/krb5kdc.log"
BACKUP_ARCHIVE_NAME="freeipa_demo1_logs_`date +%Y%m%d-%H%M%S`.tar.gz"
BACKUP_ARCHIVE_PATH="/tmp/$BACKUP_ARCHIVE_NAME"

TEMP_DIR=`mktemp -d`
cp $BACKUP_LIST $TEMP_DIR
pushd $TEMP_DIR > /dev/null
tar -czf $BACKUP_ARCHIVE_PATH *
popd > /dev/null
rm -rf $TEMP_DIR

aws s3 cp $BACKUP_ARCHIVE_PATH s3://$S3_BUCKET/$S3_BUCKET_BACKUP_PATH/
rm -f $BACKUP_ARCHIVE_PATH
