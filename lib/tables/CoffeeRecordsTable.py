from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol

import db


class CoffeeRecordsTable(Table):
    html_attrs = {'class': 'table'}
    id = Col('Id', show=False)
    date = Col('Date')
    user_name = Col('User name')
    user_id = Col('User Id', show=False)
    remove = LinkCol('Delete record', 'auth_record_delete', url_kwargs=dict(id='id'))
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('auth_records', sort=col_key, direction=direction)


# Get some objects
class CoffeeRecordsTableObject(object):
    def __init__(self, id, date, user_name, user_id):
        self.id = id
        self.date = date
        self.user_name = user_name
        self.user_id = user_id

    @classmethod
    def get_sorted_by(cls, records, sort, reverse=False):
        return sorted(
            records,
            key=lambda x: getattr(x, sort),
            reverse=reverse)
