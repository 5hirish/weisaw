from weisaw.api.extensions import db
from sqlalchemy.types import VARCHAR, TIMESTAMP, TEXT, INTEGER
from sqlalchemy import text
from datetime import datetime

# Alias common SQLAlchemy names
Column = db.Column
Relationship = db.relationship
Model = db.Model


class SlackOAuth(Model):
    __tablename__ = 'slackOAuth'

    uUid = Column(INTEGER, primary_key=True, unique=True, nullable=False)
    authScope = Column(TEXT, nullable=False)
    accessToken = Column(TEXT, nullable=False)
    slackTeamId = Column(VARCHAR(15), nullable=False)
    slackTeamName = Column(VARCHAR(255), nullable=True)
    slackUserId = Column(VARCHAR(15), nullable=False)
    slackAuthChannelId = Column(VARCHAR(15), nullable=False)
    slackAuthChannel = Column(VARCHAR(255), nullable=False)
    slackWebHookUrl = Column(TEXT, nullable=False)
    updatedAt = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)