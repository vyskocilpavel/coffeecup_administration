from flask import url_for
from flask_table import Table, Col, ButtonCol, LinkCol
from datetime import datetime


class UserRecordsTable(Table):
    def sort_url(self, col_id, reverse=False):
        pass

    html_attrs = {'class': 'table'}
    date = Col('Date')
    count = Col('count')

    @staticmethod
    def convert_object_to_table_object(objects):
        table_object_array = []
        table_dict = {}
        for item in objects:
            time = item
            date = datetime.fromtimestamp(time, tz=None).strftime('%Y-%m-%d')
            if table_dict.keys().__contains__(date):
                table_dict[date] = table_dict[date] + 1
            else:
                table_dict[date] = 1

        for date, count in table_dict.items():
            table_object_array.append(UserRecordsTableObject(date, count))

        return table_object_array


# Get some objects
class UserRecordsTableObject(object):
    def __init__(self, date, count):
        self.date = date
        self.count = count

