from datetime import date

from flask import Blueprint, request, jsonify, current_app, g
from sqlalchemy.sql.expression import and_

from weisaw.api.extensions import db
from weisaw.base.models.employee_leave_model import EmployeeLeaveModel
from weisaw.worker.tasks import parse_leave

blue_print_name = 'slash'
blue_print_prefix = '/slash'

Model = db.Model

slash_blueprint = Blueprint(blue_print_name, __name__, url_prefix=blue_print_prefix)


@slash_blueprint.before_request
def perform_before_request_tasks():

    g.user_id = request.form.get('user_id')
    g.channel_id = request.form['channel_id']
    g.team_id = request.form['team_id']
    # g.enterprise_id = request.form['enterprise_id']
    g.user_name = request.form['user_name']
    g.response_url = request.form['response_url']


@slash_blueprint.route('/hello', methods=["POST"])
def slack_greet():
    return jsonify(
        {
            "response_type": "ephemeral",
            "text": "Hello, {0}".format(g.user_name),
        }
    ), 200


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

    oauth_access_token = current_app.config.get("SLACK_OAUTH_TOKEN")

    parse_leave.delay(raw_text, leave_type,
                      g.user_name, g.user_id, g.channel_id, g.team_id, g.response_url,
                      oauth_access_token)

    return jsonify(
        {
            "response_type": "ephemeral",
            "text": "Sure, I am processing your leave, will let you know in a moment...",
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
                                                ).order_by(EmployeeLeaveModel.startDate).all()

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
                "title": str(emp_leave.uUid) + ") " + emp_leave.leaveType.upper(),
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
                                                ).order_by(EmployeeLeaveModel.startDate).all()

    if upcoming_leaves is not None and len(upcoming_leaves) > 0:

        slack_msg_builder = {
            "response_type": "in_channel",
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
                "response_type": "in_channel",
                "text": "Wow! Everybody is in today.",
            }
        ), 200


@slash_blueprint.route('/delete', methods=["POST"])
def slack_delete_leave():
    """
    Delete leaves from database
    :return:
    """

    raw_text = request.form['text']

    if raw_text is not None and raw_text != "":

        try:
            leave_id = int(raw_text)
        except ValueError:
            return jsonify(
                {
                    "response_type": "ephemeral",
                    "text": "Could not find your leave...",
                }
            ), 200

        date_after = date.today()

        discard_leave = EmployeeLeaveModel.query.filter(
            and_(
                EmployeeLeaveModel.slackTeamId == g.team_id,
                EmployeeLeaveModel.uUid == leave_id,
                EmployeeLeaveModel.startDate >= date_after
            )
        ).one_or_none()

        if discard_leave is not None:

            db.session.delete(discard_leave)
            db.session.commit()

            slack_msg_builder = {
                "response_type": "ephemeral",
                "text": "Whoosh! its gone, deleted!",
            }

            return jsonify(slack_msg_builder), 200
        else:
            return jsonify(
                {
                    "response_type": "ephemeral",
                    "text": "Could not find your leave...",
                }
            ), 200

    else:
        return jsonify(
            {
                "response_type": "ephemeral",
                "text": "Give me a serial number of your leave and its gone!",
            }
        ), 200


