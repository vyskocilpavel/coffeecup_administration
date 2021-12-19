from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol

import db


class UserTable(Table):
    html_attrs = {'class': 'table'}
    name = Col('Name')
    organization = Col('Organization')
    chip = Col('Chip card number')
    id = Col('Id', show=False)
    detail = LinkCol('Detail', 'auth_user_detail', url_kwargs=dict(id='id'))
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('auth_users', sort=col_key, direction=direction)


class UserTableObject(object):
    def __init__(self, id, name, organization, chip):
        self.id = id
        self.name = name
        self.organization = organization
        self.chip = chip

    @classmethod
    def get_elements(cls):
        users = db.Db().get_all_users()
        users_objects = []
        for user in users:
            users_objects.append(UserTableObject(user.id, user.name, user.organization, user.chip))
        return users_objects

    @classmethod
    def get_sorted_by(cls, sort, reverse=False):
        return sorted(
            cls.get_elements(),
            key=lambda x: getattr(x, sort),
            reverse=reverse)

    @classmethod
    def get_element_by_id(cls, id):
        return [i for i in cls.get_elements() if i.id == id][0]
