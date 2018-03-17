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
    username = StringField('Никнейм', validators=[DataRequired(),
        Unique(
            User,
            User.username,
            message='Уже существует профиль стаким никнейом.')]
    )
class ExtendedRegisterForm(RegisterForm):
    username = StringField('Никнейм', validators=[DataRequired(),
        Unique(
            User,
            User.username,
            message='Уже существует профиль стаким никнейом.')]
    )



class UserEditForm(FlaskForm):
    class Meta:
        model = User

    username = StringField('Никнейм', validators = [Length(min=4, max=25), Unique] )
    about_me = StringField('О себе', widget=TextArea(), validators = [Length(min = 0, max = 1000)])
    file = FileField('Изображение', validators=[
        FileAllowed(images, 'Только картинки!')
    ])



class PostForm(FlaskForm):
    title = StringField('Заголовок', [validators.Length(min = 1,max=200)])
    body = StringField('Текст', [validators.Length(min = 5, max=1000)], widget=TextArea())
    file = FileField('Фото',  validators=[
        FileAllowed(images, 'Images only!')
    ])




class CommentForm(FlaskForm):
    text = StringField('text', [validators.Length(min=1, max=800)], widget=TextArea())
    file = FileField('фото', validators=[
        FileAllowed(images, 'Только картинки!')
    ])




class ProductCommentForm(FlaskForm):
    text = StringField('Text', [validators.Length(min = 1, max=800)], widget=TextArea())
    parent = HiddenField()
    product_id = HiddenField()
    file = FileField('image', validators=[
        FileAllowed(images, 'Только картинки!')
    ])



class ProductForm(FlaskForm):
    title = StringField('Название', [validators.Length(min =1, max=200)])
    price = StringField('Цена', [validators.Length(min=1, max=200)])
    images = FileField('Фото', validators=[
        FileAllowed(images, 'Только картинки!')
    ])
    description = StringField('Описание', [validators.Length(min = 5, max=1500)], widget=TextArea())

