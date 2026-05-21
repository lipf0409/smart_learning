<template>
  <div class="posture-page">
    <Navbar />

    <div class="page-container">
      <el-page-header @back="$router.push('/')">
        <template #content>
          <span class="page-title">
            <el-icon><Monitor /></el-icon>
            坐姿检测
          </span>
        </template>
      </el-page-header>

      <div class="content-grid">
        <!-- 左侧：摄像头区域 -->
        <div class="camera-section">
          <div class="camera-card">
            <div class="video-container">
              <!-- 显示处理后的视频帧 - 使用 key 强制刷新 -->
              <img
                v-if="processedFrame"
                :key="frameKey"
                :src="'data:image/jpeg;base64,' + processedFrame"
                class="processed-frame"
              />

              <!-- 原始摄像头 -->
              <video ref="videoRef" autoplay playsinline :class="{ hidden: streaming }"></video>
              <canvas ref="canvasRef" style="display: none;"></canvas>

              <div v-if="!cameraActive" class="camera-placeholder">
                <el-icon :size="64"><VideoCamera /></el-icon>
                <p>点击下方按钮开启摄像头</p>
              </div>

              <!-- 实时状态指示器 -->
              <div v-if="streaming" class="live-indicator">
                <span class="live-dot"></span>
                <span>实时检测中</span>
              </div>

              <!-- 当前状态显示 -->
              <div v-if="currentStatus && streaming" class="status-overlay" :class="currentStatus">
                <span>{{ currentMessage }}</span>
              </div>
            </div>

            <div class="controls">
              <el-button
                v-if="!cameraActive"
                type="primary"
                size="large"
                round
                @click="startCamera"
              >
                <el-icon class="btn-icon"><VideoCamera /></el-icon>
                开启摄像头
              </el-button>

              <el-button
                v-else-if="!streaming"
                type="success"
                size="large"
                round
                @click="startStreaming"
              >
                <el-icon><VideoPlay /></el-icon>
                开始检测
              </el-button>

              <el-button
                v-if="streaming"
                type="danger"
                size="large"
                round
                @click="stopStreaming"
              >
                <el-icon><VideoPause /></el-icon>
                停止检测
              </el-button>

              <el-button
                v-if="cameraActive"
                type="warning"
                size="large"
                round
                @click="stopCamera"
              >
                <el-icon><SwitchButton /></el-icon>
                关闭摄像头
              </el-button>
            </div>

            <!-- 检测模式说明 -->
            <div class="mode-info">
              <el-alert
                title="检测模式"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <p>基于 OpenVINO 人体姿态估计，实时检测坐姿状态</p>
                  <p>可识别：耸肩、低头、歪头等不良坐姿</p>
                </template>
              </el-alert>
            </div>
          </div>
        </div>

        <!-- 右侧：结果区域 -->
        <div class="result-section">
          <!-- 当前检测结果 -->
          <div class="result-card" v-if="result">
            <div class="result-header" :class="result.status">
              <el-icon :size="96" :class="result.status + '-icon'">
                <CircleCheck v-if="result.status === 'good'" />
                <Warning v-else-if="result.status === 'bad'" />
                <QuestionFilled v-else />
              </el-icon>
              <div class="status-info">
                <h3>{{ statusText }}</h3>
                <p class="message">{{ result.message }}</p>
              </div>
            </div>

            <!-- 关键点信息 -->
            <div class="keypoints-section" v-if="result.key_points && result.key_points.length > 0">
              <h4>
                <el-icon><Aim /></el-icon>
                检测到的关键点
              </h4>
              <div class="keypoints-grid">
                <div v-for="kp in result.key_points" :key="kp.name" class="keypoint-item">
                  <span class="kp-name">{{ getKeyName(kp.name) }}</span>
                  <span class="kp-conf">{{ (kp.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <div class="tips-section">
              <h4>
                <el-icon><InfoFilled /></el-icon>
                健康提示
              </h4>
              <ul v-if="result.status === 'bad'">
                <li v-if="result.gesture_type?.includes('耸肩')">放松肩膀，避免长时间耸肩</li>
                <li v-if="result.gesture_type?.includes('低头')">调整屏幕高度，保持视线水平</li>
                <li v-if="result.gesture_type?.includes('歪头')">保持头部端正，避免侧倾</li>
                <li>背部挺直，双脚平放地面</li>
              </ul>
              <p v-else-if="result.status === 'good'" class="good-tip">继续保持良好的坐姿习惯！</p>
              <p v-else>正在检测中...</p>
            </div>
          </div>

          <!-- 无结果时的提示 -->
          <div class="result-card empty" v-else>
            <el-icon :size="120" color="#94A3B8"><VideoPause /></el-icon>
            <p>暂无检测结果</p>
            <p class="tip">请开启摄像头并点击开始检测</p>
          </div>

          <!-- 检测历史 -->
          <div class="history-card" v-if="history.length > 0">
            <div class="history-header">
              <h4>
                <el-icon><Clock /></el-icon>
                检测历史
              </h4>
              <el-tag type="info" size="small">最近10次</el-tag>
            </div>

            <div class="history-list">
              <div
                v-for="(item, index) in history.slice(-10)"
                :key="index"
                class="history-item"
                :class="item.status"
              >
                <el-icon :size="32" :class="item.status + '-icon'">
                  <CircleCheck v-if="item.status === 'good'" />
                  <Warning v-else />
                </el-icon>
                <div class="history-info">
                  <span class="history-status">{{ item.status === 'good' ? '良好' : '不良' }}</span>
                  <span class="history-time">{{ item.time }}</span>
                </div>
                <span class="history-message">{{ item.message }}</span>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="stats-row">
              <div class="stat-item">
                <span class="stat-label">良好次数</span>
                <span class="stat-value good">{{ goodCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">不良次数</span>
                <span class="stat-value bad">{{ badCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">达标率</span>
                <span class="stat-value">{{ passRate }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, VideoPlay, VideoPause, SwitchButton, Clock, InfoFilled, Aim, VideoCamera, CircleCheck, Warning, QuestionFilled } from '@element-plus/icons-vue'
import Navbar from '../components/Navbar.vue'

interface PostureResult {
  status: string
  message: string
  gesture_type?: string
  key_points?: Array<{ name: string; x: number; y: number; confidence: number }>
}

interface HistoryItem {
  status: string
  message: string
  time: string
}

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const cameraActive = ref(false)
const streaming = ref(false)
const result = ref<PostureResult | null>(null)
const history = ref<HistoryItem[]>([])
const processedFrame = ref<string | null>(null)
const currentStatus = ref<string | null>(null)
const currentMessage = ref<string>('')
const frameKey = ref(0)  // 用于强制刷新图片

let stream: MediaStream | null = null
let ws: WebSocket | null = null
let frameInterval: number | null = null

const statusText = computed(() => {
  if (!result.value) return ''
  switch (result.value.status) {
    case 'good': return '坐姿良好'
    case 'bad': return '坐姿不良'
    default: return '检测中'
  }
})

const goodCount = computed(() => history.value.filter(h => h.status === 'good').length)
const badCount = computed(() => history.value.filter(h => h.status === 'bad').length)
const passRate = computed(() => {
  const total = history.value.length
  if (total === 0) return 0
  return Math.round((goodCount.value / total) * 100)
})

const keyNameMap: Record<string, string> = {
  nose: '鼻子',
  r_eye: '右眼',
  l_eye: '左眼',
  r_ear: '右耳',
  l_ear: '左耳',
  r_shoulder: '右肩',
  l_shoulder: '左肩'
}

const getKeyName = (name: string) => keyNameMap[name] || name

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 640, height: 480 }
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraActive.value = true
      ElMessage.success('摄像头已开启')
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
    console.error('Camera error:', error)
  }
}

const stopCamera = () => {
  stopStreaming()
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  cameraActive.value = false
  processedFrame.value = null
  ElMessage.info('摄像头已关闭')
}

const startStreaming = () => {
  if (!cameraActive.value) {
    ElMessage.warning('请先开启摄像头')
    return
  }

  // 如果已经有WebSocket连接，先关闭
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('Closing existing WebSocket connection')
    ws.close()
    ws = null
  }

  // Connect to WebSocket - 使用动态URL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = '127.0.0.1:8000'  // 后端服务地址
  const wsUrl = `${protocol}//${host}/api/posture/stream`
  console.log('Connecting to WebSocket:', wsUrl)

  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    streaming.value = true
    ElMessage.success('实时检测已开启')
    console.log('WebSocket connected, starting frame capture...')

    // Start sending frames
    frameInterval = window.setInterval(sendFrame, 100) // 10 FPS
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      if (data.status === 'error') {
        console.error('Detection error:', data.message)
        return
      }

      // Update result
      result.value = {
        status: data.status,
        message: data.message,
        gesture_type: data.gesture_type,
        key_points: data.key_points
      }

      // Update current status for overlay
      currentStatus.value = data.status
      currentMessage.value = data.message

      // Update processed frame - this creates the "video" effect
      if (data.frame) {
        processedFrame.value = data.frame
        frameKey.value++  // 强制刷新图片
      }

      // Add to history (throttled)
      if (data.status !== 'unknown') {
        const now = new Date()
        const lastHistory = history.value[history.value.length - 1]
        const lastTime = lastHistory ? new Date(lastHistory.time).getTime() : 0

        // Only add if more than 1 second passed
        if (now.getTime() - lastTime > 1000) {
          history.value.push({
            status: data.status,
            message: data.message,
            time: now.toLocaleTimeString()
          })
        }
      }

    } catch (e) {
      console.error('Parse error:', e)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    ElMessage.error('连接失败，请检查服务是否启动')
    streaming.value = false
  }

  ws.onclose = (event) => {
    console.log('WebSocket closed, code:', event.code, 'reason:', event.reason)
    streaming.value = false
    if (frameInterval) {
      clearInterval(frameInterval)
      frameInterval = null
    }
  }
}

const stopStreaming = () => {
  if (frameInterval) {
    clearInterval(frameInterval)
    frameInterval = null
  }

  if (ws) {
    ws.close()
    ws = null
  }

  streaming.value = false
  currentStatus.value = null
  ElMessage.info('实时检测已停止')
}

const sendFrame = () => {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.log('WebSocket not ready, state:', ws?.readyState)
    return
  }
  if (!videoRef.value || !canvasRef.value) {
    console.log('Video or canvas not ready')
    return
  }

  const canvas = canvasRef.value
  const video = videoRef.value

  // Check video dimensions
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    console.log('Video dimensions not ready:', video.videoWidth, video.videoHeight)
    return
  }

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.drawImage(video, 0, 0)

  // Send as base64
  const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
  ws.send(dataUrl)
  // console.log('Frame sent, size:', dataUrl.length)  // 减少日志
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.posture-page {
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

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 30px;
}

.camera-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
}

.video-container {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-container video.hidden {
  display: none;
}

.processed-frame {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.camera-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4A90E2, #2E6AB3);
}

.camera-placeholder img {
  width: 80px;
  height: 80px;
}

.camera-placeholder p {
  color: white;
  margin-top: 15px;
}

.live-indicator {
  position: absolute;
  top: 15px;
  left: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 15px;
  border-radius: 20px;
  color: white;
  z-index: 10;
}

.live-dot {
  width: 10px;
  height: 10px;
  background: #F56C6C;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.status-overlay {
  position: absolute;
  bottom: 15px;
  left: 15px;
  right: 15px;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: bold;
  z-index: 10;
}

.status-overlay.good {
  background: rgba(103, 194, 58, 0.9);
  color: white;
}

.status-overlay.bad {
  background: rgba(245, 108, 108, 0.9);
  color: white;
}

.controls {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-icon {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}

.mode-info {
  margin-top: 20px;
}

.mode-info p {
  margin: 5px 0;
  font-size: 13px;
}

/* Result Section */
.result-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 15px;
}

.result-header.good {
  background: linear-gradient(135deg, #E8F8E8, #67C23A);
}

.result-header.bad {
  background: linear-gradient(135deg, #FEF0F0, #F56C6C);
}

.result-header.unknown {
  background: linear-gradient(135deg, #F4F4F5, #909399);
}

.status-icon {
  width: 60px;
  height: 60px;
}

.good-icon {
  color: #67C23A;
}

.bad-icon {
  color: #F56C6C;
}

.unknown-icon {
  color: #909399;
}

.status-info h3 {
  font-size: 24px;
  margin-bottom: 5px;
}

.result-header.good h3 {
  color: #67C23A;
}

.result-header.bad h3 {
  color: #F56C6C;
}

.message {
  color: #606266;
}

.keypoints-section {
  margin-top: 20px;
  padding: 15px;
  background: #F5F9FC;
  border-radius: 10px;
}

.keypoints-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4A90E2;
  margin-bottom: 15px;
}

.keypoints-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.keypoint-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
}

.kp-name {
  color: #606266;
}

.kp-conf {
  color: #67C23A;
  font-weight: bold;
}

.tips-section {
  margin-top: 20px;
  padding: 20px;
  background: #F5F9FC;
  border-radius: 10px;
}

.tips-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4A90E2;
  margin-bottom: 15px;
}

.tips-section ul {
  list-style: none;
  padding: 0;
}

.tips-section li {
  padding: 8px 0;
  color: #606266;
  border-bottom: 1px dashed #E4E7ED;
}

.tips-section li:last-child {
  border-bottom: none;
}

.good-tip {
  color: #67C23A;
  font-weight: bold;
}

.result-card.empty {
  text-align: center;
  padding: 50px;
}

.result-card.empty img {
  width: 100px;
  height: 100px;
}

.result-card.empty p {
  color: #606266;
  margin-top: 15px;
}

.result-card.empty .tip {
  color: #909399;
  font-size: 14px;
}

/* History Card */
.history-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-top: 20px;
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.15);
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.history-header h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  border-radius: 10px;
}

.history-item.good {
  background: #E8F8E8;
}

.history-item.bad {
  background: #FEF0F0;
}

.history-item img {
  width: 24px;
  height: 24px;
}

.history-info {
  flex: 1;
}

.history-status {
  font-weight: bold;
}

.history-time {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.history-message {
  color: #606266;
  font-size: 12px;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #E4E7ED;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: #909399;
  font-size: 12px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #4A90E2;
}

.stat-value.good {
  color: #67C23A;
}

.stat-value.bad {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .controls {
    flex-wrap: wrap;
  }
}
</style>
