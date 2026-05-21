# 智能学习系统

一个基于AI的综合性学习辅助平台，集成了坐姿检测、拍照搜题、AI答疑、学习报告、学习计划等功能。

## 功能特性

- 🎯 **坐姿检测**: 基于MediaPipe的实时姿态估计，检测不良坐姿
- 📸 **拍照搜题**: 讯飞星火多模态识别，分步骤解题
- 🤖 **AI答疑**: 启发式教学对话，多学科支持
- 📊 **学习报告**: 数据可视化，知识点掌握分析
- 📅 **学习计划**: 智能生成个性化学习计划
- 👨‍💼 **管理后台**: 用户管理，数据统计

## 技术栈

| 服务 | 技术栈 |
|------|--------|
| 前端 | Vue 3 + TypeScript + Element Plus + ECharts |
| 后端 | Spring Boot 3 + MySQL + BCrypt |
| AI服务 | FastAPI + 讯飞星火大模型 + MediaPipe |
| 缓存 | Redis |
| 部署 | Docker + Docker Compose + Nginx |

## 项目结构

```
smart_learning/
├── frontend/           # 前端服务
├── backend/            # 后端服务
├── ai-service/         # AI服务
├── docker/             # Docker配置
│   ├── nginx/         # Nginx配置
│   └── mysql/         # MySQL初始化脚本
├── docs/              # 文档
│   ├── TECHNICAL_DOCUMENTATION.md  # 技术文档
│   └── DEPLOYMENT_GUIDE.md        # 部署文档
├── docker-compose.yml  # Docker编排配置
└── .env.example        # 环境变量示例
```

## 快速开始

### 环境要求

- Docker 24.0+
- Docker Compose 2.0+
- 讯飞星火API凭证

### 部署步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd smart_learning
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填写讯飞星火API配置
```

3. **启动服务**
```bash
docker-compose up -d --build
```

4. **访问应用**
- 前端: http://localhost
- 后端API: http://localhost:8080
- AI服务: http://localhost:8000

### 默认账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
|  | admin123 | 管理员 |

> ⚠️ 生产环境请务必修改默认密码

## 文档

- [技术文档](docs/TECHNICAL_DOCUMENTATION.md)
- [部署文档](docs/DEPLOYMENT_GUIDE.md)
- [AI服务配置](ai-service/CONFIG.md)

## 开发

### 本地开发

```bash
# 前端
cd frontend
npm install
npm run dev

# 后端
cd backend
mvn spring-boot:run

# AI服务
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 构建生产版本

```bash
# 前端
cd frontend
npm run build

# 后端
cd backend
mvn package -DskipTests

# AI服务
cd ai-service
# Docker构建
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
