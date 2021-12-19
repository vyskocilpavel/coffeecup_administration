from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol


class OverViewUserTable(Table):
    html_attrs = {'class': 'table'}
    id = Col('Id', show=False)
    user_name = Col('User name')
    organization = Col('Organization')
    count = Col('Count')
    user_detail = LinkCol('User detail', 'auth_user_detail', url_kwargs=dict(id='id'))
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('auth_overview', sort=col_key, direction=direction)


# Get some objects
class OverViewUserTableObject(object):
    def __init__(self, id, user_name, organization, count):
        self.id = id
        self.user_name = user_name
        self.organization = organization
        self.count = count

    @classmethod
    def get_sorted_by(cls, records, sort, reverse=False):
        return sorted(
            records,
            key=lambda x: getattr(x, sort),
            reverse=reverse)
