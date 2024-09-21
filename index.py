import cpmdetail
import secrets
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect

from cpmdetail import get_comparison
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
            return render_template('matches.html', form=form, message=message, matches_length=len(detailed_matches_dict), detailed_matches_dict=detailed_matches_dict)
        except NotFoundError as ex:
            return render_template('index.html', form=form, message=ex.message)
    return render_template('index.html', form=form, message="Invalid Form")


@app.route("/<puuid>/<participant_id>/match/<match_id>/<champ_name>")
def match(puuid, participant_id, match_id, champ_name):
    message = str(f"CPM for a {champ_name} game")
    csm_detail = cpmdetail.get_cs_per_frame(participant_id, match_id)
    print(str(f"Getting {match_id} match for {puuid}:{participant_id}"))
    return render_template('match-detail.html', message=message, csm_detail=csm_detail, puuid=puuid, participant_id=participant_id, match_id=match_id, champ_name=champ_name)

@app.route("/<puuid>/<participant_id>/match/<match_id>/<champ_name>/compare")
def compare(puuid, participant_id, match_id, champ_name):

    # average data or some other compare if more than one, then return data
    compare_detail = get_comparison(participant_id, match_id, champ_name)

    # fill in Subtitle via message
    message = str(f"Comparing your game on {champ_name} to Experts")
    # return page
    return render_template('match-compare.html', message=message, compare_detail=compare_detail)

if __name__ == "__main__":
    app.run(debug=True)
