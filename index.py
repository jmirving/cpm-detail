import cpmdetail
import secrets
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect

from errors.not_found_error import NotFoundError
from myforms.nameform import NameForm


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


@app.route("/", methods=['GET'])
def index():
    form = NameForm()
    message = ""
    return render_template('index.html', form=form, message=message)


@app.route("/", methods=['POST'])
def index_post():
    form = NameForm()
    if form.validate_on_submit():
        game_tag = form.gametag.data
        tag_line = form.tagline.data
        try:
            detailed_matches_dict = cpmdetail.get_matches_from_user_input(game_tag, tag_line)
            message = str(f"Matches for: {game_tag}#{tag_line}")
            puuid = next(iter(detailed_matches_dict))
            detailed_matches = detailed_matches_dict.get(puuid)
            return render_template('matches.html', form=form, message=message, matches_length=len(detailed_matches), detailed_matches_dict=detailed_matches, puuid=puuid)
        except NotFoundError as ex:
            return render_template('index.html', form=form, message=ex.message)
    return render_template('index.html', form=form, message="Invalid Form")


@app.route("/<puuid>/<participant_id>/match/<match_id>")
def match(puuid, participant_id, match_id):
    message = str(f"CSM for {match_id}")
    csm_detail = cpmdetail.get_cs_per_frame(participant_id, match_id)
    print(str(f"Getting {match_id} match for {puuid}:{participant_id}"))
    return render_template('match-detail.html', message=message, csm_detail=csm_detail)


if __name__ == "__main__":
    app.run(debug=True)
