from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class WebStoreForm(FlaskForm):
    web_store_url = StringField('What is the sticker URL?', validators=[DataRequired()])
    submit = SubmitField('Download')
