import db


class User:
    chip = None
    id = None
    name = None
    organization = None
    records = []

    def __init__(self, chip, id, name, organization):
        self.chip = chip
        self.id = id
        self.name = name
        self.organization = organization
        self.records = db.Db().get_coffee_records_for_user(id)

