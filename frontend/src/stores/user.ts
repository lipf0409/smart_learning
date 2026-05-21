import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const username = ref<string>(localStorage.getItem('username') || '')
  const role = ref<string>(localStorage.getItem('role') || '')

  const isLoggedIn = () => !!token.value

  const isAdmin = () => role.value === 'admin'

  const login = (newToken: string, name: string, userRole?: string) => {
    token.value = newToken
    username.value = name
    role.value = userRole || 'user'
    localStorage.setItem('token', newToken)
    localStorage.setItem('username', name)
    localStorage.setItem('role', role.value)
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    role.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
  }

  return { token, username, role, isLoggedIn, isAdmin, login, logout }
})
