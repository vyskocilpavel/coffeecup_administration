from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol


class OverViewOrgTable(Table):
    html_attrs = {'class': 'table'}
    organization = Col('Organization')
    count = Col('Count')

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('auth_overview', sort=col_key, direction=direction)


# Get some objects
class OverViewOrgTableObject(object):
    def __init__(self, organization, count):
        self.id = id
        self.organization = organization
        self.count = count

    @classmethod
    def get_sorted_by(cls, records, sort, reverse=False):
        return sorted(
            records,
            key=lambda x: getattr(x, sort),
            reverse=reverse)
