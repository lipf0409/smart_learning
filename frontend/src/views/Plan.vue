<template>
  <div class="plan-page">
    <Navbar />

    <div class="page-container">
      <el-page-header @back="$router.push('/')">
        <template #content>
          <span class="page-title">
            <el-icon><Calendar /></el-icon>
            学习计划
          </span>
        </template>
      </el-page-header>

      <div class="plan-content">
        <!-- 配置区域 -->
        <div class="config-section">
          <div class="config-card">
            <h3>
              <el-icon :size="24" color="#3B82F6"><Setting /></el-icon>
              计划配置
            </h3>

            <el-form label-position="top">
              <el-form-item label="每日可用学习时间">
                <el-input-number v-model="availableHours" :min="1" :max="8" />
                <span class="unit">小时</span>
              </el-form-item>

              <el-form-item label="学习目标">
                <el-input v-model="goal" placeholder="例如：提高数学成绩到90分" />
              </el-form-item>

              <el-form-item label="知识薄弱点">
                <el-select v-model="weakPoints" multiple placeholder="选择薄弱知识点" style="width: 100%">
                  <el-option label="三角函数" value="三角函数" />
                  <el-option label="牛顿运动定律" value="牛顿运动定律" />
                  <el-option label="化学方程式" value="化学方程式" />
                  <el-option label="几何证明" value="几何证明" />
                  <el-option label="代数运算" value="代数运算" />
                </el-select>
              </el-form-item>

              <el-form-item label="知识强项">
                <el-select v-model="strongPoints" multiple placeholder="选择擅长知识点" style="width: 100%">
                  <el-option label="代数运算" value="代数运算" />
                  <el-option label="几何证明" value="几何证明" />
                  <el-option label="物理实验" value="物理实验" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" size="large" round @click="generatePlan" :loading="loading">
                  <el-icon><MagicStick /></el-icon>
                  智能生成计划
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 计划展示区域 -->
        <div class="plan-section" v-if="plan">
          <!-- 进度甘特图 -->
          <div class="gantt-card">
            <h3>
              <el-icon :size="24" color="#8B5CF6"><DataBoard /></el-icon>
              学习进度甘特图
            </h3>
            <div class="gantt-chart">
              <div class="gantt-header">
                <div class="gantt-label">知识点</div>
                <div class="gantt-days">
                  <span v-for="day in 7" :key="day">第{{ day }}天</span>
                </div>
              </div>
              <div class="gantt-body">
                <div v-for="(item, index) in ganttData" :key="index" class="gantt-row">
                  <div class="gantt-label">{{ item.name }}</div>
                  <div class="gantt-bar-container">
                    <div
                      class="gantt-bar"
                      :style="{
                        left: `${item.start * 14.28}%`,
                        width: `${item.duration * 14.28}%`,
                        backgroundColor: item.color
                      }"
                    >
                      <span class="gantt-bar-text">{{ item.duration }}天</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 每日目标 -->
          <div class="daily-card">
            <h3>
              <el-icon :size="24" color="#10B981"><Clock /></el-icon>
              每日学习安排
            </h3>

            <div class="daily-timeline">
              <el-timeline>
                <el-timeline-item
                  v-for="(item, index) in plan.daily_goals"
                  :key="index"
                  :timestamp="item['时间'] || item.time"
                  placement="top"
                  color="#3B82F6"
                >
                  <el-card>
                    <h4>{{ item['内容'] || item.content }}</h4>
                    <p>知识点: {{ item['知识点'] || item.knowledge_point }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </div>

          <!-- 本周重点 -->
          <div class="focus-card">
            <h3>
              <el-icon :size="24" color="#F59E0B"><Aim /></el-icon>
              本周重点攻克
            </h3>

            <div class="focus-list">
              <div v-for="(area, index) in plan.focus_areas" :key="index" class="focus-item">
                <el-icon color="#EF4444"><Warning /></el-icon>
                <span>{{ area }}</span>
                <el-progress :percentage="getProgress(area)" :stroke-width="10" color="#3B82F6" />
              </div>
            </div>
          </div>

          <!-- 里程碑 -->
          <div class="milestone-card">
            <h3>
              <el-icon :size="24" color="#3B82F6"><Flag /></el-icon>
              学习里程碑
            </h3>

            <div class="milestone-list">
              <el-steps direction="vertical" :active="currentMilestone" finish-status="success">
                <el-step
                  v-for="(milestone, index) in plan.milestones"
                  :key="index"
                  :title="milestone['阶段'] || milestone.stage"
                  :description="milestone['目标'] || milestone.goal + ' (' + (milestone['时间'] || milestone.time) + ')'"
                />
              </el-steps>
            </div>
          </div>

          <!-- 时间线 -->
          <div class="timeline-card">
            <h3>
              <el-icon :size="24" color="#06B6D4"><Timer /></el-icon>
              预计完成时间
            </h3>
            <div class="timeline-info">
              <el-statistic title="总学习周期" :value="plan.timeline" />
            </div>
          </div>
        </div>

        <!-- 无计划时的提示 -->
        <div class="empty-plan" v-else>
          <el-icon :size="80" color="#94A3B8"><Calendar /></el-icon>
          <p>请配置学习参数后生成智能学习计划</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calendar, Warning, Setting, MagicStick, Clock, Aim, Flag, Timer, DataBoard
} from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'

interface StudyPlan {
  daily_goals: Array<{时间: string; 内容: string; 知识点: string}>
  weekly_plan: Array<any>
  focus_areas: string[]
  timeline: string
  milestones: Array<{阶段: string; 目标: string; 时间: string}>
}

const availableHours = ref(2)
const goal = ref('')
const weakPoints = ref<string[]>([])
const strongPoints = ref<string[]>([])
const loading = ref(false)
const plan = ref<StudyPlan | null>(null)
const currentMilestone = ref(0)

const progressMap: Record<string, number> = {
  '三角函数': 20,
  '牛顿运动定律': 35,
  '化学方程式': 50
}

const getProgress = (area: string) => {
  return progressMap[area] || 0
}

// 甘特图数据
const ganttData = computed(() => {
  if (!plan.value) return []

  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return weakPoints.value.map((point, index) => ({
    name: point,
    start: index * 2,
    duration: Math.ceil(Math.random() * 2 + 2),
    color: colors[index % colors.length]
  }))
})

const generatePlan = async () => {
  if (!goal.value) {
    ElMessage.warning('请填写学习目标')
    return
  }

  if (weakPoints.value.length === 0) {
    ElMessage.warning('请选择至少一个薄弱知识点')
    return
  }

  loading.value = true

  try {
    // 模拟数据 - 实际应调用API
    plan.value = {
      daily_goals: [
        { '时间': '09:00-10:00', '内容': '复习三角函数基础概念', '知识点': '三角函数' },
        { '时间': '10:00-10:30', '内容': '完成三角函数练习题', '知识点': '三角函数' },
        { '时间': '14:00-15:00', '内容': '学习牛顿运动定律', '知识点': '牛顿运动定律' },
        { '时间': '15:00-15:30', '内容': '物理受力分析练习', '知识点': '牛顿运动定律' },
        { '时间': '16:00-16:30', '内容': '化学方程式配平练习', '知识点': '化学方程式' }
      ],
      weekly_plan: [],
      focus_areas: weakPoints.value,
      timeline: '4周',
      milestones: [
        { '阶段': '第一阶段', '目标': '掌握基础概念', '时间': '第1周' },
        { '阶段': '第二阶段', '目标': '完成基础练习', '时间': '第2周' },
        { '阶段': '第三阶段', '目标': '攻克难题', '时间': '第3周' },
        { '阶段': '第四阶段', '目标': '综合复习巩固', '时间': '第4周' }
      ]
    }
    ElMessage.success('学习计划已生成')
  } catch (error) {
    ElMessage.error('生成计划失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.plan-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #EFF6FF 0%, #F8FAFC 100%);
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
  color: #3B82F6;
}

.plan-content {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 30px;
  margin-top: 30px;
}

.config-card, .gantt-card, .daily-card, .focus-card, .milestone-card, .timeline-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.config-card h3, .gantt-card h3, .daily-card h3, .focus-card h3, .milestone-card h3, .timeline-card h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1E293B;
  margin-bottom: 20px;
  font-weight: 600;
}

.unit {
  margin-left: 10px;
  color: #64748B;
}

.plan-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Gantt Chart */
.gantt-chart {
  margin-top: 20px;
}

.gantt-header {
  display: flex;
  border-bottom: 2px solid #E2E8F0;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.gantt-label {
  width: 120px;
  font-weight: 600;
  color: #1E293B;
}

.gantt-days {
  display: flex;
  flex: 1;
}

.gantt-days span {
  flex: 1;
  text-align: center;
  color: #64748B;
  font-size: 12px;
}

.gantt-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gantt-row {
  display: flex;
  align-items: center;
}

.gantt-row .gantt-label {
  color: #475569;
  font-weight: 500;
}

.gantt-bar-container {
  flex: 1;
  height: 32px;
  background: #F1F5F9;
  border-radius: 8px;
  position: relative;
}

.gantt-bar {
  position: absolute;
  height: 100%;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.gantt-bar:hover {
  transform: scaleY(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.daily-timeline {
  padding: 10px;
}

.daily-timeline .el-card {
  margin-top: 10px;
  border-radius: 12px;
}

.daily-timeline h4 {
  color: #3B82F6;
}

.daily-timeline p {
  color: #64748B;
  margin-top: 5px;
}

.focus-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.focus-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: linear-gradient(135deg, #FEF2F2 0%, #FFF1F2 100%);
  border-radius: 12px;
  border-left: 4px solid #EF4444;
}

.focus-item span {
  flex: 1;
  color: #1E293B;
  font-weight: 500;
}

.milestone-list {
  padding: 10px;
}

.timeline-info {
  padding: 20px;
  background: linear-gradient(135deg, #EFF6FF 0%, #F8FAFC 100%);
  border-radius: 12px;
}

.empty-plan {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.empty-plan p {
  color: #64748B;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .plan-content {
    grid-template-columns: 1fr;
  }
}
</style>