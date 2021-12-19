import datetime

from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol, DateCol

import db


class ServiceRecordsTable(Table):
    html_attrs = {'class': 'table'}
    id = Col('Id', show=False)
    date = DateCol('Date')
    description = Col('Description')
    detail = LinkCol('Detail', 'auth_service_record_detail', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'auth_service_record_delete', url_kwargs=dict(id='id'))
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('auth_service_records', sort=col_key, direction=direction)


# Get some objects
class ServiceRecordsTableObject(object):
    def __init__(self, id, date, description):
        self.id = id
        self.date = datetime.datetime.fromtimestamp(date)
        self.description = description
        # self.extent = extent
        # self.note = note

    @classmethod
    def get_sorted_by(cls, records, sort, reverse=False):
        return sorted(
            records,
            key=lambda x: getattr(x, sort),
            reverse=reverse)
