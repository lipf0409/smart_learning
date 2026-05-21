<template>
  <div class="admin-page">
    <Navbar />

    <div class="admin-container">
      <div class="admin-header">
        <h1>
          <div class="header-icon">
            <el-icon :size="28"><Setting /></el-icon>
          </div>
          管理后台
        </h1>
        <p>系统管理与数据统计</p>
      </div>

      <!-- Stats Cards -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon blue">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
            <div class="stat-trend up">+{{ stats.newUsersToday }} 今日新增</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon green">
            <el-icon :size="28"><Camera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalQuestions }}</div>
            <div class="stat-label">搜题次数</div>
            <div class="stat-trend up">+{{ stats.questionsToday }} 今日</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon orange">
            <el-icon :size="28"><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalPostures }}</div>
            <div class="stat-label">检测次数</div>
            <div class="stat-trend up">+{{ stats.posturesToday }} 今日</div>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-icon red">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.badPostureCount }}</div>
            <div class="stat-label">不良坐姿次数</div>
            <div class="stat-trend down">需关注</div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="charts-row">
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#4A90E2"><TrendCharts /></el-icon>
              用户活跃度趋势
            </h3>
            <LineChart
              :data="activityData"
              height="260px"
              color="#4A90E2"
            />
          </div>
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#67C23A"><PieChart /></el-icon>
              学科使用分布
            </h3>
            <PieChart
              :data="subjectUsageData"
              height="260px"
            />
          </div>
        </div>
        <div class="charts-row">
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#E6A23C"><DataBoard /></el-icon>
              每周访问量统计
            </h3>
            <BarChart
              :data="weeklyVisitData"
              height="260px"
            />
          </div>
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#67C23A"><DataLine /></el-icon>
              用户增长趋势
            </h3>
            <LineChart
              :data="userGrowthData"
              height="260px"
              color="#67C23A"
            />
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="admin-tabs">
        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="table-header">
            <el-input
              v-model="searchUsername"
              placeholder="搜索用户名"
              prefix-icon="Search"
              clearable
              style="width: 200px;"
            />
            <el-button type="primary" @click="refreshUsers">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>

          <el-table :data="filteredUsers" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="createdAt" label="注册时间" width="180" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                  {{ row.status === 'active' ? '正常' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="editUser(row)">编辑</el-button>
                <el-button size="small" :type="row.status === 'active' ? 'warning' : 'success'" @click="toggleUserStatus(row)">
                  {{ row.status === 'active' ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 搜题记录 -->
        <el-tab-pane label="搜题记录" name="questions">
          <el-table :data="questionRecords" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="userId" label="用户ID" width="100" />
            <el-table-column prop="questionText" label="题目内容" show-overflow-tooltip />
            <el-table-column prop="subject" label="学科" width="100" />
            <el-table-column prop="createdAt" label="时间" width="180" />
          </el-table>
        </el-tab-pane>

        <!-- 坐姿记录 -->
        <el-tab-pane label="坐姿记录" name="postures">
          <el-table :data="postureRecords" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="userId" label="用户ID" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'good' ? 'success' : 'danger'">
                  {{ row.status === 'good' ? '良好' : '不良' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="{ row }">
                {{ (row.confidence * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="detectedAt" label="检测时间" width="180" />
          </el-table>
        </el-tab-pane>

        <!-- 系统设置 -->
        <el-tab-pane label="系统设置" name="settings">
          <el-form label-width="150px" style="max-width: 500px;">
            <el-form-item label="AI服务地址">
              <el-input v-model="settings.aiServiceUrl" placeholder="http://localhost:8000" />
            </el-form-item>
            <el-form-item label="检测间隔(秒)">
              <el-input-number v-model="settings.detectInterval" :min="1" :max="30" />
            </el-form-item>
            <el-form-item label="置信度阈值">
              <el-slider v-model="settings.confidenceThreshold" :min="0" :max="100" show-input />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting, User, Camera, Monitor, Warning, Refresh, Search,
  TrendCharts, PieChart as PieChartIcon, DataLine, DataBoard
} from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import { LineChart, PieChart, BarChart } from '../components/charts'

// 统计数据
const stats = ref({
  totalUsers: 156,
  totalQuestions: 1234,
  totalPostures: 5678,
  badPostureCount: 234,
  newUsersToday: 5,
  questionsToday: 48,
  posturesToday: 156
})

// 用户活跃度数据
const activityData = ref([
  { date: '5/1', value: 120 },
  { date: '5/2', value: 145 },
  { date: '5/3', value: 132 },
  { date: '5/4', value: 168 },
  { date: '5/5', value: 185 },
  { date: '5/6', value: 142 },
  { date: '5/7', value: 156 }
])

// 学科使用分布
const subjectUsageData = ref([
  { name: '数学', value: 450 },
  { name: '物理', value: 280 },
  { name: '化学', value: 200 },
  { name: '语文', value: 180 },
  { name: '英语', value: 124 }
])

// 每周访问量
const weeklyVisitData = ref([
  { name: '周一', value: 320 },
  { name: '周二', value: 380 },
  { name: '周三', value: 420 },
  { name: '周四', value: 390 },
  { name: '周五', value: 450 },
  { name: '周六', value: 520 },
  { name: '周日', value: 480 }
])

// 用户增长趋势
const userGrowthData = ref([
  { date: '12月', value: 80 },
  { date: '1月', value: 95 },
  { date: '2月', value: 110 },
  { date: '3月', value: 128 },
  { date: '4月', value: 142 },
  { date: '5月', value: 156 }
])

// 用户数据
const users = ref([
  { id: 1, username: 'admin', email: 'admin@example.com', createdAt: '2026-01-01', status: 'active' },
  { id: 2, username: 'user1', email: 'user1@example.com', createdAt: '2026-02-15', status: 'active' },
  { id: 3, username: 'user2', email: 'user2@example.com', createdAt: '2026-03-20', status: 'active' },
  { id: 4, username: 'test', email: 'test@example.com', createdAt: '2026-04-10', status: 'disabled' },
])

const searchUsername = ref('')
const filteredUsers = computed(() => {
  if (!searchUsername.value) return users.value
  return users.value.filter(u => u.username.includes(searchUsername.value))
})

// 搜题记录
const questionRecords = ref([
  { id: 1, userId: 2, questionText: '求证: sin²x + cos²x = 1', subject: '数学', createdAt: '2026-05-01 10:30' },
  { id: 2, userId: 3, questionText: '计算: ∫x²dx', subject: '数学', createdAt: '2026-05-01 11:00' },
  { id: 3, userId: 2, questionText: '牛顿第二定律的应用', subject: '物理', createdAt: '2026-05-02 09:15' },
])

// 坐姿记录
const postureRecords = ref([
  { id: 1, userId: 2, status: 'good', confidence: 0.95, detectedAt: '2026-05-01 10:00' },
  { id: 2, userId: 3, status: 'bad', confidence: 0.87, detectedAt: '2026-05-01 10:05' },
  { id: 3, userId: 2, status: 'good', confidence: 0.92, detectedAt: '2026-05-01 10:10' },
])

// 系统设置
const settings = ref({
  aiServiceUrl: 'http://localhost:8000',
  detectInterval: 3,
  confidenceThreshold: 70
})

const activeTab = ref('users')

const refreshUsers = () => {
  ElMessage.success('用户列表已刷新')
}

const editUser = (user: any) => {
  ElMessage.info(`编辑用户: ${user.username}`)
}

const toggleUserStatus = (user: any) => {
  const newStatus = user.status === 'active' ? '禁用' : '启用'
  ElMessageBox.confirm(`确定${newStatus}用户 ${user.username}?`, '确认', {
    type: 'warning'
  }).then(() => {
    user.status = user.status === 'active' ? 'disabled' : 'active'
    ElMessage.success(`用户已${newStatus}`)
  }).catch(() => {})
}

const saveSettings = () => {
  ElMessage.success('设置已保存')
}

onMounted(() => {
  // 加载实际数据
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8F4FD 0%, #F5F9FC 100%);
}

.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
}

.admin-header {
  margin-bottom: 30px;
}

.admin-header h1 {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4A90E2;
  font-size: 28px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4A90E2, #2E6AB3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.admin-header p {
  color: #909399;
  margin-top: 8px;
  margin-left: 60px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.blue { background: linear-gradient(135deg, #4A90E2, #2E6AB3); }
.stat-icon.green { background: linear-gradient(135deg, #67C23A, #4A9F2E); }
.stat-icon.orange { background: linear-gradient(135deg, #E6A23C, #C98B2B); }
.stat-icon.red { background: linear-gradient(135deg, #F56C6C, #D94848); }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend.up { color: #67C23A; }
.stat-trend.down { color: #F56C6C; }

/* Charts Section */
.charts-section {
  margin-bottom: 30px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.1);
}

.chart-card h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
  margin-bottom: 16px;
  font-size: 16px;
}

.admin-tabs {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

@media (max-width: 992px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>