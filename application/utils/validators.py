
from wtforms.validators import ValidationError


class Unique(object):
    def __init__(self, model, field, message='This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class ImageOnly(object):
    def __init__(self,  message='Has to be an image.'):
        self.message = message

    def __call__(self, form, field):
        if not '.' in field.data or not field.data.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
            raise ValidationError(self.message)



