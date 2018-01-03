# FreeIPA Demo
Tools for building or managing [FreeIPA Public Demo].

## Building
### Installing Dependencies
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Configuring AWS access
This step requires AWS *Access Key ID* and *Secret Access Key* for FreeIPA Demo AWS instance.
```
aws configure
```
### Building for AWS Lambda
Zip file for AWS Lambda can be built with
```
./build.sh
```
The resulting zip file then needs to be uploaded via AWS Console.

## Usage
```
./freeipa_org_demo_reset.py --help
./freeipa_org_demo_check.py --help
```

   [FreeIPA Public Demo]: <https://www.freeipa.org/page/Demo>
