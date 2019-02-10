import spacy
import dateparser
import psycopg2
import requests
import os
from flask import Blueprint, Response, request, jsonify, session, send_file, abort

blue_print_name = 'slash'
blue_print_prefix = '/slash'

slash_blueprint = Blueprint(blue_print_name, __name__, url_prefix=blue_print_prefix)


@slash_blueprint.before_request
def perform_before_request_tasks():
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    # is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

    if not is_token_valid:
        abort(404)


@slash_blueprint.route('/ooo', methods=["POST"])
def slack_out_of_office(type="ooo"):
    """
    Out of Office: Mark users as Out of Office, with period, email, type (ooo), user name and the raw command
    :param type:
    :return:
    """
    user_id = request.form['user_id']
    user_name = request.form['user_name']
    response_url = request.form['response_url']
    raw_text = request.form['text']

    nlp = spacy.load('en_core_web_sm')
    cmd_doc = nlp(raw_text)

    date_list = []
    start_date, end_date = None, None
    days_count = 0

    for ent in cmd_doc.ents:
        if ent.label_ == "DATE" or ent.label_ == "TIME":
            date_list.append(dateparser.parse(ent.text, languages=['en']))

    if date_list is not None and len(date_list) > 0:
        date_list.sort(reverse=True)

        if len(date_list) == 2:

            end_date = date_list[0]
            start_date = date_list[1]
            delta_leave = end_date - start_date
            days_count = delta_leave.days + 1

        elif len(date_list) == 1:
            end_date = date_list[0]
            start_date = date_list[0]
            days_count = 1

    if start_date is not None and end_date is not None and days_count > 0:
        # user_email = get_slack_user_email(user_id)
        insert_leave("Empty", start_date, end_date, days_count, type, raw_text, user_name)

        response_msg = "Got it {0}...Safe travel!".format(user_name)

        return jsonify(
            {
                "response_type": "ephemeral",
                "text": response_msg,
            }
        ), 200
    else:
        return jsonify(
            {
                "response_type": "ephemeral",
                "text": "Oops! Something went wrong... :/",
            }
        ), 200


@slash_blueprint.route('/wfh', methods=["POST"])
def slack_work_from_home():
    """
    Working from home: Mark users as working from home with period, type (wfh), email, user name and raw command
    :return:
    """
    return slack_out_of_office("wfh")


@slash_blueprint.route('/list', methods=["POST"])
def slack_list_leaves():
    """
    Show all the ooo or wfh listings of the requesting user
    :return:
    """
    return slack_out_of_office("wfh")


@slash_blueprint.route('/upcoming', methods=["POST"])
def slack_upcoming_leaves():
    """
    Show all the ooo or wfh of all the users for the requested day
    :return:
    """
    return slack_out_of_office("wfh")


def insert_leave(email_address, start_date, end_date, days_count, leave_type, raw_comment, slack_username):

    insert_leave_sql = """INSERT INTO employee_leave
            (email_address, start_date, end_date, days_count, leave_type, raw_comment, slack_username) 
            VALUES(%s, %s, %s, %s, %s, %s, %s);"""
    conn = None

    try:

        conn = psycopg2.connect(os.environ["RS_URI"])
        cur = conn.cursor()
        cur.execute(insert_leave_sql, (email_address, start_date, end_date, days_count, leave_type, raw_comment, slack_username))
        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_slack_user_email(userid):

    headers = {'content-type': 'x-www-form-urlencoded'}
    data = [
        ('token', os.environ["SLACK_ACCESS_TOKEN"]),
        ('user', userid)
    ]

    slack_user_info = requests.get("https://slack.com/api/users.info", data=data, headers=headers)

    if slack_user_info.ok:
        user_info_json = slack_user_info.json()
        if user_info_json is not None and user_info_json.get("ok") and user_info_json.get("user") is not None:
            if user_info_json.get("user").get("profile") is not None:
                user_email = user_info_json.get("user").get("profile").get("email")
                return user_email
    return None

