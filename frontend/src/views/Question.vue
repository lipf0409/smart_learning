<template>
  <div class="question-page">
    <Navbar />

    <div class="page-container">
      <el-page-header @back="$router.push('/')">
        <template #content>
          <span class="page-title">
            <el-icon><Camera /></el-icon>
            拍照搜题
          </span>
        </template>
      </el-page-header>

      <div class="content-grid">
        <!-- 左侧：上传区域 -->
        <div class="upload-section">
          <div class="upload-card">
            <div class="upload-header">
              <div class="header-icon">
                <el-icon :size="40"><Camera /></el-icon>
              </div>
              <h3>上传题目图片</h3>
              <p>支持 JPG、PNG 格式，AI智能识别解答</p>
            </div>

            <el-upload
              ref="uploadRef"
              class="upload-area"
              drag
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileChange"
              accept="image/*"
            >
              <div v-if="!previewImage" class="upload-placeholder">
                <el-icon :size="64" color="#3B82F6"><Upload /></el-icon>
                <div class="upload-text">
                  <p>将题目图片拖到此处</p>
                  <p>或<em>点击上传</em></p>
                </div>
              </div>
              <div v-else class="preview-container">
                <img :src="previewImage" alt="题目预览" />
                <div class="preview-overlay">
                  <el-button type="primary" round @click.stop="clearImage">
                    <el-icon><RefreshRight /></el-icon>
                    重新上传
                  </el-button>
                </div>
              </div>
            </el-upload>

            <div class="actions">
              <el-button
                type="primary"
                size="large"
                round
                :disabled="!selectedFile"
                :loading="solving"
                @click="solveQuestion"
              >
                <el-icon><Search /></el-icon>
                开始解题
              </el-button>
            </div>

            <!-- 支持的学科 -->
            <div class="subjects-section">
              <h4>支持学科</h4>
              <div class="subject-tags">
                <el-tag effect="plain" size="large">
                  <el-icon :size="16"><DataAnalysis /></el-icon>
                  数学
                </el-tag>
                <el-tag effect="plain" type="success" size="large">
                  <el-icon :size="16"><Compass /></el-icon>
                  物理
                </el-tag>
                <el-tag effect="plain" type="warning" size="large">
                  <el-icon :size="16"><Document /></el-icon>
                  化学
                </el-tag>
                <el-tag effect="plain" type="info" size="large">
                  <el-icon :size="16"><Reading /></el-icon>
                  语文
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：结果区域 -->
        <div class="result-section">
          <!-- 解答结果 -->
          <div class="result-card" v-if="result">
            <div class="result-header">
              <div class="result-icon">
                <el-icon :size="28"><Document /></el-icon>
              </div>
              <div class="header-info">
                <h3>解答结果</h3>
                <el-tag v-if="!result.success" type="warning" size="small">模拟数据</el-tag>
                <el-tag v-else type="success" size="small">{{ result.provider }}</el-tag>
              </div>
            </div>

            <!-- 题目内容 -->
            <div class="question-section">
              <h4>
                <el-icon :size="18" color="#3B82F6"><EditPen /></el-icon>
                题目内容
              </h4>
              <div class="question-content">
                {{ result.question_text }}
              </div>
            </div>

            <el-divider />

            <!-- 答案 -->
            <div class="answer-section">
              <h4>
                <el-icon :size="18" color="#10B981"><CircleCheck /></el-icon>
                最终答案
              </h4>
              <div class="answer-content">
                {{ result.answer }}
              </div>
            </div>

            <el-divider />

            <!-- 解题步骤 -->
            <div class="steps-section" v-if="result.steps.length > 0">
              <h4>
                <el-icon :size="18" color="#F59E0B"><List /></el-icon>
                解题步骤
              </h4>
              <el-steps direction="vertical" :active="result.steps.length" finish-status="success">
                <el-step
                  v-for="(step, index) in result.steps"
                  :key="index"
                  :title="`步骤 ${index + 1}`"
                  :description="step"
                />
              </el-steps>
            </div>

            <el-divider v-if="result.steps.length > 0" />

            <!-- 知识点 -->
            <div class="knowledge-section" v-if="result.knowledge_points.length > 0">
              <h4>
                <el-icon :size="18" color="#8B5CF6"><Lightning /></el-icon>
                涉及知识点
              </h4>
              <div class="knowledge-tags">
                <el-tag
                  v-for="(point, index) in result.knowledge_points"
                  :key="index"
                  type="success"
                  effect="light"
                  size="large"
                >
                  {{ point }}
                </el-tag>
              </div>
            </div>

            <!-- 错误提示 -->
            <div v-if="result.error" class="error-section">
              <el-alert type="warning" :title="result.error" :closable="false" show-icon />
            </div>
          </div>

          <!-- 无结果时的提示 -->
          <div class="result-card empty" v-else>
            <el-icon :size="80" color="#94A3B8"><EditPen /></el-icon>
            <p>上传题目图片后点击解题</p>
            <p class="tip">AI将自动识别题目并给出详细解答</p>
          </div>

          <!-- 使用提示 -->
          <div class="tips-card">
            <h4>
              <el-icon><InfoFilled /></el-icon>
              使用提示
            </h4>
            <ul>
              <li>请确保题目图片清晰，文字可辨认</li>
              <li>建议使用横向拍摄，避免文字倾斜</li>
              <li>复杂题目可能需要更长的解答时间</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Camera, RefreshRight, InfoFilled, Upload, Search, DataAnalysis,
  Compass, Document, Reading, EditPen, CircleCheck, List, Lightning
} from '@element-plus/icons-vue'
import { questionApi } from '../api'
import Navbar from '../components/Navbar.vue'
import type { UploadFile } from 'element-plus'

interface AnswerResult {
  question_text: string
  answer: string
  steps: string[]
  knowledge_points: string[]
  success: boolean
  error?: string
  provider?: string
}

const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const previewImage = ref<string>('')
const solving = ref(false)
const result = ref<AnswerResult | null>(null)

const handleFileChange = (uploadFile: UploadFile) => {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
    previewImage.value = URL.createObjectURL(uploadFile.raw)
    result.value = null
  }
}

const clearImage = () => {
  selectedFile.value = null
  previewImage.value = ''
  result.value = null
}

const solveQuestion = async () => {
  if (!selectedFile.value) return

  solving.value = true
  ElMessage.info('正在识别题目...')

  try {
    const data = await questionApi.solve(selectedFile.value)
    result.value = data

    if (!data.success) {
      ElMessage.warning('当前为模拟数据，请配置AI API')
    } else {
      ElMessage.success('题目解答完成！')
    }
  } catch (error) {
    ElMessage.error('解题失败，请重试')
    console.error('Solve error:', error)
  } finally {
    solving.value = false
  }
}
</script>

<style scoped>
.question-page {
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

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 30px;
}

/* Upload Section */
.upload-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.upload-header {
  text-align: center;
  margin-bottom: 25px;
}

.header-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto;
}

.upload-header h3 {
  color: #1E293B;
  margin-top: 15px;
  font-weight: 600;
}

.upload-header p {
  color: #64748B;
  font-size: 14px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #3B82F6;
  border-radius: 16px;
  background: #EFF6FF;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #1D4ED8;
  background: #DBEAFE;
}

.upload-placeholder {
  text-align: center;
}

.upload-text {
  margin-top: 20px;
  color: #475569;
}

.upload-text em {
  color: #3B82F6;
  font-style: normal;
  font-weight: 600;
}

.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container img {
  max-width: 100%;
  max-height: 220px;
  object-fit: contain;
  border-radius: 10px;
}

.preview-overlay {
  position: absolute;
  bottom: 15px;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 25px;
}

.subjects-section {
  margin-top: 25px;
  padding: 20px;
  background: #F8FAFC;
  border-radius: 12px;
}

.subjects-section h4 {
  color: #475569;
  margin-bottom: 15px;
  font-weight: 500;
}

.subject-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.subject-tags .el-tag {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Result Section */
.result-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
  min-height: 400px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 20px;
  border-bottom: 2px solid #EFF6FF;
}

.result-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-info h3 {
  color: #1E293B;
  margin: 0;
}

.question-section,
.answer-section,
.steps-section,
.knowledge-section {
  margin-top: 20px;
}

.question-section h4,
.answer-section h4,
.steps-section h4,
.knowledge-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1E293B;
  margin-bottom: 15px;
  font-weight: 600;
}

.question-content {
  background: #F8FAFC;
  padding: 15px;
  border-radius: 12px;
  color: #475569;
  line-height: 1.6;
}

.answer-content {
  background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
  padding: 15px;
  border-radius: 12px;
  color: #1E293B;
  font-size: 18px;
  font-weight: 600;
}

.knowledge-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.error-section {
  margin-top: 20px;
}

.result-card.empty {
  text-align: center;
  padding: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.result-card.empty p {
  color: #475569;
  margin-top: 20px;
}

.result-card.empty .tip {
  color: #94A3B8;
  font-size: 14px;
}

/* Tips Card */
.tips-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-top: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.tips-card h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #3B82F6;
  margin-bottom: 15px;
  font-weight: 600;
}

.tips-card ul {
  list-style: none;
  padding: 0;
}

.tips-card li {
  padding: 10px 0;
  color: #475569;
  border-bottom: 1px dashed #E2E8F0;
}

.tips-card li:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>