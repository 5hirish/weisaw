from weisaw.api.extensions import db
from sqlalchemy.types import VARCHAR, TIMESTAMP, DATE, TEXT, INTEGER
from datetime import datetime

# Alias common SQLAlchemy names
Column = db.Column
Relationship = db.relationship
Model = db.Model


class EmployeeLeaveModel(Model):
    __tablename__ = 'slackEmpLeaves'

    uUid = Column(INTEGER, primary_key=True, unique=True, nullable=False)
    startDate = Column(DATE, nullable=False)
    endDate = Column(DATE, nullable=False)
    daysCount = Column(INTEGER, nullable=False)
    leaveType = Column(VARCHAR(15), nullable=False)
    rawComment = Column(TEXT, nullable=True)
    slackEmailAddress = Column(VARCHAR(255), nullable=False)
    slackUsername = Column(VARCHAR(15), nullable=False)
    slackUserId = Column(VARCHAR(15), nullable=False)
    slackChannelId = Column(VARCHAR(15), nullable=False)
    slackTeamId = Column(VARCHAR(15), nullable=False)
    slackFullName = Column(VARCHAR(255), nullable=True)
    slackAvatarUrl = Column(TEXT, nullable=True)
    createdAt = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)