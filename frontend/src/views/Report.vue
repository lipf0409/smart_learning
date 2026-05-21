<template>
  <div class="report-page">
    <Navbar />

    <div class="page-container">
      <el-page-header @back="$router.push('/')">
        <template #content>
          <span class="page-title">
            <el-icon><DataAnalysis /></el-icon>
            学习报告
          </span>
        </template>
      </el-page-header>

      <!-- 学习统计卡片 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-icon blue">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ report.total_questions || 0 }}</div>
            <div class="stat-label">已解题目</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ ((report.correct_rate || 0) * 100).toFixed(1) }}%</div>
            <div class="stat-label">正确率</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ studyHours }}</div>
            <div class="stat-label">学习时长</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">
            <el-icon :size="28"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ Object.keys(report.subjects || {}).length }}</div>
            <div class="stat-label">涉及学科</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <div class="charts-row">
          <div class="chart-card">
            <div class="chart-header">
              <h3>
                <el-icon :size="20" color="#4A90E2"><TrendCharts /></el-icon>
                学习进度趋势
              </h3>
              <el-radio-group v-model="timeRange" size="small">
                <el-radio-button label="7">近7天</el-radio-button>
                <el-radio-button label="30">近30天</el-radio-button>
              </el-radio-group>
            </div>
            <LineChart
              :data="progressData"
              height="280px"
              color="#4A90E2"
            />
          </div>
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#67C23A"><PieChart /></el-icon>
              学科分布
            </h3>
            <PieChart
              :data="subjectPieData"
              height="280px"
            />
          </div>
        </div>
        <div class="charts-row">
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#E6A23C"><DataLine /></el-icon>
              各学科正确率
            </h3>
            <BarChart
              :data="correctRateData"
              height="280px"
            />
          </div>
          <div class="chart-card">
            <h3>
              <el-icon :size="20" color="#9B59B6"><TrendCharts /></el-icon>
              知识掌握程度
            </h3>
            <RadarChart
              :indicators="radarIndicators"
              :values="radarValues"
              height="280px"
            />
          </div>
        </div>
      </div>

      <div class="content-grid">
        <!-- 左侧：知识漏洞分析 -->
        <div class="analysis-section">
          <!-- 知识薄弱点 -->
          <div class="weak-points-card">
            <h3>
              <el-icon :size="24" color="#F56C6C"><Warning /></el-icon>
              知识薄弱点
            </h3>

            <div class="weak-points-list" v-if="report.weak_points && report.weak_points.length > 0">
              <div v-for="(point, index) in report.weak_points" :key="index" class="weak-point-item">
                <div class="point-header">
                  <span class="point-name">{{ point['知识点'] || point.knowledge_point }}</span>
                  <el-tag type="danger" size="small">错误 {{ point['错误次数'] || point.error_count }} 次</el-tag>
                </div>
                <p class="point-suggestion">{{ point['建议'] || point.suggestion }}</p>
              </div>
            </div>

            <div class="empty-tip" v-else>
              <el-icon :size="48" color="#67C23A"><CircleCheckFilled /></el-icon>
              <p>暂无明显薄弱点，继续保持！</p>
            </div>
          </div>

          <!-- 知识强项 -->
          <div class="strong-points-card">
            <h3>
              <el-icon :size="24" color="#67C23A"><Medal /></el-icon>
              知识强项
            </h3>

            <div class="strong-tags" v-if="report.strong_points && report.strong_points.length > 0">
              <el-tag
                v-for="(point, index) in report.strong_points"
                :key="index"
                type="success"
                effect="light"
                size="large"
              >
                {{ point }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 右侧：学习建议 -->
        <div class="recommendations-section">
          <!-- 学习建议 -->
          <div class="recommendations-card">
            <h3>
              <el-icon :size="24" color="#E6A23C"><Lightning /></el-icon>
              学习建议
            </h3>

            <ul class="recommendations-list" v-if="report.recommendations && report.recommendations.length > 0">
              <li v-for="(rec, index) in report.recommendations" :key="index">
                <el-icon color="#4A90E2"><Check /></el-icon>
                {{ rec }}
              </li>
            </ul>
          </div>

          <!-- 强化练习建议 -->
          <div class="practice-card">
            <h3>
              <el-icon :size="24" color="#4A90E2"><EditPen /></el-icon>
              强化练习建议
            </h3>

            <div class="practice-list" v-if="report.practice_suggestions && report.practice_suggestions.length > 0">
              <div v-for="(practice, index) in report.practice_suggestions" :key="index" class="practice-item">
                <div class="practice-info">
                  <span class="practice-point">{{ practice['知识点'] || practice.knowledge_point }}</span>
                  <span class="practice-type">{{ practice['题目类型'] || practice.question_type }}</span>
                </div>
                <div class="practice-meta">
                  <el-tag size="small">{{ practice['难度'] || practice.difficulty }}</el-tag>
                  <span class="practice-count">推荐 {{ practice['数量'] || practice.count }} 题</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 生成报告按钮 -->
      <div class="action-section">
        <el-button type="primary" size="large" round @click="generateReport" :loading="loading">
          <el-icon><Refresh /></el-icon>
          重新分析
        </el-button>
        <el-button type="success" size="large" round @click="$router.push('/plan')">
          <el-icon><Calendar /></el-icon>
          生成学习计划
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataAnalysis, Check, Refresh, Calendar, Document, CircleCheck, Timer,
  Collection, TrendCharts, PieChart as PieChartIcon, DataLine, DataBoard,
  Warning, CircleCheckFilled, Medal, Lightning, EditPen
} from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import { LineChart, PieChart, BarChart, RadarChart } from '../components/charts'

interface LearningReport {
  total_questions: number
  correct_rate: number
  subjects: Record<string, number>
  weak_points: Array<{知识点: string; 错误次数: number; 建议: string}>
  strong_points: string[]
  recommendations: string[]
  practice_suggestions: Array<{知识点: string; 题目类型: string; 难度: string; 数量: number}>
}

const report = ref<LearningReport>({
  total_questions: 0,
  correct_rate: 0,
  subjects: {},
  weak_points: [],
  strong_points: [],
  recommendations: [],
  practice_suggestions: []
})

const studyHours = ref(12)
const loading = ref(false)
const timeRange = ref('7')

// 学习进度数据
const progressData = computed(() => {
  const days = parseInt(timeRange.value)
  const data = []
  const now = new Date()
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({
      date: `${date.getMonth() + 1}/${date.getDate()}`,
      value: Math.round(Math.random() * 3 + 1)
    })
  }
  return data
})

// 学科分布饼图数据
const subjectPieData = computed(() => {
  return Object.entries(report.value.subjects || {}).map(([name, value]) => ({
    name,
    value
  }))
})

// 正确率柱状图数据
const correctRateData = computed(() => {
  const subjects = Object.keys(report.value.subjects || {})
  return subjects.map(name => ({
    name,
    value: Math.round(Math.random() * 30 + 60) // 模拟正确率
  }))
})

// 雷达图指标
const radarIndicators = computed(() => {
  const subjects = Object.keys(report.value.subjects || {})
  if (subjects.length === 0) {
    return [
      { name: '数学', max: 100 },
      { name: '物理', max: 100 },
      { name: '化学', max: 100 },
      { name: '语文', max: 100 },
      { name: '英语', max: 100 }
    ]
  }
  return subjects.map(name => ({ name, max: 100 }))
})

// 雷达图数据
const radarValues = computed(() => {
  return radarIndicators.value.map(() => Math.round(Math.random() * 40 + 50))
})

const generateReport = async () => {
  loading.value = true
  try {
    // 模拟数据 - 实际应调用API
    report.value = {
      total_questions: 50,
      correct_rate: 0.72,
      subjects: {
        '数学': 25,
        '物理': 15,
        '化学': 10
      },
      weak_points: [
        { '知识点': '三角函数', '错误次数': 5, '建议': '建议多做三角函数恒等变换练习' },
        { '知识点': '牛顿运动定律', '错误次数': 3, '建议': '复习牛顿三定律的基本概念' }
      ],
      strong_points: ['代数运算', '几何证明', '化学方程式'],
      recommendations: [
        '建议每天花30分钟复习三角函数相关知识点',
        '物理部分需要加强受力分析的训练',
        '可以尝试做一些综合题目提高解题能力'
      ],
      practice_suggestions: [
        { '知识点': '三角函数', '题目类型': '恒等变换', '难度': '中等', '数量': 10 },
        { '知识点': '牛顿运动定律', '题目类型': '受力分析', '难度': '简单', '数量': 8 }
      ]
    }
    ElMessage.success('学习报告已生成')
  } catch (error) {
    ElMessage.error('生成报告失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  generateReport()
})
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8F4FD 0%, #F5F9FC 100%);
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  color: #4A90E2;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 16px;
  padding: 24px;
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
.stat-icon.purple { background: linear-gradient(135deg, #9B59B6, #8E44AD); }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #4A90E2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

/* Charts Section */
.charts-section {
  margin-top: 30px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.1);
}

.chart-card h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
  margin-bottom: 20px;
  font-size: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin-bottom: 0;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 30px;
}

.weak-points-card, .strong-points-card,
.recommendations-card, .practice-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
  margin-bottom: 20px;
}

.weak-points-card h3, .strong-points-card h3,
.recommendations-card h3, .practice-card h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
  margin-bottom: 20px;
}

.weak-points-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.weak-point-item {
  padding: 15px;
  background: linear-gradient(135deg, #FEF0F0 0%, #FFF5F5 100%);
  border-radius: 12px;
  border-left: 4px solid #F56C6C;
}

.point-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.point-name {
  font-weight: bold;
  color: #303133;
}

.point-suggestion {
  color: #606266;
  margin-top: 10px;
  font-size: 14px;
}

.empty-tip {
  text-align: center;
  padding: 30px;
}

.empty-tip p {
  color: #909399;
  margin-top: 12px;
}

.strong-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.recommendations-list {
  list-style: none;
  padding: 0;
}

.recommendations-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: linear-gradient(135deg, #E8F4FD 0%, #F5F9FC 100%);
  border-radius: 10px;
  margin-bottom: 10px;
  color: #606266;
}

.practice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.practice-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: linear-gradient(135deg, #F5F9FC 0%, #F8FAFC 100%);
  border-radius: 12px;
}

.practice-point {
  font-weight: bold;
  color: #303133;
}

.practice-type {
  color: #909399;
  margin-left: 10px;
}

.practice-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.practice-count {
  color: #4A90E2;
  font-weight: bold;
}

.action-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

@media (max-width: 992px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .stats-overview {
    grid-template-columns: 1fr;
  }
}
</style>