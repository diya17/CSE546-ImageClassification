from flask import Flask, render_template, request, make_response
from flask_bootstrap import Bootstrap
from model.FilesForm import FilesForm
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
Bootstrap(app)
allowedFileExtensions = ['JPEG']

@app.route('/', methods=['GET', 'POST'])
def index():
    uploadFilesForm = FilesForm(request.form)
    resp = make_response(render_template("index.html", form=uploadFilesForm))
    if request.method == "POST" and uploadFilesForm.validate():
        listOfFiles = []
        if request.cookies.get('uploadedFiles') is not None:
            listOfFiles = json.loads(request.cookies.get('uploadedFiles'))
        for uploadedFile in request.files.getlist('files'):
            if uploadedFile.content_type != 'image/jpeg' and uploadedFile.content_type != 'image/png':
                uploadFilesForm.files.errors.append(uploadedFile.filename + " Files Need to be a jpeg or png image.")
                continue

            if len(uploadedFile.filename) > 0:
                fileName = secure_filename(uploadedFile.filename)
                listOfFiles.append(fileName)
        resp.set_cookie('uploadedFiles', json.dumps(listOfFiles))

    return resp

if __name__ == '__main__':
    app.run(debug=True)
