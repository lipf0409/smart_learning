# RAG Service - Retrieval-Augmented Generation (预留接口)
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class KnowledgeChunk(BaseModel):
    """知识块"""
    id: str
    title: str
    content: str
    subject: Optional[str] = None
    source: Optional[str] = None
    similarity: Optional[float] = None


class RAGServiceInterface(ABC):
    """RAG服务接口 - 抽象基类

    未来可替换为真实的向量数据库实现，如：
    - Milvus
    - Pinecone
    - Elasticsearch with vector search
    - ChromaDB
    """

    @abstractmethod
    async def index_knowledge(self, knowledge: KnowledgeChunk) -> bool:
        """索引知识点到向量数据库"""
        pass

    @abstractmethod
    async def search_relevant(self, query: str, top_k: int = 3) -> List[KnowledgeChunk]:
        """搜索相关知识"""
        pass

    @abstractmethod
    async def generate_with_context(
        self,
        query: str,
        context: List[KnowledgeChunk]
    ) -> str:
        """基于上下文生成回答"""
        pass

    @abstractmethod
    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """删除知识点"""
        pass


class MockRAGService(RAGServiceInterface):
    """Mock实现 - 当前使用

    未来替换为真实实现时，只需修改 get_rag_service() 函数
    """

    async def index_knowledge(self, knowledge: KnowledgeChunk) -> bool:
        """Mock: 暂不实现"""
        print(f"[RAG Mock] 知识点已索引: {knowledge.title}")
        return True

    async def search_relevant(self, query: str, top_k: int = 3) -> List[KnowledgeChunk]:
        """Mock: 返回空列表"""
        print(f"[RAG Mock] 搜索查询: {query}")
        return []

    async def generate_with_context(
        self,
        query: str,
        context: List[KnowledgeChunk]
    ) -> str:
        """Mock: 返回空字符串"""
        print(f"[RAG Mock] 生成回答，上下文数量: {len(context)}")
        return ""

    async def delete_knowledge(self, knowledge_id: str) -> bool:
        """Mock: 暂不实现"""
        print(f"[RAG Mock] 知识点已删除: {knowledge_id}")
        return True


# 工厂方法 - 未来可替换为真实实现
_rag_service: Optional[RAGServiceInterface] = None


def get_rag_service() -> RAGServiceInterface:
    """获取RAG服务实例"""
    global _rag_service
    if _rag_service is None:
        # 当前使用 Mock 实现
        # 未来可替换为: MilvusRAGService() 或其他真实实现
        _rag_service = MockRAGService()
    return _rag_service


def set_rag_service(service: RAGServiceInterface):
    """设置RAG服务实例（用于切换实现）"""
    global _rag_service
    _rag_service = service