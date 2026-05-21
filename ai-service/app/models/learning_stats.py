# Learning Stats Model - 学习统计
from sqlalchemy import Column, BigInteger, Integer, JSON, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class LearningStats(Base):
    """学习统计表"""
    __tablename__ = "t_learning_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, unique=True, comment="用户ID")

    # 总体统计
    total_questions = Column(Integer, default=0, comment="总解题数")
    correct_count = Column(Integer, default=0, comment="正确数")
    total_study_time = Column(Integer, default=0, comment="总学习时长(分钟)")

    # 学科统计(JSON)
    subject_stats = Column(JSON, comment="各学科统计")
    # 格式: {"数学": {"total": 10, "correct": 8}, "物理": {...}}

    # 知识点统计(JSON)
    knowledge_stats = Column(JSON, comment="知识点掌握统计")
    # 格式: {"三角函数": {"total": 5, "correct": 3, "weak": true}, ...}

    # 连续学习
    streak_days = Column(Integer, default=0, comment="连续学习天数")
    last_study_date = Column(Date, comment="最后学习日期")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "correct_rate": self.correct_count / max(self.total_questions, 1),
            "total_study_time": self.total_study_time,
            "subject_stats": self.subject_stats or {},
            "knowledge_stats": self.knowledge_stats or {},
            "streak_days": self.streak_days,
            "last_study_date": self.last_study_date.isoformat() if self.last_study_date else None
        }