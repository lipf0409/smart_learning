# Knowledge Base Model - RAG知识库(预留)
from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base


class KnowledgeBase(Base):
    """RAG知识库表"""
    __tablename__ = "t_knowledge_base"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 知识内容
    title = Column(String(200), nullable=False, comment="知识点标题")
    content = Column(Text, nullable=False, comment="知识点内容")
    subject = Column(String(50), comment="所属学科")

    # 向量索引(预留)
    vector_id = Column(String(100), comment="向量数据库中的ID")
    embedding_model = Column(String(50), comment="嵌入模型")

    # 元数据
    source = Column(String(200), comment="知识来源")
    difficulty = Column(String(20), comment="难度等级")
    tags = Column(JSON, comment="标签列表")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "subject": self.subject,
            "vector_id": self.vector_id,
            "source": self.source,
            "difficulty": self.difficulty,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }