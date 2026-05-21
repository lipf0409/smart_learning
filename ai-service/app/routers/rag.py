# RAG API Router - 知识库管理接口(预留)
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.services.rag_service import get_rag_service, KnowledgeChunk

router = APIRouter(prefix="/api/rag", tags=["rag"])


class KnowledgeInput(BaseModel):
    """知识输入模型"""
    title: str
    content: str
    subject: Optional[str] = None
    source: Optional[str] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[KnowledgeChunk]
    total: int


@router.post("/knowledge")
async def add_knowledge(knowledge: KnowledgeInput):
    """
    添加知识到向量库

    未来功能：
    - 将知识内容向量化
    - 存储到向量数据库
    - 建立索引
    """
    rag = get_rag_service()

    chunk = KnowledgeChunk(
        id=f"knowledge_{hash(knowledge.title)}",
        title=knowledge.title,
        content=knowledge.content,
        subject=knowledge.subject,
        source=knowledge.source
    )

    success = await rag.index_knowledge(chunk)
    return {
        "success": success,
        "message": "知识点已添加" if success else "添加失败",
        "id": chunk.id
    }


@router.get("/search", response_model=SearchResponse)
async def search_knowledge(query: str, top_k: int = 3):
    """
    搜索相关知识

    未来功能：
    - 将查询向量化
    - 在向量数据库中搜索相似内容
    - 返回最相关的知识点
    """
    rag = get_rag_service()
    results = await rag.search_relevant(query, top_k)

    return SearchResponse(
        results=results,
        total=len(results)
    )


@router.post("/generate")
async def generate_answer(query: str, use_rag: bool = True):
    """
    RAG增强的答案生成

    未来功能：
    - 搜索相关知识
    - 构建增强prompt
    - 调用LLM生成回答
    """
    rag = get_rag_service()

    if use_rag:
        context = await rag.search_relevant(query)
    else:
        context = []

    answer = await rag.generate_with_context(query, context)

    return {
        "answer": answer,
        "context_used": len(context),
        "sources": [c.title for c in context]
    }


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    """
    删除知识点

    未来功能：
    - 从向量数据库中删除
    - 更新索引
    """
    rag = get_rag_service()
    success = await rag.delete_knowledge(knowledge_id)

    return {
        "success": success,
        "message": "知识点已删除" if success else "删除失败"
    }


@router.get("/health")
async def rag_health():
    """RAG服务健康检查"""
    return {
        "status": "ok",
        "service": "MockRAGService",
        "message": "RAG服务已就绪，当前使用Mock实现"
    }
