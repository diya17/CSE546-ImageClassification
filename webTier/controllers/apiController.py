import collections
from flask import request,jsonify
from webTier import app
from webTier.service import uploadService as uploadService
from webTier.service import resultsService as resultsService

usersToFileMap = collections.defaultdict(set)

@app.route('/api/upload', methods=['POST'])
def uploadFiles():
    userIp = request.remote_addr
    print(request.files.get("myfile"))
    print(len(request.files.getlist('files')))
    print(userIp)
    if userIp:
        uploadService.processUploadFileForApi(request.files.getlist('files'), userIp, usersToFileMap, len(request.files.getlist('files')), False)
        result = resultsService.generateResultsForUser(userIp, usersToFileMap)
        return jsonify(result)
    elif len(request.files.getlist('files')) == 1:
        resultFileName = uploadService.processUploadFileForApi(request.files.getlist('files'), userIp, usersToFileMap, len(request.files.getlist('files')), False)
        result = resultsService.generateResultForFile(resultFileName)
        return result
    return "Invalid File Upload"
@app.route('/api/upload/file', methods=['POST'])
def uploadFile():
    userIp = request.remote_addr
    if userIp:
        resultFileName = uploadService.processUploadFileForApi([request.files.get("myfile")], userIp, usersToFileMap, 1, True)
        result = resultsService.generateResultForFile(resultFileName)
        return result
    return "Invalid File Upload"
