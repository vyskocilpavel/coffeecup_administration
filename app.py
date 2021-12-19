import datetime

from flask import Flask, render_template, redirect, url_for, request, session, make_response, g, abort
from flask_oidc import OpenIDConnect
from flask_bootstrap import Bootstrap
from flask_weasyprint import HTML, render_pdf

from lib.forms.CoffeeRecordForms import CoffeeRecordDeleteForm
from lib.forms.MonthForms import MonthForm
from lib.tables.CoffeeRecordsTable import CoffeeRecordsTableObject, CoffeeRecordsTable
from lib.models.ServiceRecord import ServiceRecord
from lib.forms.ServiceRecordForms import ServiceRecordEditForm, ServiceRecordDetailForm, ServiceRecordCreateForm, \
    ServiceRecordDeleteForm
from lib.tables.OverViewOrgTable import OverViewOrgTable, OverViewOrgTableObject
from lib.tables.OverViewUserTable import OverViewUserTable, OverViewUserTableObject
from lib.tables.ServiceRecordsTable import ServiceRecordsTable, ServiceRecordsTableObject
from lib.forms.UserForms import UserDetailForm, UserEditForm
from lib.tables.UserRecordsTable import UserRecordsTable
from db import Db
from lib.tables.UserTable import UserTableObject, UserTable
from logging.config import dictConfig

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'DB_CONF_FILE': 'db_conf.yml'
})
oidc = OpenIDConnect(app)
db = Db()
db.init_db_tables()
db.get_table_list()
Bootstrap(app)


@app.route('/')
@oidc.require_login
def index():
    return redirect(url_for('auth_overview'))


@app.route('/login')
@oidc.require_login
def login():
    return redirect(url_for('auth_overview'))


@app.route('/auth/overview', methods=['GET', 'POST'])
@oidc.require_login
def auth_overview():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')

    month_form = MonthForm()
    if month_form.validate_on_submit():
        date = month_form.month.data
    elif 'date' in request.cookies.keys():
        date = datetime.datetime.strptime(request.cookies.get('date'), "%Y-%m")
        month_form.month.data = date
    else:
        date = datetime.datetime.now()
        month_form.month.data = date

    timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()

    results = db.get_month_overview(date)
    if month_form.export.data:
        html = render_template('auth/overview_export.html', results=results, month=date.month, year=date.year)
        return render_pdf(HTML(string=html))

    table_objects = []
    org_table_objects = []
    for id, user_record in results['user_stats'].items():
        table_objects.append(
            OverViewUserTableObject(user_record.id, user_record.name, user_record.organization, user_record.count))

    for org, count in results['org_stats'].items():
        org_table_objects.append(OverViewOrgTableObject(org, count))

    user_stats_table = OverViewUserTable(OverViewUserTableObject.get_sorted_by(table_objects, sort, reverse),
                                         sort_by=sort,
                                         sort_reverse=reverse)

    org_stats_table = OverViewOrgTable(org_table_objects)

    resp = make_response(
        render_template('auth/overview.html', total_count=results['total_count'], org_stats_table=org_stats_table,
                        user_stats_table=user_stats_table, month_form=month_form))
    resp.set_cookie('date', date.strftime("%Y-%m"))
    return resp


@app.route('/auth/users')
@oidc.require_login
def auth_users():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    users = db.get_all_users()

    table = UserTable(UserTableObject.get_sorted_by(sort, reverse),
                      sort_by=sort,
                      sort_reverse=reverse)
    return render_template('auth/user/users.html', users_table=table)


@app.route('/auth/user/<string:id>')
@oidc.require_login
def auth_user_detail(id):
    user = db.get_user_by_id(id)
    form = UserDetailForm()
    form.id.data = user.id
    form.name.data = user.name
    form.organization.data = user.organization
    form.chip_card.data = user.chip

    records = UserRecordsTable.convert_object_to_table_object(user.records)
    records.sort(key=lambda x: x.date, reverse=True)
    user_records_table = UserRecordsTable(records)

    return render_template('auth/user/user_detail.html', user=user, form=form, table=user_records_table)


@app.route('/auth/user/<string:id>/edit', methods=['GET', 'POST'])
@oidc.require_login
def auth_user_edit(id):
    user = db.get_user_by_id(id)
    form = UserEditForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.organization = form.organization.data
        db.edit_user(user)
        return redirect(url_for('auth_user_detail', id=id))
    else:
        form.id.data = user.id
        form.name.data = user.name
        form.organization.data = user.organization
        form.chip_card.data = user.chip

    return render_template('auth/user/user_edit.html', user=user, form=form)


@app.route('/auth/records', methods=['GET', 'POST'])
@oidc.require_login
def auth_records():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')

    month_form = MonthForm()
    if month_form.validate_on_submit():
        date = month_form.month.data
    elif 'date' in request.cookies.keys():
        date = datetime.datetime.strptime(request.cookies.get('date'), "%Y-%m")
        month_form.month.data = date
    else:
        date = datetime.datetime.now()
        month_form.month.data = date
    timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()
    records = db.get_coffee_records_for_month(date)

    if month_form.export.data:
        records.sort(key=lambda x: x.date)
        html = render_template('auth/coffee_records/coffee_records_export.html', records=records, month=date.month,
                               year=date.year)
        return render_pdf(HTML(string=html))

    table_objects = []
    for record in records:
        table_objects.append(CoffeeRecordsTableObject(record.id, record.date, record.user_name, record.user_id))

    table = CoffeeRecordsTable(CoffeeRecordsTableObject.get_sorted_by(table_objects, sort, reverse),
                               sort_by=sort,
                               sort_reverse=reverse)

    resp = make_response(render_template('auth/coffee_records/records.html', table=table, month_form=month_form))
    resp.set_cookie('date', date.strftime("%Y-%m"))
    return resp


@app.route('/auth/records/<string:id>/delete', methods=['GET', 'POST'])
@oidc.require_login
def auth_record_delete(id):
    record = db.get_coffee_record_by_id(id)
    form = CoffeeRecordDeleteForm()
    if form.validate_on_submit():
        db.delete_coffee_record(record.id)
        return redirect(url_for('auth_records'))
    else:
        form.id.data = record.id
        form.date.data = record.date
        form.user_name.data = record.user_name
    return render_template('auth/coffee_records/record_delete.html', record=record, form=form)


@app.route('/auth/service_records', methods=['GET', 'POST'])
@oidc.require_login
def auth_service_records():
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')

    month_form = MonthForm()
    if month_form.validate_on_submit():
        date = month_form.month.data
    elif 'date' in request.cookies.keys():
        date = datetime.datetime.strptime(request.cookies.get('date'), "%Y-%m")
        month_form.month.data = date
    else:
        date = datetime.datetime.now()
        month_form.month.data = date
    timestamp = datetime.datetime(date.year, date.month, 1, 0, 0).timestamp()
    records = db.get_service_records_for_month(date)

    if month_form.export.data:
        records = db.get_service_records_for_month(date)
        records.sort(key=lambda x: x.date)

        html = render_template('auth/service_records/service_records_export.html', records=records, month=date.month,
                               year=date.year)
        return render_pdf(HTML(string=html))

    table_objects = []
    for record in records:
        table_objects.append(ServiceRecordsTableObject(record.id, record.date, record.description))

    table = ServiceRecordsTable(ServiceRecordsTableObject.get_sorted_by(table_objects, sort, reverse),
                                sort_by=sort,
                                sort_reverse=reverse)
    resp = make_response(
        render_template('auth/service_records/service_records.html', table=table, month_form=month_form))
    resp.set_cookie('date', date.strftime("%Y-%m"))
    return resp


@app.route('/auth/service_record', methods=['GET', 'POST'])
@oidc.require_login
def auth_service_record_create():
    form = ServiceRecordCreateForm()
    if form.validate_on_submit():
        db.create_service_record(
            ServiceRecord(None, int(round(datetime.datetime.now().timestamp())), form.description.data,
                          form.extent.data, form.note.data))
        return redirect(url_for('auth_service_records'))
    return render_template('auth/service_records/service_record_create.html', form=form)


@app.route('/auth/service_record/<string:id>/', methods=['GET', 'POST'])
@oidc.require_login
def auth_service_record_detail(id):
    service_record = db.get_service_record_by_id(id)
    form = ServiceRecordDetailForm()
    form.date.data = service_record.date
    form.description.data = service_record.description
    form.extent.data = service_record.extent
    form.note.data = service_record.note
    return render_template('auth/service_records/service_record_detail.html', form=form, service_record_id=id)


@app.route('/auth/service_record/<string:id>/edit', methods=['GET', 'POST'])
@oidc.require_login
def auth_service_record_edit(id):
    service_record = db.get_service_record_by_id(id)
    form = ServiceRecordEditForm()
    if form.validate_on_submit():
        db.edit_service_record(service_record.id)
        return redirect(url_for('auth_service_records'))
    else:
        form.id.data = service_record.id
        form.date.data = service_record.date
        form.description.data = service_record.description
        form.extent.data = []
        form.note.data = service_record.note
    return render_template('auth/service_records/service_record_edit.html', form=form, service_record_id=id)


@app.route('/auth/service_record/<string:id>/delete', methods=['GET', 'POST'])
@oidc.require_login
def auth_service_record_delete(id):

    service_record = db.get_service_record_by_id(id)
    print(f"SERVICE_RECORD: {service_record.extent}")
    form = ServiceRecordDeleteForm()
    if form.validate_on_submit():
        db.delete_service_record(service_record.id)
        return redirect(url_for('auth_service_records'))
    else:
        form.id.data = service_record.id
        form.date.data = service_record.date
        form.description.data = service_record.description
        form.extent.data = service_record.extent
        form.note.data = service_record.note
    return render_template('auth/service_records/service_record_delete.html', form=form)


if __name__ == '__main__':
    app.run()
