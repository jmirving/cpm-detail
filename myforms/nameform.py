from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
    gametag = StringField('Enter username', validators=[DataRequired(), Length(3, 16)])
    tagline = StringField('Enter tagline', validators=[DataRequired(), Length(3, 5)])
    submit = SubmitField('Submit')