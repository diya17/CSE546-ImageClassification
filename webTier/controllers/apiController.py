import collections
from flask import request,jsonify
from webTier import app
from webTier.service import uploadService as uploadService
from webTier.service import resultsService as resultsService

usersToFileMap = collections.defaultdict(set)

@app.route('/api/upload', methods=['POST'])
def uploadFile():
    userIp = request.remote_addr
    if userIp:
        uploadService.processUploadFileForApi(request.files.getlist('files'), userIp, usersToFileMap, True)
    print(usersToFileMap)
    result = resultsService.generateResultsForUser(userIp, usersToFileMap)
    return jsonify(result)

