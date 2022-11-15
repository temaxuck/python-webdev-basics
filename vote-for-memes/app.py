from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from uuid import uuid4


app = Flask(__name__)
allowed_filetypes = ["image/png", "image/gif", "image/jpeg", "image/pjpeg"]

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    image_filename = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.Integer, default=0)
    
@app.route("/", methods=["GET"])
def home():
    meme = Meme.query.first()
    return render_template("home.html", meme=meme)


@app.route("/meme/upload", methods=["GET", "POST"])
def upload_meme():
    if request.method == "POST":
        username = request.form.get('username')
        file = request.files['upload-meme']
        filename = secure_filename(f"{uuid4()}.{file.filename.split('.', 1)[1].lower()}")
        
        if file.mimetype in allowed_filetypes:
            file.save(f"static/pics/{filename}")
        else:
            return url_for(home)

        new_meme = Meme(author=username, image_filename=filename)
        db.session.add(new_meme)
        db.session.commit()

    return render_template("upload_meme.html")


if __name__ == '__main__':
    app.run("localhost", 5000, debug=True)

with app.app_context():
    db.create_all()

