<template>
  <div class="login-page">
    <Navbar />

    <div class="login-container">
      <div class="login-card">
        <div class="card-header">
          <el-icon :size="80" color="#4A90E2"><User /></el-icon>
          <h2>{{ isLogin ? '登录' : '注册' }}</h2>
        </div>

        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="登录" name="login">
            <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="top">
              <el-form-item label="用户名" prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  round
                  class="submit-btn"
                  @click="handleLogin"
                  :loading="loading"
                >
                  <el-icon><UserFilled /></el-icon>
                  登录
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top">
              <el-form-item label="用户名" prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  prefix-icon="User"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  prefix-icon="Message"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请确认密码"
                  prefix-icon="Lock"
                  size="large"
                  show-password
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="success"
                  size="large"
                  round
                  class="submit-btn"
                  @click="handleRegister"
                  :loading="loading"
                >
                  <el-icon><UserFilled /></el-icon>
                  注册
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <div class="card-footer">
          <p>使用智能学习系统，开启高效学习之旅</p>
        </div>
      </div>

      <div class="login-image">
        <el-icon :size="200" color="#4A90E2"><Reading /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled, User, Reading } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { authApi } from '../api'
import Navbar from '../components/Navbar.vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const isLogin = ref(true)
const loading = ref(false)
const rememberMe = ref(false)

const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleTabChange = (name: string) => {
  isLogin.value = name === 'login'
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await authApi.login(loginForm.username, loginForm.password)
        if (result.success) {
          userStore.login(result.token, result.username, result.role)
          ElMessage.success('登录成功！')
          router.push('/')
        } else {
          ElMessage.error(result.message || '登录失败')
        }
      } catch (error) {
        ElMessage.error('登录失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await authApi.register(
          registerForm.username,
          registerForm.password,
          registerForm.email
        )
        if (result.success) {
          ElMessage.success('注册成功！请登录')
          activeTab.value = 'login'
          loginForm.username = registerForm.username
        } else {
          ElMessage.error(result.message || '注册失败')
        }
      } catch (error) {
        ElMessage.error('注册失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F4FD 0%, #F5F9FC 100%);
}

.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 1000px;
  margin: 50px auto;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 10px 40px rgba(74, 144, 226, 0.2);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  color: #4A90E2;
  margin-top: 15px;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  font-size: 18px;
}

.card-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #E4E7ED;
}

.card-footer p {
  color: #909399;
  font-size: 14px;
}

.login-image {
  margin-left: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-card {
    width: 100%;
    max-width: 400px;
  }

  .login-image {
    margin-left: 0;
    margin-top: 30px;
  }
}
</style>