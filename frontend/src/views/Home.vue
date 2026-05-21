<template>
  <div class="home-page">
    <Navbar />

    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-bg-pattern"></div>
      <div class="hero-content">
        <h1 class="hero-title">
          <div class="hero-icon-wrapper">
            <el-icon :size="48"><Reading /></el-icon>
          </div>
          智能学习系统
        </h1>
        <p class="hero-subtitle">AI赋能学习，让知识触手可及</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" round @click="$router.push('/chat')">
            <el-icon><ChatDotRound /></el-icon>
            开始体验
          </el-button>
          <el-button size="large" round class="btn-outline" @click="$router.push('/report')">
            <el-icon><DataAnalysis /></el-icon>
            查看报告
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <div class="hero-illustration">
          <div class="floating-card card-1">
            <el-icon :size="24" color="#3B82F6"><TrendCharts /></el-icon>
          </div>
          <div class="floating-card card-2">
            <el-icon :size="24" color="#10B981"><Medal /></el-icon>
          </div>
          <div class="floating-card card-3">
            <el-icon :size="24" color="#F59E0B"><Star /></el-icon>
          </div>
          <div class="center-circle">
            <el-icon :size="64" color="white"><Reading /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 今日学习概览 -->
    <div class="overview-section">
      <div class="container">
        <div class="section-header">
          <div class="header-icon blue">
            <el-icon :size="24"><Sunny /></el-icon>
          </div>
          <h2>今日学习概览</h2>
        </div>
        <div class="overview-cards">
          <div class="overview-card">
            <div class="card-icon blue">
              <el-icon :size="28"><Timer /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ studyStats.todayHours }}h</div>
              <div class="card-label">学习时长</div>
              <div class="card-trend up">
                <el-icon><Top /></el-icon>
                较昨日 +{{ studyStats.hoursChange }}h
              </div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon green">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ studyStats.todayQuestions }}</div>
              <div class="card-label">解答题目</div>
              <div class="card-trend up">
                <el-icon><Top /></el-icon>
                较昨日 +{{ studyStats.questionsChange }}题
              </div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon orange">
              <el-icon :size="28"><CircleCheck /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ studyStats.correctRate }}%</div>
              <div class="card-label">正确率</div>
              <div class="card-trend up">
                <el-icon><Top /></el-icon>
                较昨日 +{{ studyStats.rateChange }}%
              </div>
            </div>
          </div>
          <div class="overview-card">
            <div class="card-icon purple">
              <el-icon :size="28"><Flag /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-value">{{ studyStats.streakDays }}</div>
              <div class="card-label">连续学习天数</div>
              <div class="card-trend keep">
                <el-icon><Check /></el-icon>
                保持连续
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 本周学习进度 -->
    <div class="weekly-section">
      <div class="container">
        <div class="section-header">
          <div class="header-icon purple">
            <el-icon :size="24"><Calendar /></el-icon>
          </div>
          <h2>本周学习进度</h2>
        </div>
        <div class="weekly-content">
          <div class="weekly-chart">
            <PieChart
              :data="weeklyData"
              title="本周学习时长分布"
              height="280px"
            />
          </div>
          <div class="weekly-stats">
            <div class="weekly-stat-item">
              <div class="stat-icon-wrap blue">
                <el-icon :size="20"><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">本周总时长</div>
                <div class="stat-value">{{ weeklyTotalHours }}h</div>
              </div>
            </div>
            <div class="weekly-stat-item">
              <div class="stat-icon-wrap green">
                <el-icon :size="20"><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-label">日均时长</div>
                <div class="stat-value">{{ weeklyAvgHours }}h</div>
              </div>
            </div>
            <div class="weekly-stat-item progress-item">
              <div class="stat-header">
                <div class="stat-icon-wrap orange">
                  <el-icon :size="20"><Aim /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">完成目标</div>
                  <div class="stat-value">{{ weeklyGoalProgress }}%</div>
                </div>
              </div>
              <el-progress :percentage="weeklyGoalProgress" :stroke-width="10" :show-text="false" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目背景 -->
    <div class="background-section">
      <div class="container">
        <div class="section-header">
          <div class="header-icon cyan">
            <el-icon :size="24"><InfoFilled /></el-icon>
          </div>
          <h2>项目背景</h2>
        </div>
        <div class="background-cards">
          <div class="bg-card">
            <div class="bg-icon blue">
              <el-icon :size="32"><Notebook /></el-icon>
            </div>
            <h3>学习压力增大</h3>
            <p>随着教育竞争日益激烈，学生面临巨大的学业压力，课后作业和自主学习时间大幅增加，但缺乏有效的学习辅助工具。</p>
          </div>
          <div class="bg-card">
            <div class="bg-icon green">
              <el-icon :size="32"><Service /></el-icon>
            </div>
            <h3>辅导资源不均</h3>
            <p>优质教育资源分布不均衡，许多学生无法获得及时、专业的学习指导，导致学习效率低下，知识漏洞难以弥补。</p>
          </div>
          <div class="bg-card">
            <div class="bg-icon orange">
              <el-icon :size="32"><FirstAidKit /></el-icon>
            </div>
            <h3>健康问题凸显</h3>
            <p>长时间伏案学习导致学生近视率攀升、脊椎问题频发，不良坐姿严重影响青少年的身体健康发育。</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目立意 -->
    <div class="purpose-section">
      <div class="purpose-bg"></div>
      <div class="container">
        <div class="section-header light">
          <div class="header-icon white">
            <el-icon :size="24"><Aim /></el-icon>
          </div>
          <h2>项目立意</h2>
        </div>
        <div class="purpose-content">
          <div class="purpose-main">
            <div class="brain-icon">
              <el-icon :size="56"><Cpu /></el-icon>
            </div>
            <h3>以AI技术赋能教育，让每一位学生都能享受智能化、个性化的学习体验</h3>
          </div>
          <div class="purpose-points">
            <div class="purpose-item">
              <div class="purpose-icon-item blue">
                <el-icon :size="24"><Check /></el-icon>
              </div>
              <div class="purpose-text">
                <h4>启发式教学</h4>
                <p>拒绝直接给答案，引导学生自主思考，培养独立解决问题的能力</p>
              </div>
            </div>
            <div class="purpose-item">
              <div class="purpose-icon-item green">
                <el-icon :size="24"><Check /></el-icon>
              </div>
              <div class="purpose-text">
                <h4>个性化学习</h4>
                <p>根据学习数据智能分析知识漏洞，定制专属学习计划</p>
              </div>
            </div>
            <div class="purpose-item">
              <div class="purpose-icon-item orange">
                <el-icon :size="24"><Check /></el-icon>
              </div>
              <div class="purpose-text">
                <h4>健康守护</h4>
                <p>实时监测坐姿状态，保护学生视力与脊椎健康</p>
              </div>
            </div>
            <div class="purpose-item">
              <div class="purpose-icon-item purple">
                <el-icon :size="24"><Check /></el-icon>
              </div>
              <div class="purpose-text">
                <h4>高效便捷</h4>
                <p>拍照搜题、AI答疑，随时随地获取学习帮助</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目功能 -->
    <div class="features-section">
      <div class="container">
        <div class="section-header">
          <div class="header-icon green">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <h2>项目功能</h2>
        </div>
        <div class="features-grid">
          <div class="feature-card" @click="$router.push('/chat')">
            <div class="feature-icon blue">
              <el-icon :size="36"><ChatDotRound /></el-icon>
            </div>
            <h3>AI答疑助手</h3>
            <p>全天候启发式答疑，引导思考而非直接给答案，杜绝惰性学习</p>
            <div class="card-tags">
              <el-tag type="primary" effect="light" size="small">启发式教学</el-tag>
              <el-tag type="success" effect="light" size="small">多学科支持</el-tag>
            </div>
          </div>

          <div class="feature-card" @click="$router.push('/report')">
            <div class="feature-icon green">
              <el-icon :size="36"><DataAnalysis /></el-icon>
            </div>
            <h3>学习报告</h3>
            <p>分析学习记录，精准定位知识漏洞，生成个性化学习报告</p>
            <div class="card-tags">
              <el-tag type="warning" effect="light" size="small">漏洞分析</el-tag>
              <el-tag type="info" effect="light" size="small">练习建议</el-tag>
            </div>
          </div>

          <div class="feature-card" @click="$router.push('/plan')">
            <div class="feature-icon orange">
              <el-icon :size="36"><Calendar /></el-icon>
            </div>
            <h3>学习计划</h3>
            <p>根据学习进度智能生成动态学习计划，确保学习连贯性</p>
            <div class="card-tags">
              <el-tag type="primary" effect="light" size="small">智能规划</el-tag>
              <el-tag type="success" effect="light" size="small">进度追踪</el-tag>
            </div>
          </div>

          <div class="feature-card" @click="$router.push('/question')">
            <div class="feature-icon purple">
              <el-icon :size="36"><Camera /></el-icon>
            </div>
            <h3>拍照搜题</h3>
            <p>拍照上传题目，AI智能识别并解答，提供详细解题步骤</p>
            <div class="card-tags">
              <el-tag type="success" effect="light" size="small">OCR识别</el-tag>
              <el-tag type="warning" effect="light" size="small">详细步骤</el-tag>
            </div>
          </div>

          <div class="feature-card" @click="$router.push('/posture')">
            <div class="feature-icon cyan">
              <el-icon :size="36"><Monitor /></el-icon>
            </div>
            <h3>坐姿检测</h3>
            <p>实时监测坐姿状态，智能提醒纠正，保护脊椎健康</p>
            <div class="card-tags">
              <el-tag type="primary" effect="light" size="small">实时检测</el-tag>
              <el-tag type="danger" effect="light" size="small">健康守护</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <p>© 2026 智能学习系统 | AI赋能教育，让学习更高效</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { PieChart } from '../components/charts'
import {
  ChatDotRound, Check, Top, Sunny, Timer, Document, CircleCheck, Flag,
  Calendar, InfoFilled, Notebook, Service, FirstAidKit, Aim, Cpu,
  Setting, DataAnalysis, Camera, Monitor, Reading, TrendCharts, Star, Medal
} from '@element-plus/icons-vue'

// 学习统计数据
const studyStats = ref({
  todayHours: 2.5,
  hoursChange: 0.5,
  todayQuestions: 15,
  questionsChange: 3,
  correctRate: 85,
  rateChange: 5,
  streakDays: 7
})

// 本周学习数据
const weeklyData = ref([
  { name: '周一', value: 2.5 },
  { name: '周二', value: 3.0 },
  { name: '周三', value: 2.0 },
  { name: '周四', value: 3.5 },
  { name: '周五', value: 2.8 },
  { name: '周六', value: 4.0 },
  { name: '周日', value: 1.5 }
])

const weeklyTotalHours = computed(() => {
  return weeklyData.value.reduce((sum, item) => sum + item.value, 0).toFixed(1)
})

const weeklyAvgHours = computed(() => {
  return (parseFloat(weeklyTotalHours.value) / 7).toFixed(1)
})

const weeklyGoalProgress = computed(() => {
  const goal = 21
  return Math.min(100, Math.round((parseFloat(weeklyTotalHours.value) / goal) * 100))
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #F8FAFC;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

/* Hero Section */
.hero-section {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 40px;
  background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 50%, #FDF2F8 100%);
  overflow: hidden;
}

.hero-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(236, 72, 153, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

.hero-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.hero-title {
  display: flex;
  align-items: center;
  font-size: 48px;
  background: linear-gradient(135deg, #1E293B, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
}

.hero-icon-wrapper {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 16px;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.hero-subtitle {
  font-size: 22px;
  color: #64748B;
  margin-bottom: 40px;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn-outline {
  border: 2px solid #E2E8F0 !important;
  background: white !important;
  color: #475569 !important;
}

.btn-outline:hover {
  border-color: #3B82F6 !important;
  color: #3B82F6 !important;
}

.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.hero-illustration {
  position: relative;
  width: 280px;
  height: 280px;
}

.center-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 140px;
  height: 140px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 60px rgba(59, 130, 246, 0.4);
}

.floating-card {
  position: absolute;
  width: 56px;
  height: 56px;
  background: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  animation: floatCard 4s ease-in-out infinite;
}

.card-1 { top: 10px; left: 20px; animation-delay: 0s; }
.card-2 { top: 30px; right: 10px; animation-delay: 1s; }
.card-3 { bottom: 40px; right: 30px; animation-delay: 2s; }

@keyframes floatCard {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(5deg); }
}

/* Section Header */
.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon.blue { background: linear-gradient(135deg, #3B82F6, #1D4ED8); }
.header-icon.green { background: linear-gradient(135deg, #10B981, #059669); }
.header-icon.orange { background: linear-gradient(135deg, #F59E0B, #D97706); }
.header-icon.purple { background: linear-gradient(135deg, #8B5CF6, #6D28D9); }
.header-icon.cyan { background: linear-gradient(135deg, #06B6D4, #0891B2); }
.header-icon.white { background: rgba(255, 255, 255, 0.2); }

.section-header h2 {
  font-size: 26px;
  color: #1E293B;
  margin: 0;
  font-weight: 700;
}

.section-header.light h2 {
  color: white;
}

/* Overview Section */
.overview-section {
  background: white;
  padding: 60px 0;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F1F5F9 100%);
  border-radius: 16px;
  border: 1px solid #E2E8F0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.12);
  border-color: #3B82F6;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-icon.blue { background: linear-gradient(135deg, #3B82F6, #1D4ED8); }
.card-icon.green { background: linear-gradient(135deg, #10B981, #059669); }
.card-icon.orange { background: linear-gradient(135deg, #F59E0B, #D97706); }
.card-icon.purple { background: linear-gradient(135deg, #8B5CF6, #6D28D9); }
.card-icon.cyan { background: linear-gradient(135deg, #06B6D4, #0891B2); }

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #1E293B;
}

.card-label {
  font-size: 14px;
  color: #64748B;
  margin-top: 2px;
}

.card-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 6px;
  font-weight: 500;
}

.card-trend.up { color: #10B981; }
.card-trend.keep { color: #F59E0B; }

/* Weekly Section */
.weekly-section {
  background: linear-gradient(180deg, #F8FAFC 0%, #EFF6FF 100%);
  padding: 60px 0;
}

.weekly-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 32px;
  align-items: center;
}

.weekly-chart {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.weekly-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weekly-stat-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid #E2E8F0;
  transition: all 0.3s ease;
}

.weekly-stat-item:hover {
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
  border-color: #3B82F6;
}

.stat-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon-wrap.blue { background: linear-gradient(135deg, #3B82F6, #1D4ED8); }
.stat-icon-wrap.green { background: linear-gradient(135deg, #10B981, #059669); }
.stat-icon-wrap.orange { background: linear-gradient(135deg, #F59E0B, #D97706); }

.weekly-stat-item .stat-label {
  font-size: 13px;
  color: #64748B;
}

.weekly-stat-item .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1E293B;
  margin-top: 2px;
}

.progress-item {
  flex-direction: column;
  align-items: stretch;
}

.progress-item .stat-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

/* Background Section */
.background-section {
  background: white;
  padding: 60px 0;
}

.background-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.bg-card {
  text-align: center;
  padding: 36px 28px;
  border-radius: 20px;
  background: linear-gradient(135deg, #FAFBFC 0%, #F1F5F9 100%);
  border: 1px solid #E2E8F0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.bg-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(59, 130, 246, 0.12);
  border-color: #3B82F6;
}

.bg-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 20px;
}

.bg-card h3 {
  font-size: 20px;
  color: #1E293B;
  margin-bottom: 12px;
  font-weight: 600;
}

.bg-card p {
  font-size: 14px;
  color: #64748B;
  line-height: 1.7;
}

/* Purpose Section */
.purpose-section {
  position: relative;
  background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  padding: 60px 0;
  overflow: hidden;
}

.purpose-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

.purpose-section .container {
  position: relative;
  z-index: 1;
}

.purpose-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.purpose-main {
  text-align: center;
}

.brain-icon {
  width: 96px;
  height: 96px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 24px;
  backdrop-filter: blur(10px);
}

.purpose-main h3 {
  font-size: 24px;
  font-weight: 500;
  color: white;
  line-height: 1.6;
  max-width: 700px;
  margin: 0;
}

.purpose-points {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  width: 100%;
  max-width: 900px;
}

.purpose-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.12);
  padding: 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.purpose-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(8px);
}

.purpose-icon-item {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.purpose-icon-item.blue { background: rgba(59, 130, 246, 0.5); }
.purpose-icon-item.green { background: rgba(16, 185, 129, 0.5); }
.purpose-icon-item.orange { background: rgba(245, 158, 11, 0.5); }
.purpose-icon-item.purple { background: rgba(139, 92, 246, 0.5); }

.purpose-text h4 {
  font-size: 17px;
  color: white;
  margin: 0 0 6px 0;
  font-weight: 600;
}

.purpose-text p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.6;
  margin: 0;
}

/* Features Section */
.features-section {
  background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
  padding: 60px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 32px 28px;
  text-align: center;
  cursor: pointer;
  border: 1px solid #E2E8F0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3B82F6, #8B5CF6);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 50px rgba(59, 130, 246, 0.15);
  border-color: #3B82F6;
}

.feature-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto 20px;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-card h3 {
  font-size: 20px;
  color: #1E293B;
  margin-bottom: 10px;
  font-weight: 600;
}

.feature-card p {
  font-size: 14px;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 16px;
}

.card-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Footer */
.footer {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #1E293B, #334155);
  color: rgba(255, 255, 255, 0.8);
}

.footer p {
  margin: 0;
  font-size: 14px;
}

/* Responsive */
@media (max-width: 992px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .background-cards,
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .purpose-points {
    grid-template-columns: 1fr;
  }

  .weekly-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    padding: 50px 20px;
    text-align: center;
  }

  .hero-title {
    font-size: 32px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .hero-image {
    display: none;
  }

  .container {
    padding: 0 20px;
  }

  .overview-cards {
    grid-template-columns: 1fr;
  }

  .background-section,
  .purpose-section,
  .features-section {
    padding: 40px 0;
  }

  .background-cards,
  .features-grid {
    grid-template-columns: 1fr;
  }

  .section-header h2 {
    font-size: 22px;
  }
}
</style>