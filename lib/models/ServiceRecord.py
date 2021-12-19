from datetime import datetime

ACTIONS = {
    'INNER_SYSTEM_CLEANING': 'Cleaning of internal systems with a tablet',
    'DECALCIFICATION': 'Decalcification',
    'MILK_SYSTEM_CLEANING': 'Milk system cleaning',
    'FILTER_EXCHANGE': 'Filter exchange'
}

class ServiceRecord:
    id = None
    date = None
    description = None
    extent = []
    note = None

    def __init__(self, id, date, description, extent, note):
        self.id = id
        self.date = date
        self.description = description
        self.extent = extent
        self.note = note

    def get_date(self):
        return datetime.fromtimestamp(self.date)

    def get_extent_translations(self):
        result = []
        for item in self.extent:
            result.append(ACTIONS[item])

        return result
