import requests
import json
import re

from dateparser.search import search_dates
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta
from slackclient import SlackClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery.utils.log import get_task_logger

from weisaw.base.models.employee_leave_model import EmployeeLeaveModel
from weisaw.worker.core import celery_task, BaseTask
from weisaw.base.models.slack_auth_model import SlackOAuth
from weisaw.base.util import tokens as date_tokens

task_base_name = "weisaw.worker."
logger = get_task_logger(__name__)


@celery_task.task(name=task_base_name + "parse_leave",
                  bind=False, max_retries=3, default_retry_delay=300, track_started=True,
                  base=BaseTask)
def parse_leave(raw_text, leave_type, user_name, user_id, channel_id, team_id, response_url, oauth_access_token):
    leaves_date_list = extract_leave_features(raw_text)

    if leaves_date_list is not None and len(leaves_date_list) > 0:

        for leaves_date in leaves_date_list:

            start_date = leaves_date.get("from")
            end_date = leaves_date.get("to")
            leave_delta = end_date - start_date
            days_count = leave_delta.days + 1

            if start_date is not None and end_date is not None and days_count > 0:

                user_email, user_full_name, user_avatar = get_slack_user_info(user_id, team_id, oauth_access_token)

                logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}'
                            .format(user_email, str(start_date), str(end_date), str(days_count), leave_type,
                                    raw_text, user_name))

                if user_email is not None:

                    emp_leave = EmployeeLeaveModel(
                        startDate=start_date,
                        endDate=end_date,
                        daysCount=days_count,
                        leaveType=leave_type,
                        rawComment=raw_text,
                        slackEmailAddress=user_email,
                        slackUsername=user_name,
                        slackUserId=user_id,
                        slackChannelId=channel_id,
                        slackTeamId=team_id,
                        slackFullName=user_full_name,
                        slackAvatarUrl=user_avatar,
                        createdAt=datetime.now(),
                    )

                    insert_employee_leave(emp_leave)

                    if leave_type == "ooo":
                        leave_str = "Out of Office"
                    else:
                        leave_str = "Working from Home"

                    response_msg = "Got it {0}...Safe travel!".format(user_name)
                    if end_date != start_date:
                        attachment_msg = "{0} from {1} till {2}".format(leave_str, start_date.strftime("%d/%b/%y"),
                                                                        end_date.strftime("%d/%b/%y"))
                    else:
                        attachment_msg = "{0} on {1}".format(leave_str, start_date.strftime("%d/%b/%y"))

                    slack_response = {
                        "response_type": "ephemeral",
                        "text": response_msg,
                        "attachments": [
                            {
                                "color": "good",
                                "text": attachment_msg
                            }
                        ]
                    }

                    post_slack_replay(response_url, slack_response)
        return None
    else:
        slack_response = {
            "response_type": "ephemeral",
            "text": "Oops! Something went wrong... :/",
        }

        post_slack_replay(response_url, slack_response)
        return None


def extract_leave_features(raw_text):
    conjunct_parse = False
    date_pattern = re.compile(r"(\d+)(?=st|nd|rd|th)")
    raw_text = raw_text.lower()
    raw_tokens = raw_text.split()

    date_results = []

    for conjunct_token in date_tokens.conjunctions:
        if conjunct_token in raw_tokens:
            if conjunct_token == "to":
                conjunct_index = raw_tokens.index("to")
                subtree_left = raw_tokens[:conjunct_index]
                subtree_right = raw_tokens[conjunct_index + 1:]
                leave_date_left, _, auto_add = parse_conjunct_subtree(subtree_left, date_pattern, is_subtree=True)
                leave_date_right, _, auto_add = parse_conjunct_subtree(subtree_right, date_pattern, auto_add,
                                                                       is_subtree=True)

                if leave_date_right is None:
                    leave_date_right = leave_date_left

                if leave_date_left is not None and leave_date_right is not None:
                    if leave_date_left > leave_date_right:
                        date_results.append({"from": leave_date_right, "to": leave_date_left})
                    else:
                        date_results.append({"from": leave_date_left, "to": leave_date_right})

            else:
                conjunct_index = raw_tokens.index(conjunct_token)
                subtree_left = raw_tokens[:conjunct_index]
                subtree_right = raw_tokens[conjunct_index + 1:]
                leave_date_left, _, auto_add = parse_conjunct_subtree(subtree_left, date_pattern, is_subtree=True)
                leave_date_right, _, auto_add = parse_conjunct_subtree(subtree_right, date_pattern, is_subtree=True)

                if leave_date_left is not None:
                    date_results.append({"from": leave_date_left, "to": leave_date_left})
                if leave_date_right is not None:
                    date_results.append({"from": leave_date_right, "to": leave_date_right})

            conjunct_parse = True

    if not conjunct_parse:
        leave_date_start, leave_date_end, auto_add = parse_conjunct_subtree(raw_tokens, date_pattern)
        if leave_date_start is not None and leave_date_end is not None:
            date_results.append({"from": leave_date_start, "to": leave_date_end})
        elif leave_date_start is not None:
            date_results.append({"from": leave_date_start, "to": leave_date_start})

    return date_results


def parse_conjunct_subtree(sub_tree, date_pattern, auto_add=0, is_subtree=False):
    week_day_now = datetime.now().weekday()
    day_now = datetime.now().day
    month_now = datetime.now().month
    year_now = datetime.now().year
    date_now = datetime.now()
    leave_date = date_now
    is_subtree_parsed = False

    for i, sub_token in enumerate(sub_tree):
        inc_next = False
        if i > 0 and (sub_tree[i - 1] == "next" or sub_tree[i - 1] == "after"):
            inc_next = True

        if sub_token == "today":
            return leave_date, None, None

        elif sub_token == "tomorrow":
            if inc_next:
                leave_date = datetime.now() + relativedelta(days=2)
            else:
                leave_date = datetime.now() + relativedelta(days=1)
            return leave_date, None, None

        elif sub_token == "week":
            is_subtree_parsed = True
            if inc_next:
                # Get next Monday to Friday
                leave_start = date_now + relativedelta(days=-date_now.weekday(), weeks=1)
                leave_end = leave_start + relativedelta(days=4)
                return leave_start, leave_end, None
            if "rest" in sub_tree:
                # Get next day to Friday
                leave_start = datetime.now() + relativedelta(days=1)
                friday_date = 4 - date_now.weekday()
                leave_end = date_now + relativedelta(days=friday_date)
                return leave_start, leave_end, None

        elif sub_token in date_tokens.week_days:
            is_subtree_parsed = True
            # Monday is 0 and Sunday is 6
            week_index = date_tokens.week_days.index(sub_token)
            delta_day = week_index - week_day_now
            set_auto_inc = False
            if delta_day < 0:
                delta_day = 7 + delta_day
                set_auto_inc = True
            if inc_next:
                delta_day = delta_day + 7

            delta_day += auto_add
            leave_date = leave_date + relativedelta(days=delta_day)

            if set_auto_inc:
                auto_add = 7

        elif sub_token in date_tokens.months or sub_token in date_tokens.months_short:
            is_subtree_parsed = True
            if sub_token in date_tokens.months:
                month_index = date_tokens.months.index(sub_token) + 1
            else:
                month_index = date_tokens.months_short.index(sub_token) + 1
            delta_month = month_index - month_now
            if delta_month < 0:
                delta_month = delta_month + 12
            leave_date = leave_date + relativedelta(months=delta_month)

        str_match = ' '.join(sub_tree)
        date_matched = re.search(date_pattern, str_match)
        if date_matched is not None and date_matched.group() is not None:
            is_subtree_parsed = True
            date_extracted = int(date_matched.group())
            # if day_now < date_extracted:
            #     pass
            leave_date = leave_date.replace(day=date_extracted)
    if is_subtree and not is_subtree_parsed:
        return None, None, auto_add
    return leave_date, None, auto_add


def is_short_month(short_token):
    for i, month in enumerate(date_tokens.months):
        if month.startswith(short_token):
            return i + 1
    return 0


def get_db_session():
    db = create_engine(os.getenv("DATABASE_URL"), echo=True)
    session_maker = sessionmaker(bind=db)
    session = session_maker()
    return session


def insert_employee_leave(emp_leave_info):
    session = get_db_session()
    session.add(emp_leave_info)
    session.commit()

    logger.debug("Inserted user leave information")


def get_slack_access_token(team_id):
    slack_auth = SlackOAuth.query.filter_by(slackTeamId=team_id).order_by(SlackOAuth.updatedAt.desc()).first()
    if slack_auth is not None:
        return slack_auth.accessToken


def get_slack_user_info(user_id, team_id, oauth_access_token):
    logger.debug("Fetching access token for the team")
    if oauth_access_token is None:
        slack_access_token = get_slack_access_token(team_id)
    else:
        slack_access_token = oauth_access_token

    if slack_access_token is not None:
        logger.debug("Fetching user info")
        sc = SlackClient(slack_access_token)

        slack_user_info = sc.api_call("users.info", user=user_id)

        if slack_user_info is not None and slack_user_info.get("ok") and slack_user_info.get("user") is not None:
            if slack_user_info.get("user").get("profile") is not None:
                slack_user_profile = slack_user_info.get("user").get("profile")
                user_email = slack_user_profile.get("email")
                full_name = slack_user_profile.get("real_name")
                avatar = slack_user_profile.get("image_512")

                return user_email, full_name, avatar
    return None, None, None


def post_slack_replay(response_url, payload):
    headers = {
        'Content-Type': "application/json"
    }

    response = requests.post(response_url, data=json.dumps(payload), headers=headers)

    logger.debug(response)
