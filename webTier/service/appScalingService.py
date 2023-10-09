import utils.ec2 as ec2Util
import utils.sqs as sqsUtil
import time
import os

SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
MESSAGE_THRESHOLD = os.getenv("MESSAGE_THRESHOLD")
PENDING_AND_RUNNING_INSTANCES = ["pending", "running"]
STOPPED_INSTANCES = ["stopped"]
class AppScalingService():

    def __init__(self):
        self.prevQueueSize = 0
        self.appTierInstanceId = 1
    def scaleServiceUp(self):
        while (True):
            currentQueueSize = sqsUtil.getNumberOfQueueMessages(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
            print("Current number of messages in the queue " + str(currentQueueSize))
            numberOfPendingOrRunningInstances = ec2Util.getCountOfInstances(PENDING_AND_RUNNING_INSTANCES)
            if numberOfPendingOrRunningInstances is None:
                numberOfPendingOrRunningInstances = 0
            print("Current number of instances in the app-tier " + str(numberOfPendingOrRunningInstances))
            newMessagesDelta = currentQueueSize - self.prevQueueSize
            self.prevQueueSize = currentQueueSize
            if newMessagesDelta > 0:
                numberOfInstancesToCreate = min(newMessagesDelta, 19 - numberOfPendingOrRunningInstances)
                self.createEC2Instances(numberOfInstancesToCreate)
            time.sleep(5)

    def createEC2Instances(self, numberOfInstancesToCreate):
        for i in range(1, numberOfInstancesToCreate + 1):
            ec2Util.createEC2Instance(self.appTierInstanceId)
            self.appTierInstanceId = (self.appTierInstanceId + 1) % 19
            if self.appTierInstanceId == 0:
                self.appTierInstanceId = 1

    def scaleServiceDown(self):
        while True:
            currentQueueSize = sqsUtil.getNumberOfQueueMessages(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
            print("Current number of messages in the queue " + str(currentQueueSize))
            
            numberOfStoppedInstances = ec2Util.getCountOfInstances(STOPPED_INSTANCES)
            if numberOfStoppedInstances is None:
                numberOfStoppedInstances = 0
            print("Current number of stopped instances in the app-tier " + str(numberOfStoppedInstances))
            if numberOfStoppedInstances > 0:
                pass
                #self.terminateEC2Instances(numberOfStoppedInstances)
        
    def terminateEC2Instances(self, number_of_instances_to_terminate):
        try:
            instances_to_terminate = ec2Util.getInstancesToStop(number_of_instances_to_terminate, STOPPED_INSTANCES)
            if instances_to_terminate:
                instance_ids = [instance['InstanceId'] for instance in instances_to_terminate]
                response = ec2Util.getInstancesToStop(InstanceIds=instance_ids)
                if 'TerminatingInstances' in response:
                    for instance in response['TerminatingInstances']:
                        print(f"Terminating Instance with ID: {instance['InstanceId']}")
                else:
                    print("Failed to terminate instances.")
            else:
                print("No instances to terminate.")
        except Exception as e:
            print(f"Error terminating instances: {str(e)}")

