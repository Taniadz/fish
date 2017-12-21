from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, HiddenField,  TextAreaField, validators
from wtforms.widgets import TextArea
from wtforms.validators import Required, Length
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_security.forms import RegisterForm



images = UploadSet('images', IMAGES)


class ExtendedRegisterForm(RegisterForm):
    username = StringField('First Name', [validators.Required()])




class UserEditForm(FlaskForm):
    username = StringField('username', [validators.Length(min=4, max=25)] )
    about_me = StringField('about_me', widget=TextArea(), validators = [Length(min = 0, max = 1000)])
    file = FileField('image')



class PostForm(FlaskForm):
    title = StringField('Title', [validators.Length(min = 1,max=200)])
    body = StringField('Body', [validators.Length(min = 5, max=1000)], widget=TextArea())
    file = FileField('image')



class CommentForm(FlaskForm):
    text = StringField('text', [validators.Length(min=1, max=800)], widget=TextArea())
    file = FileField('image')




class ProductCommentForm(FlaskForm):
    text = StringField('Text', [validators.Length(min = 1, max=800)], widget=TextArea())
    parent = HiddenField()
    product_id = HiddenField()



class ProductForm(FlaskForm):
    title = StringField('Title', [validators.Length(min =1, max=200)])
    price = StringField('Price', [validators.Length(min=1, max=200)])
    images = FileField('images')
    description = StringField('Description', [validators.Length(min = 5, max=1500)], widget=TextArea())

