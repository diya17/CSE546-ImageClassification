import utils.ec2 as ec2Util
import utils.sqs as sqsUtil
import time
import os

SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
MESSAGE_THRESHOLD = os.getenv("MESSAGE_THRESHOLD")
appTierInstanceId = 1
def scaleServiceUp():
    prevQueueSize = 0
    while(True):
        currentQueueSize = sqsUtil.getNumberOfQueueMessages(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
        print("Current number of messages in the queue " + str(currentQueueSize))
        numberOfPendingOrRunningInstances = ec2Util.getCountOfPendingOrRunningInstances()
        print("Current number of instances in the app-tier " + str(numberOfPendingOrRunningInstances))

        newMessagesDelta = currentQueueSize - prevQueueSize
        prevQueueSize = currentQueueSize
        if newMessagesDelta > int(MESSAGE_THRESHOLD):
            numberOfInstancesToCreate = min(newMessagesDelta, 19-numberOfPendingOrRunningInstances)
            createEC2Instances(numberOfInstancesToCreate)
        time.sleep(5)

def createEC2Instances(numberOfInstancesToCreate):
    for i in range(1, numberOfInstancesToCreate+1):
        ec2Util.createEC2Instance(appTierInstanceId)
        appTierInstanceId = (appTierInstanceId+1)%19
        if appTierInstanceId == 0:
            appTierInstanceId = 1
