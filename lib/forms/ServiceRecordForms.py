from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, TextAreaField, SubmitField, DateField, HiddenField, widgets

EXTENT_CHOICES = [
    ('INNER_SYSTEM_CLEANING', 'Cleaning of internal systems with a tablet'),
    ('DECALCIFICATION', 'Decalcification'),
    ('MILK_SYSTEM_CLEANING', 'Milk system cleaning'),
    ('FILTER_EXCHANGE', 'Filter exchange'),
]


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ServiceRecordCreateForm(FlaskForm):
    description = StringField('Description')
    extent = MultiCheckboxField('Extent of service', choices=EXTENT_CHOICES,
                                render_kw={'style': 'height: fit-content; list-style: none;'})
    note = TextAreaField('Note')
    submit = SubmitField('Submit')


class ServiceRecordEditForm(FlaskForm):
    id = HiddenField('Id')
    date = DateField('Date')
    description = StringField('Description')
    extent = MultiCheckboxField('Extent of service', choices=EXTENT_CHOICES,
                                render_kw={'style': 'height: fit-content; list-style: none;'})
    note = TextAreaField('Note')
    submit = SubmitField('Submit')


class ServiceRecordDeleteForm(FlaskForm):
    id = HiddenField('Id')
    date = DateField('Date', render_kw={'disabled': True})
    description = StringField('Description', render_kw={'disabled': True})
    extent = MultiCheckboxField('Extent of service', choices=EXTENT_CHOICES,
                                render_kw={'disabled': True, 'style': 'height: fit-content; list-style: none;'})
    note = TextAreaField('Note', render_kw={'disabled': True})
    submit = SubmitField('Delete')


class ServiceRecordDetailForm(FlaskForm):
    id = HiddenField('Id')
    date = DateField('Date', render_kw={'disabled': True})
    description = StringField('Description', render_kw={'disabled': True})
    extent = MultiCheckboxField('Extent of service', choices=EXTENT_CHOICES,
                                render_kw={'disabled': True, 'style': 'height: fit-content; list-style: none;'})
    note = TextAreaField('Note', render_kw={'disabled': True})
