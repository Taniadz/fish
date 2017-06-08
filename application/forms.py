from flask_wtf import Form
from wtforms import BooleanField, StringField, PasswordField, HiddenField,  TextAreaField, validators
from wtforms.widgets import TextArea
from wtforms.validators import Required, Length
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired

images = UploadSet('images', IMAGES)


class UserEditForm(Form):
    username = StringField('username')
    about_me = StringField('about_me', widget=TextArea(), validators = [Length(min = 0, max = 140)])
    file = FileField('image')


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
    text = StringField('text', [validators.Length(max=200)], widget=TextArea())
    parent = HiddenField()
    post_id = HiddenField()


class ProductCommentForm(Form):
    text = StringField('Text', [validators.Length(max=200)], widget=TextArea())
    parent = HiddenField()
    product_id = HiddenField()



class ProductForm(Form):
    title = StringField('Title', [validators.Length(max=140)])
    file = FileField('image')
    description = StringField('Description', [validators.Length(max=200)], widget=TextArea())