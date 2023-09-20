from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from model.FilesForm import FilesForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
Bootstrap(app)
allowedFileExtensions = ['JPEG']

@app.route('/', methods=['GET', 'POST'])
def index():
    uploadFilesForm = FilesForm(request.form)
    if request.method == "POST" and uploadFilesForm.validate():
        for uploadedFile in request.files.getlist('files'):
            if uploadedFile.content_type != 'image/jpeg' or uploadedFile.content_type != 'image/png':
                uploadFilesForm.files.errors.append(uploadedFile.filename + " Files Need to be a jpeg or png image.")
                continue

            if len(uploadedFile.filename) > 0:
                fileName = secure_filename(uploadedFile.filename)


    return render_template("index.html", form=uploadFilesForm)

if __name__ == '__main__':
    app.run(debug=True)
