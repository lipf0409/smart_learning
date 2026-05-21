<template>
  <div class="chat-page">
    <Navbar />

    <div class="page-container">
      <el-page-header @back="$router.push('/')">
        <template #content>
          <span class="page-title">
            <el-icon><ChatDotRound /></el-icon>
            AI答疑助手
          </span>
        </template>
      </el-page-header>

      <div class="chat-content">
        <!-- 左侧：学科选择 -->
        <div class="sidebar">
          <div class="subject-card">
            <h3>
              <el-icon :size="24" color="#3B82F6"><Reading /></el-icon>
              选择学科
            </h3>

            <div class="subject-list">
              <div
                v-for="subject in subjects"
                :key="subject.name"
                class="subject-item"
                :class="{ active: currentSubject === subject.name }"
                @click="selectSubject(subject.name)"
              >
                <el-icon :size="20">
                  <component :is="subject.icon" />
                </el-icon>
                <span>{{ subject.name }}</span>
              </div>
            </div>
          </div>

          <!-- 提示说明 -->
          <div class="tips-card">
            <h4>
              <el-icon><InfoFilled /></el-icon>
              启发式教学说明
            </h4>
            <ul>
              <li>AI会引导你思考，而非直接给答案</li>
              <li>请尝试自己推导结论</li>
              <li>多次尝试后可获得更多提示</li>
            </ul>
          </div>
        </div>

        <!-- 右侧：聊天区域 -->
        <div class="chat-area">
          <div class="chat-header">
            <div class="ai-avatar">
              <el-icon :size="32"><Cpu /></el-icon>
            </div>
            <div class="header-info">
              <h3>智能答疑助手</h3>
              <p>当前学科: {{ currentSubject }}</p>
            </div>
          </div>

          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <!-- AI欢迎消息 -->
            <div class="message ai-message">
              <div class="avatar ai-avatar-small">
                <el-icon :size="20"><Cpu /></el-icon>
              </div>
              <div class="message-content">
                <p>你好！我是你的学习助手。请告诉我你遇到的问题，我会引导你思考解决。</p>
                <p class="hint-text">提示：我会用启发式方式帮助你，让你自己找到答案。</p>
              </div>
            </div>

            <!-- 历史消息 -->
            <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.role">
              <div class="avatar" :class="msg.role === 'user' ? 'user-avatar' : 'ai-avatar-small'">
                <el-icon :size="20">
                  <component :is="msg.role === 'user' ? 'User' : 'Cpu'" />
                </el-icon>
              </div>
              <div class="message-content">
                <p>{{ msg.content }}</p>

                <!-- AI回复的提示和知识点 -->
                <div v-if="msg.role === 'ai' && msg.hints" class="hints-section">
                  <h5>
                    <el-icon><Sunny /></el-icon>
                    思考提示
                  </h5>
                  <div class="hints-list">
                    <el-tag v-for="(hint, i) in msg.hints" :key="i" type="warning" effect="light">
                      {{ hint }}
                    </el-tag>
                  </div>
                </div>

                <div v-if="msg.role === 'ai' && msg.knowledge" class="knowledge-section">
                  <h5>
                    <el-icon><Reading /></el-icon>
                    相关知识点
                  </h5>
                  <div class="knowledge-list">
                    <el-tag v-for="(k, i) in msg.knowledge" :key="i" type="success" effect="light">
                      {{ k }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="message ai-message">
              <div class="avatar ai-avatar-small">
                <el-icon :size="20"><Cpu /></el-icon>
              </div>
              <div class="message-content loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在思考...</span>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="inputMessage"
              placeholder="输入你的问题..."
              size="large"
              @keyup.enter="sendMessage"
            >
              <template #prefix>
                <el-icon><EditPen /></el-icon>
              </template>
            </el-input>

            <el-button type="primary" size="large" round @click="sendMessage" :disabled="!inputMessage || loading">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>

            <el-button size="large" round @click="clearChat">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound, InfoFilled, Sunny, Reading, Loading, EditPen, Delete,
  Promotion, Cpu, User, DataAnalysis, Compass, Document, Collection
} from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'
import { learningApi } from '../api'

interface Message {
  role: 'user' | 'ai'
  content: string
  hints?: string[]
  knowledge?: string[]
}

const subjects = [
  { name: '数学', icon: 'DataAnalysis' },
  { name: '物理', icon: 'Compass' },
  { name: '化学', icon: 'Document' },
  { name: '语文', icon: 'Reading' },
  { name: '英语', icon: 'Collection' }
]

const currentSubject = ref('数学')
const inputMessage = ref('')
const messages = ref<Message[]>([])
const loading = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

const selectSubject = (subject: string) => {
  currentSubject.value = subject
  messages.value = []
  ElMessage.success(`已切换到${subject}学科`)
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: inputMessage.value
  })

  const userQuestion = inputMessage.value
  inputMessage.value = ''

  loading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 构建历史对话
    const history = messages.value.slice(-6).map(m => ({
      role: m.role === 'user' ? 'user' : 'assistant',
      content: m.content
    }))

    // 调用真实API
    const response = await learningApi.chat(userQuestion, currentSubject.value, history)

    messages.value.push({
      role: 'ai',
      content: response.response,
      hints: response.hints || [],
      knowledge: response.related_knowledge || []
    })

  } catch (error: any) {
    console.error('AI回复失败:', error)
    ElMessage.error(error.message || 'AI回复失败，请重试')
    // 移除用户消息
    messages.value.pop()
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const clearChat = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}
</script>

<style scoped>
.chat-page {
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

.chat-content {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 30px;
  margin-top: 30px;
  height: calc(100vh - 150px);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.subject-card, .tips-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
}

.subject-card h3, .tips-card h4 {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1E293B;
  margin-bottom: 15px;
  font-weight: 600;
}

.subject-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subject-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #475569;
}

.subject-item:hover {
  background: #EFF6FF;
  color: #3B82F6;
}

.subject-item.active {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  color: white;
}

.tips-card ul {
  list-style: none;
  padding: 0;
}

.tips-card li {
  padding: 8px 0;
  color: #64748B;
  font-size: 14px;
}

.chat-area {
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #E2E8F0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
}

.ai-avatar {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-info h3 {
  color: white;
  margin: 0;
}

.header-info p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 4px 0 0;
}

.message-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 15px;
  max-width: 80%;
}

.message.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai-message {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-avatar-small {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  color: white;
}

.user-avatar {
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
}

.message-content {
  padding: 15px 20px;
  border-radius: 16px;
  max-width: 100%;
}

.user-message .message-content {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8);
  color: white;
}

.ai-message .message-content {
  background: #F1F5F9;
  color: #1E293B;
}

.message-content p {
  line-height: 1.6;
  margin: 0;
}

.hint-text {
  color: #64748B;
  font-size: 14px;
  margin-top: 10px !important;
}

.hints-section, .knowledge-section {
  margin-top: 15px;
}

.hints-section h5, .knowledge-section h5 {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #475569;
  margin-bottom: 10px;
  font-size: 13px;
}

.hints-list, .knowledge-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.message-content.loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-area {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: #F8FAFC;
  border-top: 1px solid #E2E8F0;
}

.input-area .el-input {
  flex: 1;
}

@media (max-width: 768px) {
  .chat-content {
    grid-template-columns: 1fr;
    height: auto;
  }

  .sidebar {
    order: 2;
  }

  .chat-area {
    order: 1;
    min-height: 400px;
  }
}
</style>