import boto3
import os

AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
EC2_AMI_ID = os.getenv("EC2_AMI_ID")
EC2_SERVICE = os.getenv("EC2_SERVICE")
EC2_IAM_INSTANCE_PROFILE = os.getenv("EC2_IAM_INSTANCE_PROFILE")
EC2_KEY_NAME_PAIR = os.getenv("EC2_KEY_NAME_PAIR")
EC2_TAG_KEY_GROUP = os.getenv("EC2_TAG_KEY_GROUP")
EC2_TAG_VALUE_GROUP = os.getenv("EC2_TAG_VALUE_GROUP")
EC2_INSTANCE_TYPE = os.getenv("EC2_INSTANCE_TYPE")
EC2_SECURITY_GROUP_ID = os.getenv("EC2_SECURITY_GROUP_ID")
EC2_APP_INSTANCE_NAME_TAG = os.getenv("EC2_APP_INSTANCE_NAME_TAG")
EC2_APP_INSTANCE_NAME_VALUE_PREFIX = os.getenv("EC2_APP_INSTANCE_NAME_VALUE_PREFIX")

ec2Client = boto3.client(EC2_SERVICE,
                   region_name=AWS_REGION,
                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def createEC2Instance(instanceNumber):
    response = ec2Client.run_instances(
        ImageId=EC2_AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType=EC2_INSTANCE_TYPE,
        SecurityGroupIds=[EC2_SECURITY_GROUP_ID],
        Placement={'AvailabilityZone': 'us-east-1b'},
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': EC2_TAG_KEY_GROUP,
                        'Value': EC2_TAG_VALUE_GROUP
                    },
                    {
                        'Key': EC2_APP_INSTANCE_NAME_TAG,
                        'Value': EC2_APP_INSTANCE_NAME_VALUE_PREFIX + str(instanceNumber),
                    }
                ]
            },
        ],
        KeyName=EC2_KEY_NAME_PAIR,
    )
    print("Created Instance with Id : " + response['Instances'][0]['InstanceId'])


def describeEC2Instances():
    instances = ec2Client.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': [EC2_TAG_KEY_GROUP]},
            {'Name': 'tag-value', 'Values': [EC2_TAG_VALUE_GROUP]}
        ]
    )
    return instances
def getCountOfInstances(state):
    ec2Response = ec2Client.describe_instances(
        Filters=[
            {
                'Name': 'tag:{0}'.format(EC2_TAG_KEY_GROUP),
                'Values': [EC2_TAG_VALUE_GROUP]
            },
            {
                'Name': 'instance-state-name',
                'Values': state
            },
            {
                'Name': 'availability-zone',
                'Values': ['us-east-1b']
            }
        ]
    )
    return len(ec2Response["Reservations"])

def getInstancesToStop(stoppedStates):
    try:
        instancesToStop = []

        ec2Response = ec2Client.describe_instances(
            Filters=[
                {'Name': 'tag:{0}'.format(EC2_TAG_KEY_GROUP), 'Values': [EC2_TAG_VALUE_GROUP]},
                {'Name': 'instance-state-name', 'Values': stoppedStates}
            ]
        )
        for reservation in ec2Response["Reservations"]:
            instancesToStop.extend(reservation['Instances'])
        instancesToStop.sort(key=lambda x: x['LaunchTime'])
        return instancesToStop
    except Exception as e:
        print(f"Error getting instances to stop: {str(e)}")
        return []

def terminateInstances(instanceIds):
    ec2Response = ec2Client.terminate_instances(
        InstanceIds=instanceIds
    )
    if 'TerminatingInstances' in ec2Response:
        for instance in ec2Response['TerminatingInstances']:
            print(f"Terminating Instance with ID: {instance['InstanceId']}")
    else:
        print("Failed to terminate instances.")
