import axios from 'axios'

// API base URLs
const AI_SERVICE_URL = 'http://localhost:8000'
const BACKEND_URL = 'http://localhost:8080'

// AI Service API
export const aiApi = axios.create({
  baseURL: AI_SERVICE_URL,
  timeout: 60000  // 增加超时时间，AI响应可能较慢
})

// Backend API
export const backendApi = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000
})

// Add auth token to backend requests
backendApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Posture detection API
export const postureApi = {
  detect: async (imageFile: File) => {
    const formData = new FormData()
    formData.append('file', imageFile)
    const response = await aiApi.post('/api/posture/detect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}

// Question solving API
export const questionApi = {
  solve: async (imageFile: File) => {
    const formData = new FormData()
    formData.append('file', imageFile)
    const response = await aiApi.post('/api/question/solve', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}

// Learning API - AI答疑、学习报告等
export const learningApi = {
  // AI启发式答疑
  chat: async (question: string, subject: string, history?: Array<{role: string, content: string}>) => {
    const response = await aiApi.post('/api/learning/chat', {
      question,
      subject,
      history: history || []
    })
    return response.data
  },

  // 获取聊天记录
  getChatRecords: async (limit: number = 20) => {
    const response = await aiApi.get('/api/learning/records', {
      params: { limit }
    })
    return response.data
  },

  // 获取学习统计
  getStats: async () => {
    const response = await aiApi.get('/api/learning/stats')
    return response.data
  },

  // 生成学习报告
  analyze: async (records?: Array<{
    question_text: string
    subject: string
    knowledge_points: string[]
    success: boolean
    timestamp: string
  }>) => {
    const response = await aiApi.post('/api/learning/analyze', records || [])
    return response.data
  },

  // 生成学习计划
  generatePlan: async (
    weakPoints: string[],
    strongPoints: string[],
    availableHours: number,
    goal: string
  ) => {
    const params = new URLSearchParams()
    weakPoints.forEach(p => params.append('weak_points', p))
    strongPoints.forEach(p => params.append('strong_points', p))
    params.append('available_hours', availableHours.toString())
    params.append('goal', goal)
    const response = await aiApi.post('/api/learning/plan', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
  }
}

// RAG API - 知识库管理(预留)
export const ragApi = {
  // 搜索知识
  search: async (query: string, topK: number = 3) => {
    const response = await aiApi.get('/api/rag/search', {
      params: { query, top_k: topK }
    })
    return response.data
  },

  // 添加知识
  addKnowledge: async (title: string, content: string, subject?: string) => {
    const response = await aiApi.post('/api/rag/knowledge', {
      title,
      content,
      subject
    })
    return response.data
  }
}

// Auth API
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await backendApi.post('/api/auth/login', { username, password })
    return response.data
  },
  register: async (username: string, password: string, email: string) => {
    const response = await backendApi.post('/api/auth/register', { username, password, email })
    return response.data
  }
}
