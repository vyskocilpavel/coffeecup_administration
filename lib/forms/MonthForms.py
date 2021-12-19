from datetime import date

from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, MonthField
from wtforms.validators import ValidationError, DataRequired


class MonthForm(FlaskForm):
    month = MonthField('Month', format='%Y-%m', default=date.today, validators=[])
    submit = SubmitField('Filter selected')
    export = SubmitField('Export selected')
