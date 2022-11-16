from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from uuid import uuid4

import random

# app settings
app = Flask(__name__)
allowed_filetypes = ["image/png", "image/gif", "image/jpeg", "image/pjpeg"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

# extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# models
class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    image_filename = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.Integer, default=0)
    
# routes
@app.route("/", methods=["GET"])
def home():
    # arg = request.args
    
    if meme_id := request.args.get('meme_id'):
        meme = Meme.query.filter_by(id=meme_id).first()
        if not meme:
            meme = get_random_meme()
    else:
        meme = get_random_meme()
    
    next_meme_id = meme.id + 1
    if Meme.query.filter_by(id=next_meme_id).count() == 0:
        next_meme_id = 1
    
    prev_meme_id = meme.id - 1
    if Meme.query.filter_by(id=prev_meme_id).count() == 0:
        prev_meme_id = len(Meme.query.all())
    
    return render_template("home.html", meme=meme, next_meme_id=next_meme_id, prev_meme_id=prev_meme_id, best_memes=get_best_memes())

@app.route("/meme/<meme_id>/upvote", methods=["GET"])
def upvote(meme_id: int):
    meme = db.get_or_404(Meme, meme_id)
    meme.rating += 1
    db.session.commit()
    return redirect(url_for('home', meme_id=meme_id))

@app.route("/meme/<meme_id>/downvote", methods=["GET"])
def downvote(meme_id: int):
    meme = db.get_or_404(Meme, meme_id)
    meme.rating -= 1
    db.session.commit()
    return redirect(url_for('home', meme_id=meme_id))

@app.route("/meme/upload", methods=["GET", "POST"])
def upload_meme():
    if request.method == "POST":
        username = request.form.get('username')
        file = request.files['upload-meme']
        filename = secure_filename(f"{uuid4()}.{file.filename.split('.', 1)[1].lower()}")
        
        if file.mimetype in allowed_filetypes:
            file.save(f"static/pics/{filename}")
        else:
            return redirect(url_for('home'))

        new_meme = Meme(author=username, image_filename=filename)
        db.session.add(new_meme)
        db.session.commit()
        return redirect(url_for('home', meme_id=new_meme.id))

    return render_template("upload_meme.html", best_memes=get_best_memes())

# utils
def get_best_memes():
    return Meme.query.order_by(Meme.rating.desc()).limit(5).all()

def get_random_meme():
    return random.choice(Meme.query.all())

# run app
if __name__ == '__main__':
    app.run("localhost", 5000, debug=True)

with app.app_context():
    db.create_all()

