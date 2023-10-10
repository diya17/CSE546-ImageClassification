import boto3
import os
from webTier.s3 import retrieveResultObjectFromS3  

SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL = os.getenv("SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL")
s3Client = boto3.client('s3')
sqsClient = boto3.client('sqs')
userResultMap = {}

def generateResultsForUser(userIp, usersToFileMap):
    if not userResultMap.get(userIp):
        userResultMap[userIp] = []

    while len(userResultMap[userIp]) < len(usersToFileMap[userIp]):
        outputURLs = sqsClient.receiveImageUrlFromSQS(SQS_IMAGE_CLASSIFICATION_INPUT_QUEUE_URL)
        
        for outputURL in outputURLs:
            [result_userIp, result_key, image_classification] = retrieveResultObjectFromS3(outputURL)
            if result_userIp == userIp:
                image_result = {result_key: image_classification}
                userResultMap[userIp].append(image_result)

    for image_result in userResultMap[userIp]:
        print(f"User: {userIp}, Result: {image_result}")

    return userResultMap[userIp]



# for uploaded_file in usersToFileMap[userIp]:
    #     filename, extension = os.path.splitext(uploaded_file)
    #     s3_key = f"{userIp}/{filename}"

    #     try:
    #         response = s3Client.get_object(Bucket=OUTPUT_BUCKET_NAME, Key=s3_key)
    #         result = response['Body'].read().decode('utf-8')

    #         results.append((uploaded_file, result))

    #         print(f"{uploaded_file} uploaded!")

    #     except Exception as e:
            
    #         print(f"Error retrieving result for {uploaded_file}: {str(e)}")
    # if results:
    #     for filename, result in results:
    #         print(f"{filename} uploaded! Result: {result}")
    # else:
    #     print(f"No results found for {userIp}")
    # return results 

        
    