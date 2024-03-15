import cpmdetail
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect

from myforms.nameform import NameForm
from cpmdetail import get_matches
import secrets

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
app.secret_key = secret_key

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

@app.route("/hello-world")
def hello():
    return "Hello World"

@app.route("/", methods=['GET','POST'])
def index():
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        game_tag = form.gametag.data
        tag_line = form.tagline.data
        matches = cpmdetail.get_matches(game_tag, tag_line)
        message = str(f"Found {len(matches)} games for {game_tag}#{tag_line}")
    return render_template('index.html', form=form, message=message)