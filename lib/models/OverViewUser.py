class OverViewUser:
    id = None
    name = None
    organization = None
    count = 0

    def __init__(self, id, name, organization, count):
        self.id = id
        self.name = name
        self.organization = organization
        self.count = count

