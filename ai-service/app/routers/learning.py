# Learning Analysis Service (知识漏洞分析与学习报告)
import base64
import hashlib
import hmac
import json
import re
import uuid
from datetime import datetime, date
from wsgiref.handlers import format_date_time
from time import mktime
from urllib.parse import urlencode, quote
import websocket
from fastapi import APIRouter, HTTPException, Depends, Form
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import ssl
import threading

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.redis_client import redis_client
from app.models import QuestionRecord, ChatRecord, LearningStats

router = APIRouter(prefix="/api/learning", tags=["learning"])


# ============ Pydantic Models ============

class QuestionRecordInput(BaseModel):
    question_text: str
    subject: str
    knowledge_points: List[str]
    success: bool
    timestamp: str


class LearningReport(BaseModel):
    total_questions: int
    correct_rate: float
    subjects: Dict[str, int]
    weak_points: List[Dict]
    strong_points: List[str]
    recommendations: List[str]
    practice_suggestions: List[Dict]


class StudyPlan(BaseModel):
    daily_goals: List[Dict]
    weekly_plan: List[Dict]
    focus_areas: List[str]
    timeline: str
    milestones: List[Dict]


class ChatMessage(BaseModel):
    role: str
    content: str


class AIChatResponse(BaseModel):
    response: str
    hints: List[str]
    related_knowledge: List[str]


# ============ 星火大模型 API (Lite版本用于AI答疑) ============

def create_spark_lite_auth_url() -> tuple:
    """生成星火Lite API鉴权URL - 用于AI答疑"""
    # Lite版本固定配置
    base_url = "wss://spark-api.xf-yun.com/v1.1/chat"
    path = "/v1.1/chat"
    domain = "lite"  # Lite版本的domain是"lite"，不是"general"

    host = "spark-api.xf-yun.com"

    now = datetime.now()
    date_str = format_date_time(mktime(now.timetuple()))

    signature_origin = f"host: {host}\ndate: {date_str}\nGET {path} HTTP/1.1"

    signature_sha = hmac.new(
        settings.SPARK_LITE_API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    signature = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{settings.SPARK_LITE_API_KEY}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{signature}"'
    )

    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    auth_url = f"{base_url}?authorization={quote(authorization)}&date={quote(date_str)}&host={host}"

    return auth_url, domain


def call_spark_lite_api(prompt: str, history: List[Dict] = None) -> str:
    """调用星火Lite大模型API - 用于AI答疑"""
    if not all([settings.SPARK_LITE_APP_ID, settings.SPARK_LITE_API_KEY, settings.SPARK_LITE_API_SECRET]):
        raise ValueError("星火Lite API配置不完整")

    ws_url, domain = create_spark_lite_auth_url()

    result_text = []
    error_msg = [None]
    ws_ready = threading.Event()

    def on_message(ws, message):
        try:
            data = json.loads(message)
            code = data.get('header', {}).get('code', 0)

            if code != 0:
                error_msg[0] = f"API Error {code}: {data.get('header', {}).get('message', 'Unknown')}"
                ws.close()
                return

            choices = data.get('payload', {}).get('choices', {})
            text_list = choices.get('text', [])
            if text_list:
                content = text_list[0].get('content', '')
                result_text.append(content)

            status = data.get('header', {}).get('status', 0)
            if status == 2:
                ws.close()

        except Exception as e:
            error_msg[0] = str(e)
            ws.close()

    def on_error(ws, error):
        error_msg[0] = str(error)
        ws_ready.set()

    def on_close(ws, close_status_code, close_msg):
        ws_ready.set()

    def on_open(ws):
        text_messages = []

        if history:
            for msg in history:
                text_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        text_messages.append({
            "role": "user",
            "content": prompt
        })

        message = {
            "header": {
                "app_id": settings.SPARK_LITE_APP_ID,
                "uid": "user_001"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": text_messages
                }
            }
        }
        ws.send(json.dumps(message))

    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    ws_ready.wait(timeout=60)

    if error_msg[0]:
        raise Exception(error_msg[0])

    result = ''.join(result_text)
    return result


# ============ 结构化响应解析 ============

def build_heuristic_prompt(question: str, subject: str, history: List = None) -> str:
    """构建启发式教学prompt - 针对Lite模型优化，支持历史对话"""
    # 构建历史对话上下文
    history_context = ""
    if history and len(history) > 0:
        history_context = "\n\n【历史对话】\n"
        for msg in history[-6:]:  # 只取最近6轮对话
            # 兼容 dict 和 ChatMessage 对象
            if hasattr(msg, 'role'):
                role = "学生" if msg.role == "user" else "老师"
                content = msg.content
            else:
                role = "学生" if msg.get("role") == "user" else "老师"
                content = msg.get("content", "")
            history_context += f"{role}：{content}\n"
        history_context += "\n请根据历史对话继续引导学生，不要重复之前的问题。"

    # 根据学科生成不同的示例
    examples = {
        "数学": """示例回复：
引导：你觉得这个方程有什么特点？
提示：看看方程的形式
提示：想想如何把它变成完全平方
知识：一元二次方程
知识：求根公式""",
        "物理": """示例回复：
引导：你觉得力与运动之间有什么关系？
提示：想想日常生活中的例子
提示：力的大小会影响什么
知识：牛顿第二定律
知识：力和加速度""",
        "化学": """示例回复：
引导：你觉得这个反应有什么特点？
提示：看看反应物和生成物
提示：想想电子的转移
知识：氧化还原反应
知识：化学方程式""",
        "语文": """示例回复：
引导：你觉得这篇文章的主题是什么？
提示：看看文章的结构
提示：想想作者的写作意图
知识：文章主旨
知识：写作手法""",
        "英语": """示例回复：
引导：你觉得这句话的意思是什么？
提示：看看句子的结构
提示：想想关键词的含义
知识：语法结构
知识：词汇含义"""
    }

    example_text = examples.get(subject, examples["数学"])

    return f"""你是{subject}学科的启发式教学老师。
{history_context}

当前学生问题："{question}"

请用启发式方法引导学生思考，不要直接给答案。

重要规则：
1. 学生已经掌握的知识点不要再重复讲解
2. 如果学生问的是新问题，请针对新问题进行引导
3. 如果学生回答正确，给予肯定后继续深入
4. 不要重复之前问过的问题
5. 必须针对{subject}学科的问题回答，不要回答其他学科的内容

回复格式要求：
引导：用一个问题引导学生思考（一句话）
提示：简短提示1
提示：简短提示2
知识：知识点名称1
知识：知识点名称2

{example_text}

请按上述格式回复："""


def parse_structured_response(text: str) -> dict:
    """解析结构化文本响应"""
    result = {
        "response": "",
        "hints": [],
        "related_knowledge": []
    }

    if not text:
        return result

    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 匹配 "引导：" 或 "【回复】"
        if line.startswith('引导：') or line.startswith('引导:'):
            result["response"] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
        elif line.startswith('【回复】'):
            result["response"] = line.replace('【回复】', '').strip()
        # 匹配 "提示：" 或 "【提示"
        elif line.startswith('提示：') or line.startswith('提示:'):
            hint = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            if hint:
                result["hints"].append(hint)
        elif line.startswith('【提示'):
            hint = re.sub(r'【提示\d*】', '', line).strip()
            # 去掉冒号后面的长解释，只取简短提示
            if '：' in hint:
                hint = hint.split('：')[0].strip()
            if hint and len(hint) < 50:
                result["hints"].append(hint)
        # 匹配 "知识：" 或 "【知识点"
        elif line.startswith('知识：') or line.startswith('知识:'):
            knowledge = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            if knowledge:
                result["related_knowledge"].append(knowledge)
        elif line.startswith('【知识点'):
            knowledge = re.sub(r'【知识点\d*】', '', line).strip()
            # 去掉冒号后面的长解释，只取知识点名称
            if '：' in knowledge:
                knowledge = knowledge.split('：')[0].strip()
            if knowledge and len(knowledge) < 30:
                result["related_knowledge"].append(knowledge)

    # 如果解析失败，使用原文作为回复
    if not result["response"]:
        result["response"] = text[:200] if len(text) > 200 else text
        result["hints"] = ["试着从基本概念出发思考"]

    return result


def parse_json_response(text: str) -> Optional[dict]:
    """尝试解析JSON响应"""
    try:
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return None


# ============ 缓存工具函数 ============

def get_question_hash(question: str, subject: str) -> str:
    """生成问题缓存key"""
    content = f"{question}:{subject}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


async def get_cached_response(question: str, subject: str) -> Optional[dict]:
    """获取缓存的AI响应"""
    key = f"ai:response:{get_question_hash(question, subject)}"
    return await redis_client.get(key)


async def cache_response(question: str, subject: str, response: dict):
    """缓存AI响应"""
    key = f"ai:response:{get_question_hash(question, subject)}"
    await redis_client.set(key, response, settings.CACHE_AI_RESPONSE_TTL)


# ============ API 接口 ============

class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str
    subject: str
    user_id: Optional[int] = None
    history: Optional[List[ChatMessage]] = None


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    全天候启发式AI答疑

    功能：
    - 启发式引导思考，不直接给出答案
    - 杜绝惰性学习
    - 提供相关知识链接
    - 支持历史对话上下文
    - 记录对话历史
    """
    try:
        question = request.question
        subject = request.subject
        user_id = request.user_id
        history = request.history or []

        # 1. 构建带历史对话的prompt
        prompt = build_heuristic_prompt(question, subject, history)

        # 2. 调用星火Lite API
        result_text = call_spark_lite_api(prompt)

        # 3. 解析响应 - 优先尝试结构化解析
        parsed = parse_structured_response(result_text)

        # 如果结构化解析失败，尝试JSON解析
        if not parsed["response"]:
            json_data = parse_json_response(result_text)
            if json_data:
                parsed = json_data

        # 确保响应有效
        if not parsed["response"]:
            parsed["response"] = result_text
        if not parsed["hints"]:
            parsed["hints"] = ["试着从基本概念出发思考"]
        if not parsed["related_knowledge"]:
            parsed["related_knowledge"] = []

        response = AIChatResponse(**parsed)

        # 4. 保存到数据库
        session_id = str(uuid.uuid4())
        chat_record = ChatRecord(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            question=question,
            response=response.response,
            hints=response.hints,
            related_knowledge=response.related_knowledge,
            subject=subject,
            model_version="lite"
        )
        db.add(chat_record)
        await db.commit()

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/records")
async def get_chat_records(
    user_id: int = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天记录"""
    try:
        query = select(ChatRecord).order_by(ChatRecord.created_at.desc()).limit(limit)
        if user_id:
            query = query.where(ChatRecord.user_id == user_id)

        result = await db.execute(query)
        records = result.scalars().all()

        return {
            "records": [r.to_dict() for r in records],
            "total": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_learning_stats(
    user_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """获取学习统计数据"""
    try:
        # 尝试从缓存获取
        cache_key = f"stats:user:{user_id or 'anonymous'}"
        cached = await redis_client.get(cache_key)
        if cached:
            return cached

        # 查询搜题统计
        question_query = select(
            func.count(QuestionRecord.id).label('total'),
            func.sum(func.if_(QuestionRecord.success == True, 1, 0)).label('correct')
        )
        if user_id:
            question_query = question_query.where(QuestionRecord.user_id == user_id)

        question_result = await db.execute(question_query)
        question_stats = question_result.first()

        # 查询聊天统计
        chat_query = select(func.count(ChatRecord.id))
        if user_id:
            chat_query = chat_query.where(ChatRecord.user_id == user_id)

        chat_result = await db.execute(chat_query)
        chat_count = chat_result.scalar()

        # 查询学科分布
        subject_query = select(
            QuestionRecord.subject,
            func.count(QuestionRecord.id).label('count')
        ).group_by(QuestionRecord.subject)
        if user_id:
            subject_query = subject_query.where(QuestionRecord.user_id == user_id)

        subject_result = await db.execute(subject_query)
        subject_stats = {row.subject: row.count for row in subject_result if row.subject}

        stats = {
            "total_questions": question_stats.total or 0,
            "correct_count": question_stats.correct or 0,
            "correct_rate": (question_stats.correct or 0) / max(question_stats.total or 1, 1),
            "total_chats": chat_count,
            "subject_stats": subject_stats
        }

        # 缓存结果
        await redis_client.set(cache_key, stats, settings.CACHE_USER_STATS_TTL)

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=LearningReport)
async def analyze_learning(
    records: List[QuestionRecordInput],
    db: AsyncSession = Depends(get_db)
):
    """
    分析学习记录，生成个性化学习报告

    功能：
    - 精准定位知识漏洞
    - 生成个性化总结报告
    - 提供强化练习建议
    """
    try:
        if not records:
            # 如果没有传入记录，从数据库获取
            query = select(QuestionRecord).order_by(QuestionRecord.created_at.desc()).limit(50)
            result = await db.execute(query)
            db_records = result.scalars().all()

            records = [
                QuestionRecordInput(
                    question_text=r.question_text or "",
                    subject=r.subject or "未知",
                    knowledge_points=r.knowledge_points or [],
                    success=r.success,
                    timestamp=r.created_at.isoformat() if r.created_at else ""
                )
                for r in db_records
            ]

        # 构建分析提示词
        records_summary = []
        for r in records:
            records_summary.append({
                "题目": r.question_text[:50] if r.question_text else "",
                "学科": r.subject,
                "知识点": r.knowledge_points,
                "是否正确": r.success,
                "时间": r.timestamp
            })

        prompt = f"""请根据以下学习记录，进行深度分析并生成个性化学习报告。

学习记录：
{json.dumps(records_summary, ensure_ascii=False, indent=2)}

请严格按照以下JSON格式返回分析结果：
{{
    "total_questions": 总题目数量,
    "correct_rate": 正确率(0-1),
    "subjects": {{"数学": 数量, "物理": 数量, ...}},
    "weak_points": [
        {{"知识点": "xxx", "错误次数": n, "建议": "针对性练习建议"}}
    ],
    "strong_points": ["掌握较好的知识点列表"],
    "recommendations": ["整体学习建议1", "整体学习建议2"],
    "practice_suggestions": [
        {{"知识点": "xxx", "题目类型": "xxx", "难度": "简单/中等/困难", "数量": 10}}
    ]
}}"""

        result_text = call_spark_lite_api(prompt)

        # 解析JSON
        report_data = parse_json_response(result_text)
        if report_data:
            return LearningReport(**report_data)

        # 返回基于记录的默认报告
        total = len(records)
        correct = sum(1 for r in records if r.success)
        subjects = {}
        for r in records:
            subjects[r.subject] = subjects.get(r.subject, 0) + 1

        return LearningReport(
            total_questions=total,
            correct_rate=correct / max(total, 1),
            subjects=subjects,
            weak_points=[],
            strong_points=[],
            recommendations=["请继续努力学习"],
            practice_suggestions=[]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan", response_model=StudyPlan)
async def generate_study_plan(
    weak_points: List[str],
    strong_points: List[str],
    available_hours: int,
    goal: str
):
    """
    智能生成动态学习计划

    功能：
    - 根据学习进度与能力生成计划
    - 确保学习连贯性
    - 设置里程碑目标
    """
    try:
        prompt = f"""请根据以下信息，生成一个智能动态学习计划。

知识薄弱点：{weak_points}
知识强项：{strong_points}
每日可用学习时间：{available_hours}小时
学习目标：{goal}

请严格按照以下JSON格式返回学习计划：
{{
    "daily_goals": [
        {{"时间": "09:00-10:00", "内容": "学习内容", "知识点": "xxx"}}
    ],
    "weekly_plan": [
        {{"周一": "内容", "周二": "内容", ...}}
    ],
    "focus_areas": ["本周重点攻克的知识点"],
    "timeline": "预计完成时间",
    "milestones": [
        {{"阶段": "第一阶段", "目标": "xxx", "时间": "第1周"}}
    ]
}}"""

        result_text = call_spark_lite_api(prompt)

        plan_data = parse_json_response(result_text)
        if plan_data:
            return StudyPlan(**plan_data)

        return StudyPlan(
            daily_goals=[],
            weekly_plan=[],
            focus_areas=weak_points,
            timeline="1个月",
            milestones=[]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "spark_lite_configured": bool(settings.SPARK_LITE_APP_ID and settings.SPARK_LITE_API_KEY and settings.SPARK_LITE_API_SECRET),
        "spark_pro_configured": bool(settings.SPARK_APP_ID and settings.SPARK_API_KEY and settings.SPARK_API_SECRET),
        "model_version": "lite (chat) / v3.0 (question)"
    }
