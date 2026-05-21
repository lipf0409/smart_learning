# Question Solving Service (Xunfei OCR + Spark AI Integration)
import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from urllib.parse import urlencode, quote
import websocket
import requests
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import ssl
import threading

router = APIRouter(prefix="/api/question", tags=["question"])

# ============ 讯飞API配置 ============
# 星火大模型
SPARK_APP_ID = os.getenv("SPARK_APP_ID", "")
SPARK_API_KEY = os.getenv("SPARK_API_KEY", "")
SPARK_API_SECRET = os.getenv("SPARK_API_SECRET", "")
SPARK_MODEL_VERSION = os.getenv("SPARK_MODEL_VERSION", "v3.0")

# 通用文字识别 OCR
OCR_APP_ID = os.getenv("OCR_APP_ID", "")
OCR_API_KEY = os.getenv("OCR_API_KEY", "")
OCR_API_SECRET = os.getenv("OCR_API_SECRET", "")

# 手写文字识别 OCR
OCR_HANDWRITING_APP_ID = os.getenv("OCR_HANDWRITING_APP_ID", "")
OCR_HANDWRITING_API_KEY = os.getenv("OCR_HANDWRITING_API_KEY", "")

class AnswerResult(BaseModel):
    question_text: str
    answer: str
    steps: List[str]
    knowledge_points: List[str]
    success: bool
    error: Optional[str] = None
    provider: str = "xunfei"

# ============ OCR 文字识别 (官方示例方式) ============

def assemble_ws_auth_url(request_url, method="POST", api_key="", api_secret=""):
    """生成鉴权URL - 按官方示例"""
    # 解析URL
    stidx = request_url.index("://")
    host = request_url[stidx + 3:]
    schema = request_url[:stidx + 3]
    edidx = host.index("/")
    path = host[edidx:]
    host = host[:edidx]

    # 生成日期
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 生成签名原文
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)

    # 计算签名
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

    # 生成authorization
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

    # 拼接URL
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return request_url + "?" + urlencode(values)


def ocr_general(image_base64: str) -> str:
    """
    通用文字识别 - 按官方示例格式
    """
    url = 'https://api.xf-yun.com/v1/private/sf8e6aca1'

    # 按官方示例构建请求体
    body = {
        "header": {
            "app_id": OCR_APP_ID,
            "status": 3
        },
        "parameter": {
            "sf8e6aca1": {
                "category": "ch_en_public_cloud",
                "result": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "json"
                }
            }
        },
        "payload": {
            "sf8e6aca1_data_1": {
                "encoding": "jpg",
                "image": image_base64,
                "status": 3
            }
        }
    }

    # 生成鉴权URL
    request_url = assemble_ws_auth_url(url, "POST", OCR_API_KEY, OCR_API_SECRET)

    headers = {
        'content-type': "application/json",
        'host': 'api.xf-yun.com',
        'app_id': OCR_APP_ID
    }

    try:
        response = requests.post(request_url, data=json.dumps(body), headers=headers, timeout=30)
        print(f"[OCR] Response status: {response.status_code}")

        result = json.loads(response.content.decode())

        # 检查返回码
        code = result.get("header", {}).get("code", -1)
        if code != 0:
            error_msg = result.get("header", {}).get("message", "Unknown error")
            print(f"[OCR] Error {code}: {error_msg}")
            raise Exception(f"OCR Error {code}: {error_msg}")

        # 解析结果 - 按官方示例，text字段是base64编码的
        text_base64 = result.get('payload', {}).get('result', {}).get('text', '')
        if text_base64:
            final_result = base64.b64decode(text_base64).decode()
            print(f"[OCR] 识别结果: {final_result[:200]}...")
            return final_result
        else:
            print(f"[OCR] 无text字段，完整响应: {json.dumps(result, ensure_ascii=False)[:500]}")
            return ""

    except Exception as e:
        print(f"[OCR] Exception: {str(e)}")
        raise Exception(f"OCR Error: {str(e)}")


def ocr_handwriting(image_base64: str) -> str:
    """手写文字识别"""
    url = "https://webapi.xfyun.cn/v1/service/v1/ocr/handwriting"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "appid": OCR_HANDWRITING_APP_ID
    }

    data = {
        "image": image_base64
    }

    try:
        response = requests.post(url, data=data, headers=headers, timeout=30)
        print(f"[OCR Handwriting] Response: {response.text[:500]}")

        result = response.json()

        if result.get("code", "0") == "0":
            blocks = result.get("data", {}).get("block", [])
            text_lines = []
            for block in blocks:
                lines = block.get("line", [])
                for line in lines:
                    text_lines.append(line.get("word", ""))
            return "\n".join(text_lines)
        else:
            raise Exception(f"OCR Error: {result.get('message', 'Unknown')}")

    except Exception as e:
        raise Exception(f"OCR Handwriting Error: {str(e)}")


# ============ 星火大模型 ============

def create_spark_auth_url(model_version: str = "v3.0") -> tuple:
    """生成星火API鉴权URL"""
    version_config = {
        "lite": ("wss://spark-api.xf-yun.com/v1.1/chat", "/v1.1/chat", "general"),
        "v1.5": ("wss://spark-api.xf-yun.com/v1.1/chat", "/v1.1/chat", "general"),
        "v2.0": ("wss://spark-api.xf-yun.com/v2.1/chat", "/v2.1/chat", "generalv2"),
        "v3.0": ("wss://spark-api.xf-yun.com/v3.1/chat", "/v3.1/chat", "generalv3"),
        "v3.5": ("wss://spark-api.xf-yun.com/v3.5/chat", "/v3.5/chat", "generalv3.5"),
        "v4.0": ("wss://spark-api.xf-yun.com/v4.0/chat", "/v4.0/chat", "4.0Ultra"),
    }

    host = "spark-api.xf-yun.com"
    base_url, path, domain = version_config.get(model_version, version_config["v3.0"])

    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

    signature_sha = hmac.new(
        SPARK_API_SECRET.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    signature = base64.b64encode(signature_sha).decode('utf-8')

    authorization_origin = (
        f'api_key="{SPARK_API_KEY}", '
        f'algorithm="hmac-sha256", '
        f'headers="host date request-line", '
        f'signature="{signature}"'
    )

    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

    auth_url = f"{base_url}?authorization={quote(authorization)}&date={quote(date)}&host={host}"

    return auth_url, domain


def call_spark_api(prompt: str) -> str:
    """调用星火大模型API"""
    if not all([SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET]):
        raise ValueError("星火API配置不完整")

    ws_url, domain = create_spark_auth_url(SPARK_MODEL_VERSION)
    print(f"[Spark] 连接URL: {ws_url[:80]}...")
    print(f"[Spark] Domain: {domain}")

    result_text = []
    error_msg = [None]
    ws_ready = threading.Event()

    def on_message(ws, message):
        try:
            data = json.loads(message)
            code = data.get('header', {}).get('code', 0)

            if code != 0:
                error_msg[0] = f"API Error {code}: {data.get('header', {}).get('message', 'Unknown')}"
                print(f"[Spark] 错误: {error_msg[0]}")
                ws.close()
                return

            choices = data.get('payload', {}).get('choices', {})
            text_list = choices.get('text', [])
            if text_list:
                content = text_list[0].get('content', '')
                result_text.append(content)
                print(f"[Spark] 收到内容片段: {content[:100]}...")

            status = data.get('header', {}).get('status', 0)
            print(f"[Spark] 状态: {status}")
            if status == 2:
                ws.close()

        except Exception as e:
            error_msg[0] = str(e)
            print(f"[Spark] 解析异常: {e}")
            ws.close()

    def on_error(ws, error):
        error_msg[0] = str(error)
        print(f"[Spark] WebSocket错误: {error}")
        ws_ready.set()

    def on_close(ws, close_status_code, close_msg):
        print(f"[Spark] 连接关闭")
        ws_ready.set()

    def on_open(ws):
        message = {
            "header": {
                "app_id": SPARK_APP_ID,
                "uid": "user_001"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            }
        }
        print(f"[Spark] 发送消息, 消息长度: {len(prompt)}")
        ws.send(json.dumps(message))
        # 不要在这里设置 ws_ready，等待响应完成

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
    print(f"[Spark] 完整响应长度: {len(result)}")
    return result


def parse_ai_response(content: str) -> dict:
    """解析AI响应，提取JSON"""
    try:
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return None


# ============ API 接口 ============

@router.post("/solve", response_model=AnswerResult)
async def solve_question(file: UploadFile = File(...)):
    """
    拍照搜题接口

    流程: 图片 -> OCR识别文字 -> 星火模型解答 -> 返回结果
    """
    try:
        # 读取图片
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode('UTF-8')

        # 检查API配置
        if not all([SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET]):
            return AnswerResult(
                question_text="[API未配置]",
                answer="",
                steps=["请配置星火API环境变量"],
                knowledge_points=[],
                success=False,
                error="星火API未配置",
                provider="mock"
            )

        # Step 1: OCR识别文字
        question_text = ""
        ocr_method = ""

        # 尝试通用OCR
        try:
            if all([OCR_APP_ID, OCR_API_KEY, OCR_API_SECRET]):
                question_text = ocr_general(image_base64)
                if question_text.strip():
                    ocr_method = "通用OCR"
        except Exception as e:
            print(f"[OCR] 通用OCR失败: {e}")

        # 如果通用OCR失败，尝试手写OCR
        if not question_text.strip():
            try:
                if all([OCR_HANDWRITING_APP_ID, OCR_HANDWRITING_API_KEY]):
                    question_text = ocr_handwriting(image_base64)
                    if question_text.strip():
                        ocr_method = "手写OCR"
            except Exception as e:
                print(f"[OCR] 手写OCR失败: {e}")

        if not question_text.strip():
            question_text = "[OCR未能识别到文字]"
            ocr_method = "无"

        # Step 2: 星火模型解答
        prompt = f"""请解答以下题目，给出详细的解题步骤和答案。

题目内容：
{question_text}

请严格按照以下JSON格式返回结果：
{{
    "question_text": "题目完整内容（整理后的）",
    "answer": "最终答案",
    "steps": ["解题步骤1", "解题步骤2", "解题步骤3"],
    "knowledge_points": ["涉及的知识点1", "涉及的知识点2"]
}}"""

        result_text = call_spark_api(prompt)
        print(f"[Spark] 回答长度: {len(result_text)}")

        # Step 3: 解析结果
        answer_data = parse_ai_response(result_text)

        if answer_data:
            return AnswerResult(
                question_text=answer_data.get("question_text", question_text),
                answer=answer_data.get("answer", ""),
                steps=answer_data.get("steps", []),
                knowledge_points=answer_data.get("knowledge_points", []),
                success=True,
                provider=f"xunfei ({ocr_method} + Spark)"
            )
        else:
            # 无法解析JSON，直接返回原文
            return AnswerResult(
                question_text=question_text,
                answer=result_text,
                steps=[],
                knowledge_points=[],
                success=True,
                provider=f"xunfei ({ocr_method} + Spark)"
            )

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "provider": "xunfei",
        "spark_configured": bool(SPARK_APP_ID and SPARK_API_KEY and SPARK_API_SECRET),
        "ocr_configured": bool(OCR_APP_ID and OCR_API_KEY and OCR_API_SECRET),
        "model_version": SPARK_MODEL_VERSION
    }


@router.get("/config")
async def get_config():
    """获取当前AI配置"""
    return {
        "provider": "xunfei",
        "model_version": SPARK_MODEL_VERSION,
        "spark_configured": bool(SPARK_APP_ID and SPARK_API_KEY and SPARK_API_SECRET),
        "ocr_configured": bool(OCR_APP_ID and OCR_API_KEY and OCR_API_SECRET),
        "ocr_handwriting_configured": bool(OCR_HANDWRITING_APP_ID and OCR_HANDWRITING_API_KEY)
    }