import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authAPI } from '@/services/api'

export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  created_at: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const tokenExpiry = ref<number | null>(null)
  const loading = ref(false)
  const isInitialized = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => {
    if (!token.value || !user.value) return false
    // 检查token是否过期
    if (tokenExpiry.value && Date.now() > tokenExpiry.value) {
      clearAuth()
      return false
    }
    return true
  })

  // 监听token变化，同步到localStorage
  watch(token, (newToken) => {
    if (newToken) {
      localStorage.setItem('access_token', newToken)
    } else {
      localStorage.removeItem('access_token')
    }
  }, { immediate: false })

  // 设置token和过期时间
  const setToken = (newToken: string, expiresIn?: number) => {
    token.value = newToken
    // 设置token过期时间（默认24小时）
    const expiry = expiresIn ? Date.now() + (expiresIn * 1000) : Date.now() + (24 * 60 * 60 * 1000)
    tokenExpiry.value = expiry
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('token_expiry', expiry.toString())
  }

  // 清除token
  const clearToken = () => {
    token.value = null
    tokenExpiry.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_expiry')
  }

  // 设置用户信息
  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user_info', JSON.stringify(userData))
  }

  // 清除用户信息
  const clearUser = () => {
    user.value = null
    localStorage.removeItem('user_info')
  }

  // 清除所有认证信息
  const clearAuth = () => {
    clearToken()
    clearUser()
  }

  // 用户注册
  const register = async (userData: {
    username: string
    email: string
    password: string
  }) => {
    try {
      loading.value = true
      const response = await authAPI.register(userData)
      
      if (response.access_token) {
        setToken(response.access_token)
        setUser(response.user)
      }
      
      return response
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  // 用户登录
  const login = async (credentials: {
    email: string
    password: string
  }) => {
    try {
      loading.value = true
      const response = await authAPI.login(credentials)
      
      if (response.access_token) {
        setToken(response.access_token, response.expires_in)
        // 登录成功后获取用户信息
        await fetchCurrentUser()
      }
      
      return response
    } catch (error) {
      clearAuth()
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!token.value) return
    
    try {
      loading.value = true
      const response = await authAPI.getCurrentUser()
      setUser(response)
      return response
    } catch (error) {
      // 如果获取用户信息失败，清除token
      clearToken()
      clearUser()
      throw error
    } finally {
      loading.value = false
    }
  }

  // 用户登出
  const logout = async () => {
    try {
      loading.value = true
      
      // 如果有token，尝试调用后端登出API
      if (token.value) {
        try {
          await authAPI.logout()
        } catch (error) {
          console.error('后端登出请求失败:', error)
          // 即使后端登出失败，也要清理本地状态
        }
      }
    } finally {
      // 清理所有认证相关状态
      clearAuth()
      loading.value = false
      
      // 清理可能的其他本地存储数据
      try {
        // 清理可能存在的其他认证相关数据
        const keysToRemove = ['user_preferences', 'chat_history', 'temp_data']
        keysToRemove.forEach(key => {
          if (localStorage.getItem(key)) {
            localStorage.removeItem(key)
          }
        })
        
        // 清理sessionStorage中的临时数据
        sessionStorage.clear()
      } catch (error) {
        console.error('清理本地存储失败:', error)
      }
      
      // 使用路由跳转而不是直接修改location
      if (typeof window !== 'undefined' && window.location.pathname !== '/') {
        // 延迟跳转，确保状态清理完成
        setTimeout(() => {
          window.location.href = '/'
        }, 100)
      }
    }
  }

  // 检查token是否有效
  const checkTokenValidity = () => {
    if (!token.value) return false
    if (tokenExpiry.value && Date.now() > tokenExpiry.value) {
      clearAuth()
      return false
    }
    return true
  }

  // 初始化用户状态
  const initializeAuth = async () => {
    if (isInitialized.value) return
    
    try {
      // 从localStorage恢复token过期时间
      const storedExpiry = localStorage.getItem('token_expiry')
      if (storedExpiry) {
        tokenExpiry.value = parseInt(storedExpiry)
      }
      
      // 从localStorage恢复用户信息
      const storedUser = localStorage.getItem('user_info')
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser)
        } catch (e) {
          localStorage.removeItem('user_info')
        }
      }
      
      // 检查token有效性
      if (token.value && checkTokenValidity()) {
        try {
          // 验证token并获取最新用户信息
          await fetchCurrentUser()
        } catch (error) {
          console.error('初始化用户状态失败:', error)
          clearAuth()
        }
      } else {
        clearAuth()
      }
    } finally {
      isInitialized.value = true
    }
  }

  // 刷新token（如果后端支持）
  const refreshToken = async () => {
    if (!token.value) return false
    
    try {
      // 这里可以调用刷新token的API
      // const response = await authAPI.refreshToken()
      // setToken(response.access_token, response.expires_in)
      return true
    } catch (error) {
      console.error('刷新token失败:', error)
      clearAuth()
      return false
    }
  }

  return {
    // 状态
    user,
    token,
    tokenExpiry,
    loading,
    isInitialized,
    
    // 计算属性
    isLoggedIn,
    
    // 方法
    setToken,
    clearToken,
    setUser,
    clearUser,
    clearAuth,
    register,
    login,
    logout,
    fetchCurrentUser,
    initializeAuth,
    checkTokenValidity,
    refreshToken,
  }
})