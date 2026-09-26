import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'eu-central-1')
EC2_INSTANCE_ID = os.getenv('EC2_INSTANCE_ID')

def get_ec2_client():
    return boto3.client(
        'ec2',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def get_ec2_status() -> str:
    if not AWS_ACCESS_KEY_ID or not EC2_INSTANCE_ID:
        return "CONFIG ERROR (Missing Keys)"
    try:
        ec2 = get_ec2_client()
        response = ec2.describe_instances(InstanceIds=[EC2_INSTANCE_ID])
        return response['Reservations'][0]['Instances'][0]['State']['Name'].upper()
    except Exception as e:
        return f"ERROR: {str(e)}"

def start_ec2_instance():
    if not AWS_ACCESS_KEY_ID or not EC2_INSTANCE_ID:
        return False, "❌ Missing AWS configuration in .env."
    try:
        ec2 = get_ec2_client()
        ec2.start_instances(InstanceIds=[EC2_INSTANCE_ID])
        return True, "🚀 Sent **START** signal to AWS EC2 Instance."
    except Exception as e:
        return False, f"❌ AWS Error: {str(e)}"

def stop_ec2_instance():
    if not AWS_ACCESS_KEY_ID or not EC2_INSTANCE_ID:
        return False, "❌ Missing AWS configuration in .env."
    try:
        ec2 = get_ec2_client()
        ec2.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
        return True, "🛑 Sent **STOP** signal to AWS EC2 Instance."
    except Exception as e:
        return False, f"❌ AWS Error: {str(e)}"