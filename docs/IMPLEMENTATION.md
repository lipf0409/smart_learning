# 智能学习系统实现文档

> 更新日期: 2026-05-07
> 版本: v2.1.0

---

## 1. 系统概述

智能学习系统是一个基于 AI 技术的智能学习辅助平台，提供坐姿检测、拍照搜题、AI启发式答疑、学习分析等功能。本次更新主要优化了前端界面，添加了数据可视化图表，并实现了用户密码加密功能。

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     前端 (Vue3 + TypeScript)                     │
│                     http://localhost:5173                       │
│                     ECharts 数据可视化                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌───────────────────┐  ┌───────────────┐  ┌───────────────────┐
│   AI Service      │  │   Backend     │  │   讯飞开放平台     │
│   (Python)        │  │   (Java)      │  │                   │
│   :8000           │  │   :8080       │  │  - 星火大模型     │
│                   │  │               │  │  - OCR识别        │
│                   │  │ bcrypt加密    │  │                   │
└───────────────────┘  └───────────────┘  └───────────────────┘
         │                    │
         ▼                    ▼
┌───────────────────┐  ┌───────────────┐
│   MySQL           │  │   Redis       │
│   :3306           │  │   :6379       │
└───────────────────┘  └───────────────┘
```

---

## 2. 功能模块

### 2.1 前端功能模块

| 模块 | 路由 | 功能描述 | 图表支持 |
|------|------|----------|----------|
| 首页 | `/` | 项目介绍、今日学习概览、本周进度 | 环形图 |
| AI答疑 | `/chat` | 启发式AI答疑，多学科支持 | - |
| 学习报告 | `/report` | 学习数据分析、知识漏洞定位 | 折线图、饼图、柱状图、雷达图 |
| 学习计划 | `/plan` | 智能生成学习计划、进度追踪 | 甘特图 |
| 拍照搜题 | `/question` | OCR识别、AI解题 | - |
| 坐姿检测 | `/posture` | 实时坐姿监测 | - |
| 管理后台 | `/admin` | 用户管理、系统统计 | 折线图、饼图、柱状图 |

### 2.2 后端功能模块

| 模块 | 端点 | 功能描述 |
|------|------|----------|
| 用户认证 | `/api/auth` | 注册、登录、密码修改（bcrypt加密） |
| 用户管理 | `/api/admin/users` | 用户CRUD、状态管理 |
| 统计数据 | `/api/admin/stats` | 系统统计数据接口 |
| AI服务 | `/api/learning` | AI答疑、学习分析 |
| 坐姿检测 | `/api/posture` | 实时坐姿检测 |
| 拍照搜题 | `/api/question` | OCR识别、AI解题 |

---

## 3. 技术实现

### 3.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5.x | 前端框架 |
| TypeScript | 6.0.x | 类型支持 |
| Element Plus | 2.13.x | UI组件库 |
| ECharts | 5.x | 数据可视化 |
| Vue Router | 4.x | 路由管理 |
| Pinia | 3.x | 状态管理 |
| Axios | 1.x | HTTP请求 |
| Vite | 8.x | 构建工具 |

### 3.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Spring Boot | 3.2.x | 后端框架 |
| Spring Data JPA | - | 数据持久化 |
| Spring Security Crypto | - | 密码加密 |
| MySQL | 8.0 | 关系数据库 |
| Redis | 5.0+ | 缓存 |
| Python FastAPI | 0.100+ | AI服务 |

### 3.3 密码加密实现

使用 bcrypt 算法进行密码哈希加密，应用级盐值 "556920ly" 提供额外安全层。

```java
@Service
public class PasswordService {
    private static final String APP_SALT = "556920ly";
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public String encode(String rawPassword) {
        return encoder.encode(rawPassword + APP_SALT);
    }

    public boolean matches(String rawPassword, String encodedPassword) {
        return encoder.matches(rawPassword + APP_SALT, encodedPassword);
    }
}
```

---

## 4. 图表组件

### 4.1 图表组件列表

| 组件名 | 文件路径 | 用途 |
|--------|----------|------|
| LineChart | `components/charts/LineChart.vue` | 折线图，展示趋势数据 |
| PieChart | `components/charts/PieChart.vue` | 饼图，展示占比分布 |
| BarChart | `components/charts/BarChart.vue` | 柱状图，展示对比数据 |
| RadarChart | `components/charts/RadarChart.vue` | 雷达图，展示多维数据 |

### 4.2 图表使用示例

```vue
<template>
  <LineChart
    :data="progressData"
    height="280px"
    color="#3B82F6"
  />
</template>

<script setup>
import { LineChart } from '@/components/charts'

const progressData = ref([
  { date: '5/1', value: 2.5 },
  { date: '5/2', value: 3.0 },
  // ...
])
</script>
```

---

## 5. 配色方案

### 5.1 主色调

| 颜色名称 | 色值 | 用途 |
|----------|------|------|
| 主色蓝 | #3B82F6 | 主要按钮、强调元素 |
| 主色深蓝 | #1D4ED8 | 悬停状态、渐变终点 |
| 辅助紫 | #8B5CF6 | 渐变、装饰元素 |
| 成功绿 | #10B981 | 成功状态、正向数据 |
| 警告橙 | #F59E0B | 警告状态、中性数据 |
| 危险红 | #EF4444 | 错误状态、负向数据 |
| 青色 | #06B6D4 | 装饰元素 |

### 5.2 渐变色

```css
--gradient-blue: linear-gradient(135deg, #3B82F6, #1D4ED8);
--gradient-purple: linear-gradient(135deg, #8B5CF6, #6D28D9);
--gradient-green: linear-gradient(135deg, #10B981, #059669);
--gradient-orange: linear-gradient(135deg, #F59E0B, #D97706);
--gradient-mixed: linear-gradient(135deg, #3B82F6, #8B5CF6, #EC4899);
```

---

## 6. API 接口

### 6.1 认证接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册（密码bcrypt加密） |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/logout` | POST | 用户登出 |
| `/api/auth/change-password` | POST | 修改密码 |

### 6.2 管理员接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/stats/overview` | GET | 系统总览统计 |
| `/api/admin/stats/dau` | GET | 用户活跃度趋势 |
| `/api/admin/stats/subjects` | GET | 学科使用分布 |
| `/api/admin/stats/weekly` | GET | 每周访问量 |
| `/api/admin/stats/growth` | GET | 用户增长趋势 |
| `/api/admin/users` | GET | 用户列表 |
| `/api/admin/users/{id}/status` | PUT | 更新用户状态 |

---

## 7. 目录结构

```
smart_learning/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/                # API 接口
│   │   ├── components/
│   │   │   ├── charts/         # 图表组件 (新增)
│   │   │   │   ├── LineChart.vue
│   │   │   │   ├── PieChart.vue
│   │   │   │   ├── BarChart.vue
│   │   │   │   ├── RadarChart.vue
│   │   │   │   └── index.ts
│   │   │   └── Navbar.vue
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue        # 首页 (优化)
│   │   │   ├── Report.vue      # 学习报告 (优化)
│   │   │   ├── Plan.vue        # 学习计划 (优化)
│   │   │   ├── Admin.vue       # 管理后台 (优化)
│   │   │   ├── Chat.vue
│   │   │   ├── Question.vue
│   │   │   ├── Posture.vue
│   │   │   └── Login.vue
│   │   ├── stores/             # 状态管理
│   │   ├── router/             # 路由配置
│   │   ├── style.css           # 全局样式 (优化)
│   │   └── main.ts
│   └── package.json
│
├── backend/                     # Java 后端
│   └── src/main/java/com/smartlearning/
│       ├── controller/
│       │   ├── AuthController.java    # 认证控制器 (更新)
│       │   └── AdminController.java   # 管理控制器 (更新)
│       ├── service/
│       │   └── PasswordService.java   # 密码服务 (新增)
│       ├── entity/
│       ├── repository/
│       └── config/
│
├── ai-service/                  # Python AI 服务
│   └── app/
│       ├── routers/
│       ├── services/
│       └── models/
│
└── docs/
    └── superpowers/specs/
        └── 2026-05-07-frontend-optimization-design.md
```

---

## 8. 更新日志

### v2.1.0 (2026-05-07)

#### 新增功能
- ✅ ECharts 数据可视化图表组件
- ✅ 首页学习概览卡片和本周进度环形图
- ✅ 学习报告页 4 种图表（折线图、饼图、柱状图、雷达图）
- ✅ 学习计划页甘特图进度展示
- ✅ 管理员页面统计图表
- ✅ bcrypt 密码加密服务

#### 优化改进
- ✅ 全新配色方案，增强对比度和视觉层次
- ✅ 使用 Element Plus 内置图标替换卡通图标
- ✅ 导航栏毛玻璃效果和渐变设计
- ✅ 卡片悬停动画和过渡效果
- ✅ 响应式布局优化

#### 删除内容
- ✅ 删除无用测试脚本 `test_ws.py`、`test_font.py`

---

## 9. 部署说明

### 9.1 前端部署

```bash
cd frontend
npm install
npm run build
# 生成 dist 目录，部署到静态服务器
```

### 9.2 后端部署

```bash
cd backend
./mvnw clean package
java -jar target/smart-learning-backend-1.0.0.jar
```

### 9.3 AI 服务部署

```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 10. 开发指南

### 10.1 添加新图表

1. 在 `frontend/src/components/charts/` 创建图表组件
2. 参考 ECharts 文档配置图表选项
3. 在 `index.ts` 中导出组件
4. 在页面中引入并使用

### 10.2 添加新 API 接口

1. 在 `backend` 创建 Entity、Repository
2. 创建 Service 处理业务逻辑
3. 创建 Controller 暴露 REST 接口
4. 在前端 `api/index.ts` 添加调用方法

---

## 许可证

MIT License
