# Chat Record Model - AI答疑记录
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ChatRecord(Base):
    """AI答疑记录表"""
    __tablename__ = "t_chat_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, comment="用户ID")
    session_id = Column(String(100), nullable=False, comment="会话ID")

    # 对话内容
    role = Column(String(20), nullable=False, comment="角色: user/assistant")
    question = Column(Text, comment="用户问题")
    response = Column(Text, comment="AI回复")

    # 结构化数据
    hints = Column(JSON, comment="提示列表")
    related_knowledge = Column(JSON, comment="相关知识点")

    # 分类信息
    subject = Column(String(50), comment="学科分类")

    # 元数据
    model_version = Column(String(50), comment="使用的模型版本")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "role": self.role,
            "question": self.question,
            "response": self.response,
            "hints": self.hints or [],
            "related_knowledge": self.related_knowledge or [],
            "subject": self.subject,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
