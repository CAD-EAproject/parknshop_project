from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('about me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))


    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class PromotionForm(FlaskForm):
    name = StringField(_l('What\'s promotion'), validators=[DataRequired()])
    url = StringField(_l('Photo url'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class FeatureForm(FlaskForm):
    title = TextAreaField(_l('What\'s feature?'), validators=[DataRequired()])
    url = StringField(_l('url'), validators=[DataRequired()])
    description = TextAreaField(_l('description'))
    submit = SubmitField(_l('Submit'))

class BannerForm(FlaskForm):
    banner = StringField(_l('Banner url'))
    submit = SubmitField(_l('Submit'))
