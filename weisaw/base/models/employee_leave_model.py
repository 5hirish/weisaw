from weisaw.api.extensions import db
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, TIMESTAMP, DATE, TEXT, ARRAY, BOOLEAN, INTEGER
from sqlalchemy import ForeignKey, String, Integer, text
from datetime import datetime

# Alias common SQLAlchemy names
Column = db.Column
Relationship = db.relationship
Model = db.Model


class EmployeeLeaveModel(Model):
    __tablename__ = 'slackEmpLeaves'

    uUid = Column(UUID, primary_key=True, server_default=text("uuid_generate_v4()"), unique=True, nullable=False)
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
    slackEnterpriseId = Column(VARCHAR(15), nullable=True)
    slackFullName = Column(VARCHAR(255), nullable=True)
    slackAvatarUrl = Column(TEXT, nullable=True)
    createdAt = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)