import boto3
import os
from utils import s3 as s3Service
from utils import sqs as sqsService

SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL")
userResultMap = {}
resultMap = {}

def generateResultsForUser(userIp, usersToFileMap):
    if not userResultMap.get(userIp):
        userResultMap[userIp] = []

    while len(userResultMap[userIp]) < len(usersToFileMap[userIp]):
        outputURLs = sqsService.receiveImageUrlFromSQS(SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL)
        
        for outputURL in outputURLs:
            result_userIp, result_key, image_classification = s3Service.retrieveResultObjectFromS3(outputURL)
            if result_userIp == userIp:
                image_result = {result_key: image_classification}
                userResultMap[userIp].append(image_result)
    del(usersToFileMap[userIp])
    for image_result in userResultMap[userIp]:
        print(f"User: {userIp}, Result: {image_result}")
    result = userResultMap[userIp]
    del(userResultMap[userIp])
    return result

def generateResultForFile(resultFile):
    while True:
        outputURLs = sqsService.receiveImageUrlFromSQS(SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL)

        for outputURL in outputURLs:
            resultUserIp, resultKey, imageClassification = s3Service.retrieveResultObjectFromS3(outputURL)
            resultMap[resultKey] = imageClassification
        if resultFile in resultMap.keys():
            result = resultMap[resultFile]
            del(resultMap[resultFile])
            return result