# 智能学习系统前端优化与功能增强设计文档

> 创建日期: 2026-05-07
> 状态: 待审批

---

## 1. 项目概述

### 1.1 背景

智能学习系统是一个基于 AI 技术的学习辅助平台，包含坐姿检测、拍照搜题、AI启发式答疑、学习分析等功能。当前前端界面已有基础功能，但缺乏数据可视化图表，视觉设计也有提升空间。

### 1.2 目标

1. **视觉美化**：优化界面设计，采用清新教育风格，提升用户体验
2. **功能图表**：添加 ECharts 数据可视化图表
   - 前端用户页面：个人学习数据、学习情况图表
   - 后端管理员页面：用户信息、系统使用统计图表
3. **密码加密**：在 Java 后端实现 bcrypt 密码加密，使用 "556920ly" 作为盐值增强

### 1.3 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue3 + TypeScript + Element Plus | 保持现有技术栈 |
| 图表 | ECharts 5.x | 数据可视化 |
| 后端 | Java Spring Boot 3.x | 密码加密实现 |
| 加密 | bcrypt | 密码哈希加密 |

---

## 2. 功能图表设计

### 2.1 前端用户页面图表

#### 2.1.1 首页 (Home.vue)

**新增学习概览区域：**

```
┌─────────────────────────────────────────────────────────────┐
│                    今日学习概览                              │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  学习时长    │  解答题目    │  正确率      │  连续学习天数   │
│   2.5h      │    15题     │   85%       │     7天        │
│  ↑ 较昨日+0.5h │  ↑ +3题   │  ↑ +5%     │  保持连续      │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

- **本周学习进度环形图**：展示本周每日学习时长占比
- **快速入口卡片优化**：添加悬停动画、渐变边框

#### 2.1.2 学习报告页 (Report.vue)

**图表布局：**

```
┌─────────────────────────────────────────────────────────────┐
│                      学习报告                                │
├─────────────────────────────┬───────────────────────────────┤
│  学习进度折线图              │  学科分布饼图                 │
│  (近7天/30天学习时长趋势)    │  (各学科题目占比)             │
├─────────────────────────────┼───────────────────────────────┤
│  正确率趋势柱状图            │  知识掌握雷达图               │
│  (各学科正确率对比)          │  (知识点掌握程度多维展示)     │
└─────────────────────────────┴───────────────────────────────┘
```

**图表详情：**

| 图表名称 | 类型 | 数据来源 | 交互功能 |
|----------|------|----------|----------|
| 学习进度折线图 | Line Chart | `/api/learning/stats` | 时间范围切换(7天/30天) |
| 学科分布饼图 | Pie Chart | `report.subjects` | 悬停显示详情 |
| 正确率柱状图 | Bar Chart | `report.subjects` + 正确率数据 | 点击跳转学科详情 |
| 知识雷达图 | Radar Chart | `report.weak_points` + `report.strong_points` | 无 |

#### 2.1.3 学习计划页 (Plan.vue)

**新增图表：**

- **学习进度甘特图**：展示各知识点学习时间安排
- **里程碑进度条**：可视化展示学习阶段完成情况

#### 2.1.4 AI答疑页 (Chat.vue)

**新增统计卡片：**

- 今日提问次数
- 累计学习知识点数
- 平均响应时间

### 2.2 管理员页面图表 (Admin.vue)

**页面布局：**

```
┌─────────────────────────────────────────────────────────────┐
│                    管理后台仪表盘                            │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│  总用户数    │  今日活跃    │  本周新增    │  系统运行天数   │
│   1,234     │    456      │    28       │     30天       │
└─────────────┴─────────────┴─────────────┴─────────────────┘

┌─────────────────────────────┬───────────────────────────────┐
│  用户活跃度折线图            │  学科使用分布饼图             │
│  (近30天日活趋势)            │  (各学科使用占比)             │
├─────────────────────────────┼───────────────────────────────┤
│  每周访问量柱状图            │  用户增长趋势图               │
│  (周一至周日访问分布)        │  (近6个月用户增长)            │
└─────────────────────────────┴───────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    用户列表管理                              │
│  (搜索、筛选、启用/禁用、查看详情)                           │
└─────────────────────────────────────────────────────────────┘
```

**图表详情：**

| 图表名称 | 类型 | 数据来源 | 刷新频率 |
|----------|------|----------|----------|
| 用户活跃度折线图 | Line Chart | `/api/admin/stats/dau` | 每日 |
| 学科使用分布饼图 | Pie Chart | `/api/admin/stats/subjects` | 实时 |
| 每周访问量柱状图 | Bar Chart | `/api/admin/stats/weekly` | 每周 |
| 用户增长趋势图 | Line Chart | `/api/admin/stats/growth` | 每月 |

---

## 3. 视觉美化设计

### 3.1 设计原则

- **清新教育风**：浅蓝白色调为主，营造舒适学习氛围
- **一致性**：统一的圆角、阴影、间距规范
- **层次感**：通过卡片层级、渐变背景营造深度
- **微交互**：适当的悬停动画、过渡效果

### 3.2 色彩规范

```css
:root {
  /* 主色调 - 清新蓝 */
  --primary-color: #4A90E2;
  --primary-light: #E8F4FD;
  --primary-dark: #2E6AB3;
  --primary-gradient: linear-gradient(135deg, #4A90E2, #2E6AB3);

  /* 辅助色 */
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --info-color: #909399;

  /* 背景色 */
  --bg-white: #FFFFFF;
  --bg-light: #F5F9FC;
  --bg-blue-light: #E8F4FD;
  --bg-gradient: linear-gradient(180deg, #E8F4FD 0%, #F5F9FC 100%);

  /* 文字色 */
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;

  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(74, 144, 226, 0.08);
  --shadow-md: 0 4px 16px rgba(74, 144, 226, 0.12);
  --shadow-lg: 0 8px 24px rgba(74, 144, 226, 0.16);
  --shadow-hover: 0 12px 32px rgba(74, 144, 226, 0.2);
}
```

### 3.3 组件规范

| 组件 | 圆角 | 阴影 | 内边距 |
|------|------|------|--------|
| 卡片 | 16px | shadow-md | 24px |
| 按钮(圆角) | 24px | shadow-sm | 12px 24px |
| 输入框 | 12px | - | 12px 16px |
| 标签 | 8px | - | 4px 12px |
| 头像 | 50% | shadow-sm | - |

### 3.4 动画效果

```css
/* 卡片悬停 */
.card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-hover);
  transition: all 0.3s ease;
}

/* 按钮悬停 */
.btn:hover {
  transform: scale(1.02);
  box-shadow: var(--shadow-md);
}

/* 淡入动画 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

### 3.5 页面优化要点

#### 首页 (Home.vue)
- 添加渐变装饰背景
- 功能卡片添加图标动画
- Hero 区域优化排版

#### 导航栏 (Navbar.vue)
- 添加毛玻璃效果
- 菜单项添加悬停下划线动画

#### 所有页面
- 统一使用 `page-container` 布局
- 添加页面过渡动画
- 优化移动端响应式

---

## 4. 密码加密设计

### 4.1 加密方案

使用 **bcrypt** 算法进行密码哈希加密，这是业界标准的密码存储方案。

**为什么选择 bcrypt：**
- 自带盐值，防止彩虹表攻击
- 可配置工作因子（cost factor），可调整计算复杂度
- 抗 GPU/ASIC 破解
- Spring Security 内置支持

### 4.2 盐值设计

用户提供的 "556920ly" 将作为**应用级盐值**，在 bcrypt 加密前先与密码组合：

```
最终哈希 = bcrypt(password + "556920ly", cost_factor)
```

**Why:** 即使两个用户使用相同密码，bcrypt 内置的随机盐值也会产生不同哈希。应用级盐值提供额外安全层。

### 4.3 Java 实现

#### 4.3.1 添加依赖 (pom.xml)

```xml
<!-- Spring Security Crypto -->
<dependency>
    <groupId>org.springframework.security</groupId>
    <artifactId>spring-security-crypto</artifactId>
</dependency>
```

#### 4.3.2 密码服务类

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

#### 4.3.3 修改 AuthController

- 注册时：`user.setPassword(passwordService.encode(password))`
- 登录时：`passwordService.matches(password, user.getPassword())`

---

## 5. 文件结构变更

### 5.1 前端新增文件

```
frontend/src/
├── components/
│   └── charts/
│       ├── LineChart.vue          # 折线图组件
│       ├── PieChart.vue           # 饼图组件
│       ├── BarChart.vue           # 柱状图组件
│       ├── RadarChart.vue         # 雷达图组件
│       └── index.ts               # 统一导出
├── views/
│   └── Admin.vue                  # 优化管理员页面
└── styles/
    └── charts.css                 # 图表样式
```

### 5.2 后端新增/修改文件

```
backend/src/main/java/com/smartlearning/
├── service/
│   └── PasswordService.java       # 新增：密码加密服务
├── controller/
│   ├── AuthController.java        # 修改：集成密码加密
│   └── AdminController.java       # 修改：添加统计接口
└── dto/
    └── AdminStatsDTO.java         # 新增：统计数据传输对象
```

---

## 6. API 接口设计

### 6.1 新增前端接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/learning/stats/daily` | GET | 获取每日学习统计（用于折线图） |
| `/api/learning/stats/weekly` | GET | 获取本周学习进度（用于环形图） |

### 6.2 新增管理员接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/admin/stats/overview` | GET | 获取总览数据（用户数、活跃数等） |
| `/api/admin/stats/dau` | GET | 获取日活趋势数据 |
| `/api/admin/stats/subjects` | GET | 获取学科使用分布 |
| `/api/admin/stats/weekly` | GET | 获取每周访问量 |
| `/api/admin/stats/growth` | GET | 获取用户增长趋势 |
| `/api/admin/users` | GET | 获取用户列表（分页、搜索） |
| `/api/admin/users/{id}/status` | PUT | 更新用户状态 |

---

## 7. 实施计划

### 阶段一：前端图表组件开发
1. 安装 ECharts 依赖
2. 创建图表公共组件
3. 集成到各页面

### 阶段二：视觉美化
1. 更新全局样式变量
2. 优化各页面组件样式
3. 添加动画效果

### 阶段三：管理员页面
1. 创建统计接口
2. 实现图表展示
3. 完善用户管理功能

### 阶段四：密码加密
1. 添加 Spring Security Crypto 依赖
2. 实现 PasswordService
3. 修改 AuthController

---

## 8. 验收标准

- [ ] 首页展示学习概览卡片和本周进度图
- [ ] 学习报告页展示 4 种图表
- [ ] 学习计划页展示进度甘特图
- [ ] 管理员页面展示 4 种统计图表
- [ ] 所有页面视觉风格统一、清新
- [ ] 卡片悬停动画流畅
- [ ] 用户注册时密码已加密存储
- [ ] 用户登录时密码验证正确
- [ ] 移动端响应式布局正常
