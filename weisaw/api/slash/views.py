import spacy
import dateparser
import os
from datetime import datetime, date
from slackclient import SlackClient
from flask import Blueprint, Response, request, jsonify, session, send_file, current_app, g

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_

from weisaw.api.extensions import db
from weisaw.base.models.employee_leave_model import EmployeeLeaveModel

blue_print_name = 'slash'
blue_print_prefix = '/slash'

Model = db.Model

slash_blueprint = Blueprint(blue_print_name, __name__, url_prefix=blue_print_prefix)


@slash_blueprint.before_request
def perform_before_request_tasks():

    g.user_id = request.form['user_id']
    g.channel_id = request.form['channel_id']
    g.team_id = request.form['team_id']
    g.enterprise_id = request.form['enterprise_id']
    g.user_name = request.form['user_name']
    g.response_url = request.form['response_url']


@slash_blueprint.route('/wfh', methods=["POST"])
@slash_blueprint.route('/ooo', methods=["POST"])
def slack_apply_leave(leave_type="ooo"):
    """
    Out of Office: Mark users as Out of Office, with period, email, type (ooo), user name and the raw command
    Work from Home: Mark users as Work from Home, with period, email, type (wfh), user name and the raw command
    :param leave_type: ooo/wfh
    :return:
    """

    if "ooo" in request.path:
        leave_type = "ooo"
    else:
        leave_type = "wfh"

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
                                .format("example@abc.in", str(start_date), str(end_date), str(days_count), leave_type,
                                        raw_text, g.user_name))

        user_email, user_full_name, user_avatar = get_slack_user_info(g.user_id)

        if user_email is not None:

            emp_leave = EmployeeLeaveModel(
                emailAddress="abc@example.com",
                startDate=start_date,
                endDate=end_date,
                daysCount=days_count,
                leaveType=leave_type,
                rawComment=raw_text,
                slackUsername=g.user_name,
                slackUserId=g.user_id,
                slackChannelId=g.channel_id,
                slackTeamId=g.team_id,
                slackEnterpriseId=g.enterprise_id,
                slackFullName=user_full_name,
                slackAvatarUrl=user_avatar,
                createdAt=datetime.now(),
            )

            insert_employee_leave(emp_leave)

            response_msg = "Got it {0}...Safe travel!".format(g.user_name)
            if end_date == start_date:
                attachment_msg = "Out of Office from {0} till {1}".format(start_date.strftime("%d/%b/%y"),
                                                                          end_date.strftime("%d/%b/%y"))
            else:
                attachment_msg = "Out of Office on {0}".format(start_date.strftime("%d/%b/%y"))

            return jsonify(
                {
                    "response_type": "ephemeral",
                    "text": response_msg,
                    "attachments": [
                        {
                            "color": "good",
                            "text": attachment_msg
                        }
                    ]
                }
            ), 200

    return jsonify(
        {
            "response_type": "ephemeral",
            "text": "Oops! Something went wrong... :/",
        }
    ), 200


@slash_blueprint.route('/list', methods=["POST"])
def slack_emp_list_leaves():
    """
    Show all the ooo or wfh listings of the requesting user
    :return:
    """

    emp_leaves = EmployeeLeaveModel.query.filter(
                                                    and_(
                                                        EmployeeLeaveModel.slackUserId == g.user_id,
                                                        EmployeeLeaveModel.slackTeamId == g.team_id,
                                                        EmployeeLeaveModel.endDate >= date.today()
                                                    )
                                                ).all()

    if emp_leaves is not None:

        slack_msg_builder = {
            "response_type": "ephemeral",
            "text": "Following are your leaves:",
        }

        slack_msg_attachment_list = []

        for i, emp_leave in enumerate(emp_leaves):

            if emp_leave.leaveType == "ooo":
                msg_color = "#42a5f5"
            else:
                msg_color = "#bbdefb"

            if emp_leave.startDate == emp_leave.endDate:
                leave_period = "On " + emp_leave.startDate.strftime("%d/%b/%y")
            else:
                leave_period = emp_leave.startDate.strftime("%d/%b/%y") + " to " + emp_leave.endDate.strftime("%d/%b/%y")

            slack_msg_attachment = {
                "title": str(i) + ") " + emp_leave.leaveType.upper(),
                "color": msg_color,
                "text": emp_leave.rawComment,
                "fields": [
                    {
                        "title": "Period",
                        "value": leave_period,
                        "short": True
                    }
                ]
            }

            slack_msg_attachment_list.append(slack_msg_attachment)

        slack_msg_builder["attachments"] = slack_msg_attachment_list

        return jsonify(slack_msg_builder), 200

    else:
        return jsonify(
            {
                "response_type": "ephemeral",
                "text": "Cool! No upcoming leaves for you!",
            }
        ), 200


@slash_blueprint.route('/upcoming', methods=["POST"])
def slack_upcoming_leaves():
    """
    Show all the ooo or wfh of all the users for the requested day
    :return:
    """

    upcoming_leaves = EmployeeLeaveModel.query.filter(
                                                    and_(
                                                        EmployeeLeaveModel.slackTeamId == g.team_id,
                                                        EmployeeLeaveModel.endDate >= date.today()
                                                    )
                                                ).all()

    if upcoming_leaves is not None:

        slack_msg_builder = {
            "response_type": "ephemeral",
            "text": "Coming up:",
        }

        slack_msg_attachment_list = []

        for emp_leave in upcoming_leaves:

            if emp_leave.leaveType == "ooo":
                msg_color = "#42a5f5"
            else:
                msg_color = "#bbdefb"

            if emp_leave.startDate == emp_leave.endDate:
                leave_period = "On " + emp_leave.startDate.strftime("%d/%b/%y")
            else:
                leave_period = emp_leave.startDate.strftime("%d/%b/%y") + " to " + emp_leave.endDate.strftime("%d/%b/%y")

            slack_msg_attachment = {
                "title": emp_leave.slackFullName + " - (" + emp_leave.slackUsername + ")",
                "color": msg_color,
                "text": emp_leave.rawComment,
                "fields": [
                    {
                        "title": "Period",
                        "value": leave_period,
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": emp_leave.leaveType.upper(),
                        "short": True
                    }
                ]
            }

            slack_msg_attachment_list.append(slack_msg_attachment)

        slack_msg_builder["attachments"] = slack_msg_attachment_list

        return jsonify(slack_msg_builder), 200

    else:
        return jsonify(
            {
                "response_type": "ephemeral",
                "text": "Wow! Everybody is in today.",
            }
        ), 200


def insert_employee_leave(emp_leave_info):
    db.session.add(emp_leave_info)
    db.session.commit()


def get_slack_user_info(user_id):

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    slack_user_info = sc.api_call("users.info", user=user_id)

    if slack_user_info is not None and slack_user_info.get("ok") and slack_user_info.get("user") is not None:
        if slack_user_info.get("user").get("profile") is not None:
            slack_user_profile = slack_user_info.get("user").get("profile")
            user_email = slack_user_profile.get("email")
            full_name = slack_user_profile.get("real_name")
            avatar = slack_user_profile.get("image_512")

            return user_email, full_name, avatar
    return None, None, None
