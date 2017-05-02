from flask_wtf import Form
from wtforms import Form, BooleanField, StringField, PasswordField, HiddenField, validators
from wtforms.widgets import TextArea


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    about_me = StringField('Could you tell something about you?', widget=TextArea())


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Your Password')


class PostForm(Form):
    title = StringField('Title', [validators.Length(max=140)])
    body = StringField('Body', [validators.Length(max=200)], widget=TextArea())


class CommentForm(Form):
    text = StringField('Text', [validators.Length(max=200)], widget=TextArea())
    parent = HiddenField()
    post_id = HiddenField()

