from weisaw.api.extensions import db
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, TIMESTAMP, DATE, TEXT, ARRAY, BOOLEAN, INTEGER
from sqlalchemy import ForeignKey, String, Integer, text
from datetime import datetime

# Alias common SQLAlchemy names
Column = db.Column
Relationship = db.relationship
Model = db.Model


class SlackOAuth(Model):
    __tablename__ = 'slackOAuth'

    uUid = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), unique=True, nullable=False)
    authScope = Column(TEXT, nullable=False)
    accessToken = Column(TEXT, nullable=False)
    slackTeamId = Column(VARCHAR(15), nullable=False)
    slackTeamName = Column(VARCHAR(255), nullable=True)
    slackUserId = Column(VARCHAR(15), nullable=False)
    slackAuthChannelId = Column(VARCHAR(15), nullable=False)
    slackAuthChannel = Column(VARCHAR(255), nullable=False)
    slackWebHookUrl = Column(TEXT, nullable=False)
    updatedAt = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)