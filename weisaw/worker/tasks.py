import spacy
import dateparser
import requests
import json
from spacy.symbols import *
from datetime import datetime
from slackclient import SlackClient
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import group, chain, states
from celery.utils.log import get_task_logger

from weisaw.base.models.employee_leave_model import EmployeeLeaveModel
from weisaw.worker.core import celery_task, BaseTask
from weisaw.base.models.slack_auth_model import SlackOAuth

task_base_name = "weisaw.worker."
logger = get_task_logger(__name__)


@celery_task.task(name=task_base_name + "parse_leave",
                  bind=False, max_retries=3, default_retry_delay=300, track_started=True,
                  base=BaseTask)
def parse_leave(raw_text, leave_type, user_name, user_id, channel_id, team_id, response_url):

    start_date, end_date, days_count = extract_leave_features(raw_text)

    if start_date is not None and end_date is not None and days_count > 0:

        user_email, user_full_name, user_avatar = get_slack_user_info(user_id, team_id)

        logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}'
                    .format(user_email, str(start_date), str(end_date), str(days_count), leave_type,
                            raw_text, user_name))

        if user_email is not None:

            emp_leave = EmployeeLeaveModel(
                emailAddress=user_email,
                startDate=start_date,
                endDate=end_date,
                daysCount=days_count,
                leaveType=leave_type,
                rawComment=raw_text,
                slackUsername=user_name,
                slackUserId=user_id,
                slackChannelId=channel_id,
                slackTeamId=team_id,
                slackFullName=user_full_name,
                slackAvatarUrl=user_avatar,
                createdAt=datetime.now(),
            )

            insert_employee_leave(emp_leave)

            response_msg = "Got it {0}...Safe travel!".format(user_name)
            if end_date == start_date:
                attachment_msg = "Out of Office from {0} till {1}".format(start_date.strftime("%d/%b/%y"),
                                                                          end_date.strftime("%d/%b/%y"))
            else:
                attachment_msg = "Out of Office on {0}".format(start_date.strftime("%d/%b/%y"))

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

        slack_response = {
                "response_type": "ephemeral",
                "text": "Oops! Something went wrong... :/",
            }

        post_slack_replay(response_url, slack_response)
        return None


def extract_leave_features(raw_text):
    nlp = spacy.load('en_core_web_sm')
    cmd_doc = nlp(raw_text)

    date_list = []
    start_date, end_date = None, None
    days_count = 0
    leave_date_list = []

    np_labels = set([nsubj, nsubjpass, dobj, iobj, pobj])
    np_tags = set([PROPN, NOUN])

    for token in cmd_doc:
        # if token.dep in np_labels:
        #     noun_phrase = token.subtree
        # if token.dep == root and token.tag_ == ADV:
        if token.pos in np_tags:
            if token.dep_ == "ROOT":
                # PROPN > NOUN >ADJ
                for sub_token in token.subtree:
                    print(sub_token.text, sub_token.dep_, sub_token.pos_)

        if token.ent_type_ == "DATE" or token.ent_type_ == "TIME" or token.ent_type_ == "ORDINAL":
            date_list.append(dateparser.parse(token.text, languages=['en']))

    if date_list is not None and len(date_list) > 0:
        date_list.sort(reverse=True)

        if len(date_list) == 2:

            end_date = date_list[0]
            start_date = date_list[1]
            delta_leave = end_date - start_date
            leave_date_list.append({"from": start_date, "to": end_date})
            # days_count = delta_leave.days + 1

        elif len(date_list) == 1:
            end_date = date_list[0]
            start_date = date_list[0]
            leave_date_list.append({"from": start_date, "to": end_date})
            # days_count = 1

    return leave_date_list


def get_db_session():
    db = create_engine('sqlite:///:memory:', echo=True)
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


def get_slack_user_info(user_id, team_id):
    logger.debug("Fetching access token for the team")
    slack_access_token = get_slack_access_token(team_id)

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
