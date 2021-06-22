#!/usr/bin/env python3

import boto3
import configparser
import os
import sys

# Usage:
#   assume_role.py --role-arn arn:aws:iam::12345678912:role/SomeRoleName --duration 1600
#   --session-name test-session --profile TestProfile --credentials-file ~/.aws/credentials --region us-east-1

def assume_role():
    print(f"Attempting to assume role {args['role-arn']}...")
    client = boto3.client("sts")
    creds = client.assume_role(
        DurationSeconds=args["duration"],
        RoleArn=args["role-arn"],
        RoleSessionName=args["session-name"]
    )

    return creds['Credentials']

def parse_args():
    global args
    args = {}
    args["credentials-file"] = f"{os.environ['HOME']}/.aws/credentials"
    args["duration"] = 3600
    args["profile"] = "Python"
    args["region"] = "us-east-1"
    args["session-name"] = "python-session"

    for i in range(1, len(sys.argv)):
        if sys.argv[i][0:2] == "--":
            arg_name = sys.argv[i].replace("--", "").strip()
            args[arg_name] = sys.argv[i + 1].strip()

def set_profile(creds):
    print(f"Configuring profile {args['profile']} with assume role credentials...")
    creds_file = args["credentials-file"]
    profile_name = args["profile"]
    config = configparser.ConfigParser()
    config.read(creds_file)

    if not config.has_section(profile_name):
        config.add_section(profile_name)

    config.set(profile_name, "aws_access_key_id", creds["AccessKeyId"])
    config.set(profile_name, "aws_secret_access_key", creds["SecretAccessKey"])
    config.set(profile_name, "aws_session_token", creds["SessionToken"])
    config.set(profile_name, "region", args["region"])

    with open(creds_file, 'w+') as configfile:
        config.write(configfile)

parse_args()
creds = assume_role()
set_profile(creds)
print(f"Successfully assumed role {args['role-arn']}. Exiting.")
