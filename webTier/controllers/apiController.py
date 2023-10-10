import collections
from flask import request,jsonify
from webTier import app
from webTier.service import uploadService as uploadService
from webTier.service import resultsService as resultsService

usersToFileMap = collections.defaultdict(set)

@app.route('/api/upload', methods=['POST'])
def uploadFiles():
    userIp = request.remote_addr
    if userIp:
        if len(request.files.getlist('files')) > 1:
            uploadService.processUploadFileForApi(request.files.getlist('files'), userIp, usersToFileMap, len(request.files.getlist('files')))
            result = resultsService.generateResultsForUser(userIp, usersToFileMap)
            return jsonify(result)
        elif len(request.files.getlist('files')) == 1:
            resultFileName = uploadService.processUploadFileForApi(request.files.getlist('files'), userIp, usersToFileMap, len(request.files.getlist('files')))
            result = resultsService.generateResultForFile(resultFileName)
            return result
    return "Invalid File Upload"
