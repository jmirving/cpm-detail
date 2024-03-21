import cpmdetail
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect

from myforms.nameform import NameForm
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


@app.route("/", methods=['GET', 'POST'])
def index():
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        game_tag = form.gametag.data
        tag_line = form.tagline.data
        puuid = cpmdetail.get_puuid(game_tag, tag_line)
        if "status" in puuid:
            message = puuid["status"]["message"]
            print(message)
            return render_template('index.html', form=form, message=message)

        matches = cpmdetail.get_matches(puuid)
        matches_length = len(matches)
        if matches_length > 0:
            message = str(f"Matches for: {game_tag}#{tag_line}")
            print(message)
            return render_template('matches.html', form=form, message=message, matches_length=matches_length,
                                   matches=matches, puuid=puuid)
        else:
            message = str(f"{game_tag}#{tag_line} found but no recent matches. Check for typos and try again")
            print(message)
            return render_template('index.html', form=form, message=message)

    return render_template('index.html', form=form, message=message)


@app.route("/<puuid>/match/<id>")
def match(puuid, id):
    message = str(f"You clicked the match id: {id}")
    participant_id = cpmdetail.get_participant(id, puuid)
    frames = cpmdetail.get_match_timeline(id)
    csm_detail = cpmdetail.get_cs_per_frame(participant_id, frames)
    print(str(f"Getting {id} match for {puuid}:{participant_id}"))
    return render_template('match-detail.html', message=message, csm_detail=csm_detail, frame_length=len(frames))

if __name__ == "__main__":
    app.run(debug=True)
