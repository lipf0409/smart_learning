# 智能学习系统技术文档

## 项目概述

智能学习系统是一个基于AI的综合性学习辅助平台，集成了坐姿检测、拍照搜题、AI答疑、学习报告、学习计划等功能。系统采用前后端分离架构，包含三个核心服务：

- **前端服务 (Frontend)**: Vue 3 + TypeScript + Element Plus
- **后端服务 (Backend)**: Spring Boot 3 + MySQL
- **AI服务 (AI Service)**: FastAPI + 讯飞星火大模型

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户浏览器                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    前端服务 (Vue 3 + Nginx)                      │
│                      端口: 80/443                                │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌───────────────────────────────┐   ┌─────────────────────────────┐
│   后端服务 (Spring Boot 3)     │   │   AI服务 (FastAPI)          │
│   端口: 8080                   │   │   端口: 8000                │
│   - 用户认证                   │   │   - 坐姿检测                │
│   - 用户管理                   │   │   - 拍照搜题                │
│   - 数据存储                   │   │   - AI答疑                  │
└───────────────────────────────┘   │   - 学习分析                │
            │                       └─────────────────────────────┘
            ▼                                   │
┌───────────────────────────────┐               │
│        MySQL 数据库            │               ▼
│        端口: 3306              │   ┌─────────────────────────────┐
│   - 用户数据                   │   │   Redis 缓存                │
│   - 学习记录                   │   │   端口: 6379                │
└───────────────────────────────┘   └─────────────────────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────────────┐
                                    │   讯飞星火大模型 API         │
                                    │   - 多模态识别              │
                                    │   - 自然语言处理            │
                                    └─────────────────────────────┘
```

## 技术栈详情

### 1. 前端服务 (Frontend)

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.5.x | 前端框架 |
| TypeScript | 6.0.x | 类型安全 |
| Vite | 8.0.x | 构建工具 |
| Element Plus | 2.13.x | UI组件库 |
| Vue Router | 4.6.x | 路由管理 |
| Pinia | 3.0.x | 状态管理 |
| Axios | 1.15.x | HTTP客户端 |
| ECharts | 6.0.x | 数据可视化 |

**目录结构：**
```
frontend/
├── src/
│   ├── api/           # API接口封装
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   │   └── charts/    # 图表组件
│   ├── router/        # 路由配置
│   ├── stores/        # Pinia状态管理
│   ├── views/         # 页面组件
│   │   ├── Home.vue       # 首页
│   │   ├── Login.vue      # 登录/注册
│   │   ├── Posture.vue    # 坐姿检测
│   │   ├── Question.vue   # 拍照搜题
│   │   ├── Chat.vue       # AI答疑
│   │   ├── Report.vue     # 学习报告
│   │   ├── Plan.vue       # 学习计划
│   │   └── Admin.vue      # 管理后台
│   ├── App.vue        # 根组件
│   ├── main.ts        # 入口文件
│   └── style.css      # 全局样式
├── public/            # 公共资源
├── index.html         # HTML模板
├── vite.config.ts     # Vite配置
└── package.json       # 依赖配置
```

### 2. 后端服务 (Backend)

| 技术 | 版本 | 用途 |
|------|------|------|
| Java | 21 | 编程语言 |
| Spring Boot | 3.2.5 | 后端框架 |
| Spring Data JPA | - | 数据持久化 |
| MySQL | 8.0+ | 关系数据库 |
| BCrypt | - | 密码加密 |
| Lombok | - | 代码简化 |

**目录结构：**
```
backend/
├── src/main/java/com/smartlearning/
│   ├── config/            # 配置类
│   │   ├── WebConfig.java         # Web配置
│   │   └── DataInitializer.java   # 数据初始化
│   ├── controller/        # 控制器
│   │   ├── AuthController.java    # 认证接口
│   │   ├── AdminController.java   # 管理接口
│   │   ├── PostureController.java # 坐姿接口
│   │   └── QuestionController.java# 题目接口
│   ├── entity/            # 实体类
│   │   ├── User.java             # 用户实体
│   │   ├── PostureRecord.java    # 坐姿记录
│   │   └── QuestionRecord.java   # 题目记录
│   ├── repository/        # 数据访问层
│   ├── service/           # 业务逻辑层
│   │   ├── PasswordService.java  # 密码服务
│   │   └── AiService.java        # AI服务调用
│   └── SmartLearningApplication.java  # 启动类
├── src/main/resources/
│   └── application.yml    # 应用配置
└── pom.xml               # Maven配置
```

### 3. AI服务 (AI Service)

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 编程语言 |
| FastAPI | 0.100+ | Web框架 |
| Uvicorn | 0.23+ | ASGI服务器 |
| OpenCV | 4.8+ | 图像处理 |
| MediaPipe | 0.10+ | 姿态估计 |
| 讯飞星火 | v3.5/v4.0 | 大语言模型 |
| Redis | 5.0+ | 缓存服务 |
| SQLAlchemy | 2.0+ | ORM框架 |

**目录结构：**
```
ai-service/
├── app/
│   ├── main.py            # 应用入口
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── redis_client.py    # Redis客户端
│   ├── routers/           # 路由模块
│   │   ├── posture.py     # 坐姿检测
│   │   ├── question.py    # 拍照搜题
│   │   ├── learning.py    # 学习分析
│   │   └── rag.py         # 知识库检索
│   └── services/          # 业务服务
│       ├── spark_api.py   # 星火API封装
│       └── pose_service.py# 姿态检测服务
├── weights/               # 模型权重
├── scripts/               # 脚本文件
├── .env                   # 环境变量
├── requirements.txt       # Python依赖
└── CONFIG.md             # 配置说明
```

## 核心功能模块

### 1. 用户认证模块

**功能描述：**
- 用户注册/登录
- 密码BCrypt加密（应用级盐值）
- Token认证
- 角色权限管理（user/admin）

**API接口：**
```
POST /api/auth/register  - 用户注册
POST /api/auth/login     - 用户登录
POST /api/auth/logout    - 用户登出
POST /api/auth/change-password - 修改密码
```

### 2. 坐姿检测模块

**功能描述：**
- 基于MediaPipe的姿态估计
- 实时WebSocket视频流处理
- 检测耸肩、低头、歪头等不良坐姿
- 历史记录与统计

**API接口：**
```
POST /api/posture/detect     - 单次检测
WebSocket /api/posture/stream - 实时检测流
GET  /api/posture/records    - 获取记录
```

### 3. 拍照搜题模块

**功能描述：**
- 图片OCR识别
- 讯飞星火多模态理解
- 分步骤解题
- 知识点提取

**API接口：**
```
POST /api/question/solve     - 解题请求
GET  /api/question/records   - 历史记录
```

### 4. AI答疑模块

**功能描述：**
- 启发式教学对话
- 多学科支持
- 上下文记忆
- 知识点推荐

**API接口：**
```
POST /api/learning/chat      - AI对话
GET  /api/learning/records   - 对话记录
```

### 5. 学习报告模块

**功能描述：**
- 学习数据统计
- 知识点掌握分析
- 可视化图表展示
- 学习建议生成

**API接口：**
```
GET  /api/learning/stats     - 学习统计
POST /api/learning/analyze   - 生成报告
```

### 6. 学习计划模块

**功能描述：**
- 智能计划生成
- 薄弱点分析
- 时间规划
- 进度跟踪

**API接口：**
```
POST /api/learning/plan      - 生成计划
```

### 7. 管理后台模块

**功能描述：**
- 用户管理
- 数据统计
- 系统监控

**API接口：**
```
GET  /api/admin/users        - 用户列表
GET  /api/admin/stats/overview - 系统概览
GET  /api/admin/stats/dau    - 日活统计
```

## 数据库设计

### 用户表 (t_user)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| username | VARCHAR(50) | 用户名 |
| password | VARCHAR(255) | 密码(BCrypt) |
| email | VARCHAR(100) | 邮箱 |
| avatar | VARCHAR(255) | 头像 |
| role | VARCHAR(20) | 角色(user/admin) |
| status | VARCHAR(20) | 状态(active/disabled) |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 坐姿记录表 (t_posture_record)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| status | VARCHAR(20) | 检测状态 |
| gesture_type | VARCHAR(100) | 姿态类型 |
| confidence | DECIMAL | 置信度 |
| created_at | DATETIME | 创建时间 |

### 题目记录表 (t_question_record)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| question_text | TEXT | 题目内容 |
| answer | TEXT | 答案 |
| subject | VARCHAR(50) | 学科 |
| success | BOOLEAN | 是否成功 |
| created_at | DATETIME | 创建时间 |

## 安全设计

### 密码安全
- BCrypt加密算法（工作因子12）
- 应用级盐值 "556920ly"
- 密码最小长度6位

### 认证授权
- Token认证机制
- 路由守卫保护
- 角色权限控制

### CORS配置
- 允许指定源访问
- 支持凭证传递
- 预检请求缓存

## 性能优化

### 前端优化
- Vite代码分割
- 依赖预构建
- 图标本地化
- 路由懒加载

### 后端优化
- 数据库连接池(HikariCP)
- JPA懒加载
- 接口缓存

### AI服务优化
- Redis缓存
- 异步处理
- 模型预加载

## 环境要求

### 开发环境
- Node.js 18+
- Java 21
- Python 3.10+
- MySQL 8.0+
- Redis 7.0+

### 生产环境
- Docker 24.0+
- Docker Compose 2.0+
- 阿里云服务器 (推荐2核4G以上)
