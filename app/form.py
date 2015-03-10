from flask.ext.wtf import Form
from wtforms import StringField, IntegerField
from wtforms import validators, SubmitField


class LoginForm(Form):
    """this class is used for use access to the web application"""
    name = StringField('username', [validators.Required()])
    email = StringField('email', [validators.email()])
    age = IntegerField('age', [validators.Required()])
    submit = SubmitField("Submit")
