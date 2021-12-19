import calendar
import datetime

from rethinkdb import RethinkDB

import yaml

from lib.models.CoffeeRecord import CoffeeRecord
from lib.models.OverViewUser import OverViewUser
from lib.models.ServiceRecord import ServiceRecord
from lib.models.User import User
import logging


class Db:
    TABLE_USERS = 'users'
    TABLE_RECORDS = 'records'
    TABLE_SERVICE_RECORDS = 'service_records'

    r = RethinkDB()
    host = 'localhost'
    db_name = 'db'
    port = 28015
    connection = None

    def __init__(self):
        config_file = 'db_conf.yaml'
        with open(config_file, 'r') as stream:
            try:
                db_config = yaml.safe_load(stream)
                self.host = db_config['host']
                self.db_name = db_config['db_name']
                self.port = db_config['port']
                self.connection = self.r.connect(self.host, self.port)
            except yaml.YAMLError as exc:
                print(exc)

    def get_all_users(self):
        cursor = self.r.db(self.db_name).table(self.TABLE_USERS).run(self.connection)
        users = []
        for item in cursor:
            user = User(item['chip'], item['id'], item['name'], item['organization'])
            users.append(user)
        cursor.close()
        return users

    def get_coffee_records(self):
        coffee_records_list = []
        cursor = self.r.db(self.db_name).table(self.TABLE_RECORDS).eq_join("user_id", self.r.db(self.db_name).table(self.TABLE_USERS)).without({"right": {"id": True}}).zip().run(self.connection)
        for item in cursor:
            coffee_records_list.append(CoffeeRecord(item['id'], item['time'], item['name'], item['user_id']))
        cursor.close()
        return coffee_records_list

    def get_coffee_records_for_month(self, date):
        start_timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()
        last_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        last_timestamp = datetime.datetime(last_date.year, last_date.month, last_date.day, 0, 0).timestamp()

        coffee_records_list = []
        cursor = self.r.db(self.db_name).table(self.TABLE_RECORDS).between(
            start_timestamp, last_timestamp, index='time'
        ).eq_join("user_id", self.r.db(self.db_name).table(self.TABLE_USERS)).without({"right": {"id": True}}).zip().run(self.connection)
        for item in cursor:
            coffee_records_list.append(CoffeeRecord(item['id'], item['time'], item['name'], item['user_id']))
        cursor.close()
        return coffee_records_list

    def get_coffee_record_by_id(self, id):
        print(id)
        cursor = self.r.db(self.db_name).table(self.TABLE_RECORDS).filter({'id': id}).eq_join("user_id", self.r.db(self.db_name).table(self.TABLE_USERS)).without({"right": {"id": True}}).zip().run(self.connection)
        for item in cursor:
            print(item)
            continue
        cursor.close()
        record = CoffeeRecord(item['id'], item['time'], item['name'], item['user_id'])
        return record

    def delete_coffee_record(self, id):
        try:
            self.r.db(self.db_name).table(self.TABLE_RECORDS).get(id).delete().run(self.connection)
            return True
        except Exception:
            return False

    def get_user_by_id(self, id):
        item = self.r.db(self.db_name).table(self.TABLE_USERS).get(id).run(self.connection)
        user = User(item['chip'], item['id'], item['name'], item['organization'])
        return user

    def get_coffee_records_for_user(self, id):
        coffee_records_list = []
        cursor = self.r.db(self.db_name).table(self.TABLE_RECORDS).filter({'user_id': id}).run(self.connection)
        for item in cursor:
            coffee_records_list.append(item['time'])
        cursor.close()
        return coffee_records_list

    def edit_user(self, user):
        try:
            self.r.db(self.db_name).table(self.TABLE_USERS).get(user.id)\
                .update({'name': user.name, 'organization': user.organization}).run(self.connection)
            return True
        except Exception:
            return False

    def get_service_records(self):
        service_records_list = []
        cursor = self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).run(self.connection)
        for item in cursor:
            print(item)
            service_records_list.append(ServiceRecord(item['id'], item['date'], item['description'], item['extent'], item['note']))
        return service_records_list

    def get_service_records_for_month(self, date):
        start_timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()
        last_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        last_timestamp = datetime.datetime(last_date.year, last_date.month, last_date.day, 0, 0).timestamp()

        service_records_list = []
        cursor = self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).between(
            start_timestamp, last_timestamp, index='date'
        ).run(self.connection)
        for item in cursor:
            service_records_list.append(ServiceRecord(item['id'], item['date'], item['description'], item['extent'], item['note']))
        cursor.close()
        return service_records_list

    def get_month_overview(self, date):
        start_timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()
        last_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
        last_timestamp = datetime.datetime(last_date.year, last_date.month, last_date.day, 0, 0).timestamp()

        result = {}
        org_stats = {}
        user_stats = {}
        total_count = 0
        cursor = self.r.db(self.db_name).table(self.TABLE_RECORDS).between(
            start_timestamp, last_timestamp, index='time'
        ).eq_join("user_id", self.r.db(self.db_name).table(self.TABLE_USERS)).without({"right": {"id": True}}).zip().run(self.connection)
        for item in cursor:
            user_id = item['user_id']
            organization = item['organization']
            if user_id in user_stats.keys():
                user_stats[user_id].count = user_stats[user_id].count + 1
            else:
                user = OverViewUser(user_id, item['name'], item['organization'], 1)
                user_stats[user_id] = user

            if organization in org_stats.keys():
                org_stats[organization] += 1
            else:
                org_stats[organization] = 1

            total_count += 1
        cursor.close()

        result['org_stats'] = org_stats
        result['user_stats'] = user_stats
        result['total_count'] = total_count

        return result

    def get_service_record_by_id(self, id):
        print(id)
        cursor = self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).filter({'id': id}).run(self.connection)
        for item in cursor:
            print(item)
            continue
        cursor.close()

        record = ServiceRecord(item['id'], item['date'].timestamp(), item['description'], item['extent'], item['note'])
        return record

    def create_service_record(self, service_record):
        try:
            response = self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).insert({
                'date': service_record.date,
                'description': service_record.description,
                'extent': service_record.extent,
                'note': service_record.note
            }).run(self.connection)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def edit_service_record(self, service_record):
        try:
            self.r.db(self.db_name).table(self.TABLE_USERS).get(service_record.id).update({
                'date': service_record.date.strftime("%Y-%m-%d"),
                'description': service_record.description,
                'extent': service_record.extent,
                'note': service_record.note
                 }).run(self.connection)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def delete_service_record(self, id):
        try:
            self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).get(id).delete().run(self.connection)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def get_table_list(self):
        return self.r.db(self.db_name).table_list().run(self.connection)

    def init_db_tables(self):
        tables = self.get_table_list()
        for name in [self.TABLE_USERS, self.TABLE_RECORDS, self.TABLE_SERVICE_RECORDS]:
            if name not in tables:
                print(f"Missing {name}")
                self.create_db_table(name)
        self.create_db_indexes()

    def create_db_table(self, table_name):
        try:
            self.r.db(self.db_name).table_create(table_name).run(self.connection)
            logging.info(f"Table '{table_name}' created.")
            return True
        except Exception:
            return False

    def create_db_indexes(self):
        try:
            self.r.db(self.db_name).table(self.TABLE_SERVICE_RECORDS).index_create('date').run(self.connection)
        except Exception as e:
            logging.warning(e)
            return False