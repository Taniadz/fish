from flask_wtf import FlaskForm

from wtforms import BooleanField, StringField, PasswordField, HiddenField,  TextAreaField, validators
from wtforms.widgets import TextArea
from wtforms.validators import Required, Length, DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_security.forms import RegisterForm, ConfirmRegisterForm
from .models import User
from .utils.validators import Unique
from wtforms.validators import ValidationError
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

from application import images


class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    username = StringField('First Name', validators=[DataRequired(),
        Unique(
            User,
            User.username,
            message='There is already an account with that username.')]
    )
class ExtendedRegisterForm(RegisterForm):
    username = StringField('First Name', validators=[DataRequired(),
        Unique(
            User,
            User.username,
            message='There is already an account with that username.')]
    )



class UserEditForm(FlaskForm):
    class Meta:
        model = User

    username = StringField('username', validators = [Length(min=4, max=25), Unique] )
    about_me = StringField('about_me', widget=TextArea(), validators = [Length(min = 0, max = 1000)])
    file = FileField('image', validators=[
        FileAllowed(images, 'Images only!')
    ])



class PostForm(FlaskForm):
    title = StringField('Title', [validators.Length(min = 1,max=200)])
    body = StringField('Body', [validators.Length(min = 5, max=1000)], widget=TextArea())
    file = FileField('image',  validators=[
        FileAllowed(images, 'Images only!')
    ])




class CommentForm(FlaskForm):
    text = StringField('text', [validators.Length(min=1, max=800)], widget=TextArea())
    file = FileField('image', validators=[
        FileAllowed(images, 'Images only!')
    ])




class ProductCommentForm(FlaskForm):
    text = StringField('Text', [validators.Length(min = 1, max=800)], widget=TextArea())
    parent = HiddenField()
    product_id = HiddenField()
    file = FileField('image', validators=[
        FileAllowed(images, 'Images only!')
    ])



class ProductForm(FlaskForm):
    title = StringField('Title', [validators.Length(min =1, max=200)])
    price = StringField('Price', [validators.Length(min=1, max=200)])
    images = FileField('images', validators=[
        FileAllowed(images, 'Images only!')
    ])
    description = StringField('Description', [validators.Length(min = 5, max=1500)], widget=TextArea())

