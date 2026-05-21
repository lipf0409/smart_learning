import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Posture from '../views/Posture.vue'
import Question from '../views/Question.vue'
import Login from '../views/Login.vue'
import Admin from '../views/Admin.vue'
import Report from '../views/Report.vue'
import Plan from '../views/Plan.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/posture',
    name: 'Posture',
    component: Posture
  },
  {
    path: '/question',
    name: 'Question',
    component: Question
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAdmin: true }
  },
  {
    path: '/report',
    name: 'Report',
    component: Report
  },
  {
    path: '/plan',
    name: 'Plan',
    component: Plan
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // 不需要登录的页面
  const publicPages = ['/', '/login']
  const isPublicPage = publicPages.includes(to.path)

  // 需要管理员权限的页面
  if (to.meta.requiresAdmin) {
    // 先检查是否登录
    if (!token) {
      next('/login')
      return
    }
    // 再检查是否是管理员
    if (role !== 'admin') {
      next('/')
      return
    }
    next()
    return
  }

  // 非公开页面需要登录
  if (!isPublicPage && !token) {
    next('/login')
    return
  }

  // 已登录用户访问登录页，跳转到首页
  if (to.path === '/login' && token) {
    next('/')
    return
  }

  next()
})

export default router