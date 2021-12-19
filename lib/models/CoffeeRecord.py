from datetime import datetime


class CoffeeRecord:
    id = None
    date = None
    user_name = None
    user_id = None

    def __init__(self, id, date, user_name, user_id):
        self.id = id
        self.date = datetime.fromtimestamp(date, tz=None)
        self.user_name = user_name
        self.user_id = user_id

