from flask_wtf import FlaskForm

from wtforms import StringField, HiddenField, validators, FieldList, FormField
from wtforms.widgets import TextArea
from wtforms.validators import Required, Length, DataRequired, Optional
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
            message='Уже существует профиль с этим никнейом.')]
    )
class ExtendedRegisterForm(RegisterForm):
    username = StringField('Никнейм', validators=[DataRequired(),
        Unique(
            User,
            User.username,
            message='Уже существует профиль с этим никнейом.')]
    )



class UserEditForm(FlaskForm):
    class Meta:
        model = User

    username = StringField('Никнейм', validators = [Length(min=4, max=25), Unique] )
    about_me = StringField('О себе', widget=TextArea(), validators = [Length(min = 0, max = 1000)])
    file = FileField('Изображение', validators=[
        FileAllowed(images, 'Только картинки!')
    ])

class TagsForm(FlaskForm):
    name = StringField('Тег', widget=TextArea())

class PostForm(FlaskForm):
    title = StringField('Заголовок', [validators.Length(min = 1,max=300, message="Длина заголовка должна быть от 1 до 300 символов")])
    body = StringField('Текст', [validators.Length(min = 5, max=2500, message="Длина текста должна быть от 5 до 2500 символов")], widget=TextArea())
    file = FileField('Фото',  validators=[
        FileAllowed(images, 'Только картинки!')
    ])
    tags = FieldList(FormField(TagsForm), min_entries=3, validators = [Optional()])


class EditPostForm(FlaskForm):
    title = StringField('Заголовок', [validators.Length(min = 1,max=300, message="Длина заголовка должна быть от 1 до 300 символов")])
    body = StringField('Текст', [validators.Length(min = 5, max=2500, message="Длина текста должна быть от 5 до 2500 символов")], widget=TextArea())
    file = FileField('Фото',  validators=[
        FileAllowed(images, 'Только картинки!')
    ])








class CommentForm(FlaskForm):
    text = StringField('text', [validators.Length(min=1, max=1000,  message="Длина комментария должна быть от одного до 1000 символов")], widget=TextArea())
    file = FileField('фото', validators=[
        FileAllowed(images, 'Только картинки!')
    ])




class ProductCommentForm(FlaskForm):
    text = StringField('Text', [validators.Length(min = 1, max=1000, message="Длина комментария должна быть от 1 до 1000 символов")], widget=TextArea())
    parent = HiddenField()
    product_id = HiddenField()
    file = FileField('image', validators=[
        FileAllowed(images, 'Только картинки!')
    ])



class ProductForm(FlaskForm):
    title = StringField('Название*', [validators.Length(min =1, max=300, message="Длина названия должна быть от 1 до 1000 символов")])
    price = StringField('Цена', [validators.Length(min=1, max=200)])
    images = FileField('Фото', validators=[
        FileAllowed(images, 'Только картинки!')
    ])
    description = StringField('Описание*', [validators.Length(min = 5, max=1500, message="Длина описания должна быть от 5 до 1500 символов")], widget=TextArea())




class SearchForm(FlaskForm):
    search = StringField('search', validators = [DataRequired()])