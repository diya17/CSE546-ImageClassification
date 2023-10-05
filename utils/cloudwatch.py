import boto3
import ec2 as ec2Util
import os

ALARM_NAME = os.getenv("ALARM_NAME")
ALARM_DESCRIPTION = os.getenv("ALARM_DESCRIPTION")
METRIC_NAME = os.getenv("METRIC_NAME")
NAMESPACE = os.getenv("NAMESPACE")
THRESHOLD = os.getenv("THRESHOLD")

cloudwatchClient = boto3.client('cloudwatch')


instances = ec2Util.describeEC2Instances()

# Create alarms for each tagged instance
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instanceId = instance['InstanceId']
        # Create the alarm for this instance
        cloudwatchClient.put_metric_alarm(
            AlarmName=f'{ALARM_NAME}-{instanceId}',
            AlarmDescription=ALARM_DESCRIPTION,
            MetricName=METRIC_NAME,
            Namespace=NAMESPACE,
            Statistic='Average',
            ComparisonOperator='GreaterThanThreshold',
            Threshold=THRESHOLD,
            Period=300,  # Specify the evaluation period in seconds
            EvaluationPeriods=1,
            Dimensions=[{'Name': 'InstanceId', 'Value': instanceId}],
            Unit='Percent'
        )
