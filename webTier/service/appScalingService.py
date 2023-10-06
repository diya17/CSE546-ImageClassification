import utils.ec2 as ec2Util
import utils.sqs as sqsUtil
import time
import os

SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
MESSAGE_THRESHOLD = os.getenv("MESSAGE_THRESHOLD")
class AppScalingService():

    def __init__(self):
        self.prevQueueSize = 0
        self.appTierInstanceId = 1
    def scaleServiceUp(self):
        while (True):
            currentQueueSize = sqsUtil.getNumberOfQueueMessages(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
            print("Current number of messages in the queue " + str(currentQueueSize))
            numberOfPendingOrRunningInstances = ec2Util.getCountOfPendingOrRunningInstances()
            if numberOfPendingOrRunningInstances is None:
                numberOfPendingOrRunningInstances = 0
            print("Current number of instances in the app-tier " + str(numberOfPendingOrRunningInstances))

            newMessagesDelta = currentQueueSize - self.prevQueueSize
            self.prevQueueSize = currentQueueSize
            if newMessagesDelta > int(MESSAGE_THRESHOLD):
                numberOfInstancesToCreate = min(newMessagesDelta, 19 - numberOfPendingOrRunningInstances)
                self.createEC2Instances(numberOfInstancesToCreate)
            time.sleep(5)

    def createEC2Instances(self, numberOfInstancesToCreate):
        for i in range(1, numberOfInstancesToCreate + 1):
            ec2Util.createEC2Instance(self.appTierInstanceId)
            self.appTierInstanceId = (self.appTierInstanceId + 1) % 19
            if self.appTierInstanceId == 0:
                self.appTierInstanceId = 1
