# 智能学习系统 AI 服务

基于 FastAPI 的智能学习系统 AI 服务模块，提供坐姿检测、拍照搜题、AI答疑、学习分析等功能。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue3 + TypeScript)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Service (FastAPI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 坐姿检测    │  │ 拍照搜题    │  │ AI答疑      │            │
│  │ Posture     │  │ Question    │  │ Chat        │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 学习分析    │  │ 学习计划    │  │ RAG服务     │            │
│  │ Analyze     │  │ Plan        │  │ (预留)      │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   MySQL     │      │   Redis     │      │  讯飞星火   │
│   数据库    │      │   缓存      │      │  AI API     │
└─────────────┘      └─────────────┘      └─────────────┘
```

## 功能模块

### 1. 坐姿检测 (Posture Detection)
- 基于 MobileNetV3-Small 轻量级模型
- 6通道双视角输入，提高检测准确率
- 实时检测坐姿状态（良好/不良）

### 2. 拍照搜题 (Question Solving)
- 讯飞 OCR 文字识别（支持印刷体和手写体）
- 讯飞星火大模型智能解答
- 提供详细解题步骤和知识点讲解
- 自动保存搜题记录到数据库

### 3. AI启发式答疑 (AI Chat)
- 启发式引导思考，不直接给出答案
- 支持多学科（数学、物理、化学、语文、英语）
- 结构化响应解析，适配星火Lite模型
- Redis缓存加速，相同问题秒回复
- 对话记录持久化存储

### 4. 学习分析与报告 (Learning Analysis)
- 基于真实学习数据生成报告
- 精准定位知识漏洞
- 个性化学习建议
- 学科分布统计

### 5. 智能学习计划 (Study Plan)
- 根据薄弱点和强项生成计划
- 动态调整学习安排
- 设置里程碑目标

### 6. RAG知识库 (预留)
- 抽象接口设计，支持未来扩展
- 可接入 Milvus、Pinecone 等向量数据库
- 知识检索增强生成

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| Web框架 | FastAPI | >=0.100.0 |
| ORM | SQLAlchemy | >=2.0.0 |
| 数据库 | MySQL | 8.0 |
| 缓存 | Redis | >=5.0.0 |
| AI模型 | 讯飞星火 | Lite |
| OCR | 讯飞OCR | - |
| 坐姿检测 | PyTorch + MobileNetV3 | >=2.0.0 |

## 目录结构

```
ai-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── redis_client.py      # Redis客户端
│   │
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── question_record.py
│   │   ├── chat_record.py
│   │   ├── learning_stats.py
│   │   └── knowledge_base.py
│   │
│   ├── routers/             # API路由
│   │   ├── __init__.py
│   │   ├── posture.py
│   │   ├── question.py
│   │   ├── learning.py
│   │   └── rag.py
│   │
│   └── services/            # 业务服务
│       ├── __init__.py
│       └── rag_service.py
│
├── weights/                 # 模型权重
│   └── best_fold4.pth
│
├── .env                     # 环境变量
├── requirements.txt         # 依赖列表
├── CONFIG.md               # 配置说明
└── README.md               # 本文档
```

## 快速开始

### 1. 环境准备

```bash
# 创建conda环境
conda create -n smart_learning python=3.10
conda activate smart_learning

# 安装依赖
cd ai-service
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件：

```env
# 讯飞星火API
SPARK_APP_ID=your_app_id
SPARK_API_KEY=your_api_key
SPARK_API_SECRET=your_api_secret
SPARK_MODEL_VERSION=lite

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=smart_learning

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 创建数据库

```sql
CREATE DATABASE smart_learning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动服务

```bash
# 启动MySQL和Redis服务
# Windows: 通过服务管理器启动
# Linux: sudo systemctl start mysql redis

# 启动AI服务
uvicorn app.main:app --reload --port 8000
```

### 5. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 查看API文档
# 浏览器访问 http://localhost:8000/docs
```

## API 接口

### 坐姿检测
```
POST /api/posture/detect
Content-Type: multipart/form-data

Request: file (图片文件)
Response: { status: "good"|"bad", confidence: 0.95, message: "..." }
```

### 拍照搜题
```
POST /api/question/solve
Content-Type: multipart/form-data

Request: file (题目图片)
Response: {
  question_text: "题目内容",
  answer: "答案",
  steps: ["步骤1", "步骤2"],
  knowledge_points: ["知识点"],
  success: true
}
```

### AI答疑
```
POST /api/learning/chat
Content-Type: application/x-www-form-urlencoded

Request: question=问题&subject=学科
Response: {
  response: "AI回复",
  hints: ["提示1", "提示2"],
  related_knowledge: ["知识点1", "知识点2"]
}
```

### 学习统计
```
GET /api/learning/stats

Response: {
  total_questions: 50,
  correct_count: 40,
  correct_rate: 0.8,
  total_chats: 100,
  subject_stats: {"数学": 20, "物理": 15}
}
```

### 学习报告
```
POST /api/learning/analyze

Request: [{ question_text, subject, knowledge_points, success, timestamp }]
Response: {
  total_questions: 50,
  correct_rate: 0.72,
  subjects: {"数学": 25},
  weak_points: [{"知识点": "三角函数", "错误次数": 5}],
  strong_points: ["方程求解"],
  recommendations: ["建议1"]
}
```

### 学习计划
```
POST /api/learning/plan

Request: weak_points, strong_points, available_hours, goal
Response: {
  daily_goals: [...],
  weekly_plan: [...],
  focus_areas: [...],
  timeline: "1个月",
  milestones: [...]
}
```

### RAG知识库 (预留)
```
GET /api/rag/search?query=查询内容

POST /api/rag/knowledge
Request: { title, content, subject }
```

## 数据库设计

### t_question_record (搜题记录)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| question_text | TEXT | 题目内容 |
| answer | TEXT | 答案 |
| steps | JSON | 解题步骤 |
| knowledge_points | JSON | 知识点 |
| subject | VARCHAR(50) | 学科 |
| success | BOOLEAN | 是否成功 |
| created_at | DATETIME | 创建时间 |

### t_chat_record (AI答疑记录)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| session_id | VARCHAR(100) | 会话ID |
| role | VARCHAR(20) | 角色 |
| question | TEXT | 问题 |
| response | TEXT | 回复 |
| hints | JSON | 提示 |
| related_knowledge | JSON | 知识点 |
| subject | VARCHAR(50) | 学科 |
| created_at | DATETIME | 创建时间 |

### t_learning_stats (学习统计)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| total_questions | INT | 总解题数 |
| correct_count | INT | 正确数 |
| subject_stats | JSON | 学科统计 |
| knowledge_stats | JSON | 知识点统计 |
| streak_days | INT | 连续天数 |

### t_knowledge_base (RAG知识库)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| title | VARCHAR(200) | 标题 |
| content | TEXT | 内容 |
| subject | VARCHAR(50) | 学科 |
| vector_id | VARCHAR(100) | 向量ID(预留) |

## Redis缓存策略

| 缓存Key | TTL | 说明 |
|---------|-----|------|
| ai:response:{hash} | 24h | AI回答缓存 |
| report:user:{id} | 1h | 学习报告缓存 |
| stats:user:{id} | 5min | 用户统计缓存 |

## 讯飞星火模型版本

| 版本 | URL | Domain | 说明 |
|------|-----|--------|------|
| lite | v1.1/chat | general | Lite版本，性价比高 |
| v3.5 | v3.5/chat | generalv3.5 | 推荐版本，多模态 |
| v4.0 | v4.0/chat | 4.0Ultra | 最新版本 |

## 注意事项

1. **API配额**：讯飞星火API需要付费，请确保账户有余额
2. **模型选择**：Lite版本性价比高，适合大量调用
3. **缓存利用**：相同问题会使用缓存，减少API调用
4. **数据库连接**：首次启动会自动创建表结构
5. **Redis可选**：如果Redis未启动，服务仍可运行，只是没有缓存

## 更新日志

### v2.0.0 (2026-05-05)
- 新增MySQL数据库支持，存储学习记录
- 新增Redis缓存机制，加速AI响应
- 修复AI答疑返回固定文本的问题
- 优化Prompt设计，适配星火Lite模型
- 新增RAG知识库预留接口
- 新增学习统计API
- 更新前端调用真实API

### v1.1.0
- 初始版本
- 坐姿检测、拍照搜题、AI答疑功能
