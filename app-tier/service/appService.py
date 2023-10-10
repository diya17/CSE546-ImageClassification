#!/usr/bin/env python3
import os
import sys
sys.path.append("/home/ubuntu/")
sys.path.append("/home/ubuntu/app-tier/")
from utils import s3 as s3Util
from utils import sqs as sqsUtil
from image_classification import ImageClassifier
import time
import multiprocessing

BATCH_SIZE = os.getenv("BATCH_SIZE")
SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL")
SQS_IMAGE_CLASSIFICATION_OUTPUT_MESSAGE_GROUP_ID = os.getenv("SQS_IMAGE_CLASSIFICATION_OUTPUT_MESSAGE_GROUP_ID")
INPUT_LOCAL_STORAGE_DIR = os.getenv("INPUT_LOCAL_STORAGE_DIR")

def processDownloadImagesFromS3():
    emptyQueueFlag = 0
    receivedMessages = sqsUtil.receiveImageUrlFromSQS(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
    if len(receivedMessages) == 0:
        emptyQueueFlag = 1
    else:
        pool = multiprocessing.Pool(processes=len(receivedMessages))
        pool.map(s3Util.downloadImageFromS3ToLocal, receivedMessages)
        pool.close()
        pool.join()
    
    return emptyQueueFlag

def clearImagesFromLocal():
    files = os.listdir(os.path.join(INPUT_LOCAL_STORAGE_DIR,"user-input"))
    for fileName in files:
        file_path = os.path.join(INPUT_LOCAL_STORAGE_DIR,"user-input", fileName)
        if os.path.isfile(file_path):
            os.remove(file_path)

def processGenerateOutput():
    emptyQueueCounter = 0
    imageClassifier = ImageClassifier(INPUT_LOCAL_STORAGE_DIR)

    while emptyQueueCounter < 3: #Check to determine empty Request SQS queue
        emptyQueueFlag = processDownloadImagesFromS3() #Receive s3 location urls and download images from s3 to local
        if emptyQueueFlag == 1:
            emptyQueueCounter += 1
        else:
            emptyQueueCounter = 0
        
            outputJson = imageClassifier.modelInference(int(BATCH_SIZE)) #Perform Image Classification
            
            outputList = [(imageName, imageResult) for imageName, imageResult in outputJson.items()] #Pushing the outputs parallely to S3 output bucket
            pool = multiprocessing.Pool(processes=len(outputList))
            s3PathList = pool.starmap(s3Util.addResultObjectToS3, outputList)
            pool.close()
            pool.join()

            for s3PathToFile in s3PathList: #Passing the S3 location URLs corresponding to the outputs sequentially to the Response SQS queue
                sqsUtil.sendImageFileInputToSQS(SQS_IMAGE_CLASSIFICATION_OUTPUT_QUEUE_URL, s3PathToFile, SQS_IMAGE_CLASSIFICATION_OUTPUT_MESSAGE_GROUP_ID, False)
            
            clearImagesFromLocal() #Clear all images in the local directory once processing is finished

            #time.sleep(300) #TODO: need to check whether the process must be paused in between each iteration of message processing
    
    with open(os.path.join(INPUT_LOCAL_STORAGE_DIR, "emptyQueueCounter.txt"), 'w') as file:
        file.write(str(emptyQueueCounter))
    
if __name__ == '__main__':
    processGenerateOutput()

        
