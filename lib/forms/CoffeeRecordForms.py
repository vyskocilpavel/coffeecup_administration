from flask_wtf import FlaskForm
from wtforms import HiddenField, DateField, StringField, SubmitField


class CoffeeRecordDeleteForm(FlaskForm):
    id = HiddenField('Id')
    date = DateField('Date', render_kw={'disabled': True})
    user_name = StringField('Name', render_kw={'disabled': True})
    submit = SubmitField('Delete', render_kw={'class': 'btn-primary'})
