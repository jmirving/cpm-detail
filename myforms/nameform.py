from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
    gametag = StringField('Enter username as visible in game', validators=[DataRequired(), Length(3, 16)])
    tagline = StringField('Enter tag line without the leading #. This is the #value under your game name if you hover your profile picture', validators=[DataRequired(), Length(3, 5)])
    submit = SubmitField('Submit')