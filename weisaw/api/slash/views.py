import spacy
import dateparser
import os
from datetime import datetime
from slackclient import SlackClient
from flask import Blueprint, Response, request, jsonify, session, send_file, current_app

from weisaw.api.extensions import db
from weisaw.base.models.employee_leave_model import EmployeeLeaveModel

blue_print_name = 'slash'
blue_print_prefix = '/slash'

Model = db.Model

slash_blueprint = Blueprint(blue_print_name, __name__, url_prefix=blue_print_prefix)


@slash_blueprint.before_request
def perform_before_request_tasks():
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    # is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

    if not is_token_valid:
        return jsonify(
            {
                "response_type": "ephemeral",
                "text": "Invalid verification token supplied :O",
            }
        ), 401


@slash_blueprint.route('/ooo', methods=["POST"])
def slack_out_of_office(op_type="ooo"):
    """
    Out of Office: Mark users as Out of Office, with period, email, type (ooo), user name and the raw command
    :param op_type: ooo/wfh
    :return:
    """
    user_id = request.form['user_id']
    channel_id = request.form['channel_id']
    team_id = request.form['team_id']
    enterprise_id = request.form['enterprise_id']
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
        current_app.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}'
                                .format("example@abc.in", str(start_date), str(end_date), str(days_count), op_type,
                                        raw_text, user_name))

        user_email, user_full_name, user_avatar = get_slack_user_info(user_id)

        if user_email is not None:

            emp_leave = EmployeeLeaveModel(
                emailAddress="abc@example.com",
                startDate=start_date,
                endDate=end_date,
                daysCount=days_count,
                leaveType=op_type,
                rawComment=raw_text,
                slackUsername=user_name,
                slackUserId=user_id,
                slackChannelId=channel_id,
                slackTeamId=team_id,
                slackEnterpriseId=enterprise_id,
                slackFullName=user_full_name,
                slackAvatarUrl=user_avatar,
                createdAt=datetime.now(),
            )

            # insert_employee_leave(emp_leave)

            response_msg = "Got it {0}...Safe travel!".format(user_name)

            return jsonify(
                {
                    "response_type": "ephemeral",
                    "text": response_msg,
                }
            ), 200

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


def insert_employee_leave(emp_leave_info):
    db.session.add(emp_leave_info)
    db.session.commit()


def get_slack_user_info(user_id):

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    slack_user_info = sc.api_call("users.info", user='user_id')

    if slack_user_info is not None and slack_user_info.get("ok") and slack_user_info.get("user") is not None:
        if slack_user_info.get("user").get("profile") is not None:
            slack_user_profile = slack_user_info.get("user").get("profile")
            user_email = slack_user_profile.get("email")
            full_name = slack_user_profile.get("real_name")
            avatar = slack_user_profile.get("image_512")

            return user_email, full_name, avatar
    return None, None, None
