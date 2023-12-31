import boto3
import os
import time

AWS_REGION = os.getenv("AWS_REGION")
SQS_SERVICE = os.getenv("SQS_SERVICE")
MESSAGE_THRESHOLD = os.getenv("MESSAGE_THRESHOLD")
SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")

sqsClient = boto3.client(SQS_SERVICE, region_name=AWS_REGION)

def sendImageFileInputToSQS(sqsQueueUrl, s3PathToFile, sqsMessageGroupId):
    timestamp = int(time.time() * 1000)
    messageId = s3PathToFile + '_' + str(timestamp)
    sqsClient.send_message(
        QueueUrl=sqsQueueUrl,
        MessageBody=s3PathToFile,
        MessageGroupId=sqsMessageGroupId,
        MessageDeduplicationId=messageId
    )


def receiveImageUrlFromSQS(sqsQueueUrl):
    receivedItems = []
    response = sqsClient.receive_message(
        QueueUrl=sqsQueueUrl,
        AttributeNames=['SentTimestamp'],
        MaxNumberOfMessages=int(MESSAGE_THRESHOLD),
        MessageAttributeNames=['All'],
        VisibilityTimeout=1,
        WaitTimeSeconds=7
    )
    if "Messages" not in response:
        pass
    else:
        for message in response["Messages"]:
            receivedItem = message["Body"]
            receivedItems.append(receivedItem)
            sqsClient.delete_message(
                QueueUrl=sqsQueueUrl, ReceiptHandle=message["ReceiptHandle"]
            )
    return receivedItems

def getNumberOfQueueMessages(queueURL):
    sqsResponse = sqsClient.get_queue_attributes(
        QueueUrl= SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    return int(sqsResponse['Attributes']['ApproximateNumberOfMessages'])
