from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField


class InputForm(FlaskForm):
    movie = StringField('Text')
    movieTitle = StringField('movie')
    submit = SubmitField('Submit')


