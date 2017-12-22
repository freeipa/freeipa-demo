#!/bin/bash
set -e
TARGET="/tmp/freeipa-org-demo.zip"

echo "Building to $TARGET"

rm -f $TARGET
zip -q -r $TARGET *.py freeipa_org_demo
pushd venv/lib/python3.6/site-packages/ > /dev/null
zip -q -r9 -g $TARGET .
popd > /dev/null

echo "Built $TARGET"
