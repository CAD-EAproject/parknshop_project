from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    TextAreaField, FloatField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets

class CategoriesForm(FlaskForm):
    cat = StringField(_l('Categories'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class SubCategoriesForm(FlaskForm):
    subcat = StringField(_l('Sub Categories'), validators=[DataRequired()])
    catid = SelectField(_l('Categories'), validators=[DataRequired()] ,coerce=int)
    submit = SubmitField(_l('Submit'))

class ProductBrandForm(FlaskForm):
    PoBrand = StringField(_l('Product Brand'), validators=[DataRequired()])
    url = StringField(_l('img url'))
    submit = SubmitField(_l('Submit'))

class ProductForm(FlaskForm):
    product = StringField(_l('Product'), validators=[DataRequired()])
    volumn = StringField(_l('Volumn'))
    price = StringField(_l('Price'), validators=[DataRequired()])
    pricedown = StringField(_l('PriceDown'))
    details = StringField(_l('Details'))
    origin = StringField(_l('Origin'))
    url = StringField(_l('img url'))
    catid = SelectField(_l('Categories'), validators=[DataRequired()] ,coerce=int)
    pdbid = SelectField(_l('Brand'), validators=[DataRequired()] ,coerce=int)
    submit = SubmitField(_l('Submit'))

class ProProductForm(FlaskForm):
    promotion = SelectField(_l('Promotion'), validators=[DataRequired()] ,coerce=int)
    submit = SubmitField(_l('Submit'))

class RatingForm(FlaskForm):
    rating1 = h5fields.IntegerField(_l('Good quality'), validators=[DataRequired()], widget=h5widgets.NumberInput(min=1, max=5))
    rating2 = h5fields.IntegerField(_l('Good value for money'), validators=[DataRequired()], widget=h5widgets.NumberInput(min=1, max=5))
    rating3 = h5fields.IntegerField(_l('Full nutrition details'), validators=[DataRequired()], widget=h5widgets.NumberInput(min=1, max=5))
    rating4 = h5fields.IntegerField(_l('Must-have item'), validators=[DataRequired()], widget=h5widgets.NumberInput(min=1, max=5))
    comment = TextAreaField(_l('Comment (option)'))
    submit = SubmitField(_l('Submit'))