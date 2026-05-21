<template>
  <div class="navbar">
    <div class="navbar-left">
      <div class="logo" @click="$router.push('/')">
        <div class="logo-icon">
          <el-icon :size="24"><Reading /></el-icon>
        </div>
        <span class="logo-text">智能学习系统</span>
      </div>
    </div>

    <div class="navbar-center">
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        :ellipsis="false"
        @select="handleSelect"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/posture">
          <el-icon><Monitor /></el-icon>
          <span>坐姿检测</span>
        </el-menu-item>
        <el-menu-item index="/question">
          <el-icon><Camera /></el-icon>
          <span>拍照搜题</span>
        </el-menu-item>
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI答疑</span>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon><DataAnalysis /></el-icon>
          <span>学习报告</span>
        </el-menu-item>
        <el-menu-item index="/plan">
          <el-icon><Calendar /></el-icon>
          <span>学习计划</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="navbar-right">
      <template v-if="userStore.isLoggedIn()">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="36" class="user-avatar">
              <el-icon :size="20"><User /></el-icon>
            </el-avatar>
            <span class="username">{{ userStore.username }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="history">
                <el-icon><Clock /></el-icon>
                学习记录
              </el-dropdown-item>
              <el-dropdown-item command="admin" v-if="isAdmin">
                <el-icon><Setting /></el-icon>
                管理后台
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button type="primary" round @click="$router.push('/login')">
          <el-icon><UserFilled /></el-icon>
          登录
        </el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  HomeFilled, Monitor, Camera, User, UserFilled,
  Setting, SwitchButton, Clock, ChatDotRound, DataAnalysis, Calendar, Reading
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeIndex = computed(() => route.path)
const isAdmin = computed(() => userStore.username === 'admin')

const handleSelect = (index: string) => {
  router.push(index)
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'history':
      router.push('/history')
      break
    case 'admin':
      router.push('/admin')
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/')
      break
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 0 24px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
}

.navbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 12px;
}

.logo:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-left: 12px;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.navbar-center .el-menu {
  background: transparent;
  border: none;
}

.navbar-center .el-menu-item {
  color: var(--text-secondary, #475569) !important;
  background: transparent !important;
  border-bottom: none !important;
  font-weight: 500;
  padding: 0 16px;
  margin: 0 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.navbar-center .el-menu-item:hover {
  color: #3B82F6 !important;
  background: rgba(59, 130, 246, 0.08) !important;
}

.navbar-center .el-menu-item.is-active {
  color: #3B82F6 !important;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1)) !important;
  border-bottom: none !important;
}

.navbar-center .el-menu-item.is-active::after {
  content: '';
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: linear-gradient(90deg, #3B82F6, #8B5CF6);
  border-radius: 2px;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(139, 92, 246, 0.08));
  transition: all 0.3s ease;
}

.user-info:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15));
  transform: scale(1.02);
}

.user-avatar {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  color: white;
}

.username {
  color: var(--text-primary, #1E293B);
  margin-left: 10px;
  font-size: 14px;
  font-weight: 500;
}

.navbar-right .el-button {
  background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  font-weight: 500;
}

.navbar-right .el-button:hover {
  background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

/* 响应式 */
@media (max-width: 1024px) {
  .navbar-center .el-menu-item span {
    display: none;
  }

  .navbar-center .el-menu-item {
    padding: 0 12px;
  }
}

@media (max-width: 768px) {
  .logo-text {
    display: none;
  }

  .navbar-center {
    display: none;
  }
}
</style>