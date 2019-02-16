import spacy
import dateparser
import os
from datetime import datetime, date
from slackclient import SlackClient
from flask import Blueprint, Response, request, jsonify, session, send_file, current_app, g

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_

from weisaw.api.extensions import db

blue_print_name = 'auth'
blue_print_prefix = '/auth'

Model = db.Model

auth_blueprint = Blueprint(blue_print_name, __name__, url_prefix=blue_print_prefix)


@auth_blueprint.route("/initiate", methods=["GET"])
def pre_install():
    client_id = os.environ.get("SLACK_CLIENT_ID")
    oauth_scope = os.environ.get("SLACK_BOT_SCOPE")

    return '''
      <a href="https://slack.com/oauth/authorize?scope={0}&client_id={1}">
          <img alt="Add to Slack" height="40" width="139" 
          src="https://platform.slack-edge.com/img/add_to_slack.png" 
          srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, 
          https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" />
      </a>
  '''.format(oauth_scope, client_id)


@auth_blueprint.route("/finish", methods=["GET", "POST"])
def post_install():

    client_id = os.environ.get("SLACK_CLIENT_ID")
    client_secret = os.environ.get("SLACK_CLIENT_SECRET")
    oauth_scope = os.environ.get("SLACK_BOT_SCOPE")
    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    sc = SlackClient("")

    # Request the auth tokens from Slack
    auth_response = sc.api_call(
        "oauth.access",
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )

    print(auth_response)

    if auth_response is not None:
        pass

    # os.environ["SLACK_USER_TOKEN"] = auth_response['access_token']
    # os.environ["SLACK_BOT_TOKEN"] = auth_response['bot']['bot_access_token']

    return jsonify(auth_response), 200
