#!/bin/bash
set -e
TARGET="/tmp/freeipa-demo-reset.zip"

echo "Building to $TARGET"

rm $TARGET
zip -q -r $TARGET freeipa_org_demo_reset.py
pushd venv/lib/python3.6/site-packages/ > /dev/null
zip -q -r9 -g /tmp/freeipa-demo-reset.zip .
popd > /dev/null

echo "Built $TARGET"
