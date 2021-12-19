from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, validators, SubmitField


class UserDetailForm(FlaskForm):
    id = HiddenField('Id')
    name = StringField('Name', render_kw={'disabled': True})
    organization = StringField('Organization', render_kw={'disabled': True})
    chip_card = StringField('Chip card number', render_kw={'disabled': True})


class UserEditForm(FlaskForm):
    id = HiddenField('Id')
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=4)])
    organization = StringField('Organization', [validators.Length(min=4)])
    chip_card = StringField('Chip card number', render_kw={'disabled': True})
    submit = SubmitField('Submit')
