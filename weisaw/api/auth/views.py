import os

from flask import Blueprint, request, jsonify, current_app
from slackclient import SlackClient

from weisaw.api.extensions import db
from weisaw.base.models.slack_auth_model import SlackOAuth

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

    current_app.logger.debug("Requested access token")

    if auth_response is not None and auth_response.get("ok"):
        auth_access_token = auth_response.get("access_token")
        auth_scope = auth_response.get("scope")
        auth_team_id = auth_response.get("team_id")
        auth_team_name = auth_response.get("team_name")
        auth_user_id = auth_response.get("user_id")
        auth_incoming_webhook = auth_response.get("incoming_webhook")
        auth_channel = auth_incoming_webhook.get("channel")
        auth_channel_id = auth_incoming_webhook.get("channel_id")
        auth_webhook_url = auth_incoming_webhook.get("url")

        slack_oauth = SlackOAuth(
            authScope=auth_scope,
            accessToken=auth_access_token,
            slackTeamId=auth_team_id,
            slackTeamName=auth_team_name,
            slackUserId=auth_user_id,
            slackAuthChannelId=auth_channel_id,
            slackAuthChannel=auth_channel,
            slackWebHookUrl=auth_webhook_url
        )

        db.session.add(slack_oauth)
        db.session.commit()

        current_app.logger.debug("Inserted access token")

        return jsonify({"status": "success", "msg": "Authentication successful"}), 200
    return jsonify({"status": "failure", "msg": "Authentication failed"}), 200
