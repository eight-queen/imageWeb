from flask import Flask, render_template, flash, redirect, request, session, send_file, abort
from flask_restful import Api, reqparse
import os
from flask_sqlalchemy import SQLAlchemy 

from io import BytesIO
from scipy import misc


APP_NAME = "ImageServer"
app = Flask(__name__, static_url_path='', static_folder='')

api = Api(app, prefix='/api/v1.0',)
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=0)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filesstorage.db'
db = SQLAlchemy(app)


class FileContents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)



@app.before_first_request
def before_first_request():
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, "filesstorage.db")
    if not os.path.exists(database_path):
        db.create_all()
        db.session.commit()



@app.route('/')
@app.route('/index')
def index():
    user = {'temp_user': 'Bob'}
    if not session.get('logged_in'):
        return render_template('index.html', title = 'Home')
    else:
        #return "Hello Bob!  <a href='/logout'>Logout</a>" 
        return render_template('upload.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == '12345' and request.form['username'] == 'bob':
        session['logged_in'] = True
    else:
        return "wrong password! <a href='/index'> Login </a>"
    return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files['inputFile']
    newFile = FileContents(name=file.filename, data=file.read())

    print "{} is the file name".format(file.filename)
    filename = file.filename
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png"):
        print "File accepted."
        if FileContents.query.filter_by(name=filename).first():
            print "File exists."
        else:
            db.session.add(newFile)
            db.session.commit()
        return render_template('complete.html', image_name=filename)        
    else:
        return render_template("Error.html", message="File uploaded are not supported.")


@app.route('/upload/<filename>')
def send_image(filename):
    #return send_from_directory("images", filename)
    file_data = FileContents.query.filter_by(name=filename).first()
    print "data: ", BytesIO(file_data.data)
    return send_file(BytesIO(file_data.data), attachment_filename=filename, as_attachment=True)   

@app.route('/download')
def download():
    file_data = FileContents.query.filter_by(id=1).first()
    return send_file(BytesIO(file_data.data), attachment_filename='profile2.jpg', as_attachment=True)





if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug = True, host='0.0.0.0', port=5000)