from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    TextAreaField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l

class StoreForm(FlaskForm):
    store = StringField(_l('Store'), validators=[DataRequired()])
    address = TextAreaField(_l('Address?'))
    district = SelectField(_l('District'), validators=[DataRequired()], coerce=int)
    cobrand = SelectField(_l('Brand'), validators=[DataRequired()], coerce=int)
    tel = StringField(_l('Tel no.'))
    submit = SubmitField(_l('Submit'))

class RegionForm(FlaskForm):
    region = StringField(_l('Region'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class DistrictForm(FlaskForm):
    district = StringField(_l('District'), validators=[DataRequired()])
    region = SelectField(_l('Region'), validators=[DataRequired()] ,coerce=int)
    submit = SubmitField(_l('Submit'))

class CompanyBrandForm(FlaskForm):
    brand = StringField(_l('Company Brand'), validators=[DataRequired()])
    image = StringField(_l('image url'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
