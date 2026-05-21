# Question Record Model - 搜题记录
from sqlalchemy import Column, BigInteger, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class QuestionRecord(Base):
    """搜题记录表"""
    __tablename__ = "t_question_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, comment="用户ID")

    # 题目信息
    question_text = Column(Text, comment="OCR识别的题目文本")
    image_url = Column(String(500), comment="题目图片存储路径")

    # 答案信息
    answer = Column(Text, comment="最终答案")
    steps = Column(JSON, comment="解题步骤(JSON数组)")
    knowledge_points = Column(JSON, comment="涉及知识点(JSON数组)")

    # 分类信息
    subject = Column(String(50), comment="学科分类")
    difficulty = Column(String(20), comment="难度等级")

    # 处理状态
    ocr_method = Column(String(50), comment="OCR识别方式")
    success = Column(Boolean, default=True, comment="是否成功解答")
    error_message = Column(String(500), comment="错误信息")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question_text": self.question_text,
            "answer": self.answer,
            "steps": self.steps or [],
            "knowledge_points": self.knowledge_points or [],
            "subject": self.subject,
            "success": self.success,
            "ocr_method": self.ocr_method,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
