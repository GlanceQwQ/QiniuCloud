import axios from 'axios'
import type { AxiosError } from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 用于避免循环导入的延迟获取store
let getUserStore: (() => any) | null = null

// 设置store获取函数
export const setUserStoreGetter = (getter: () => any) => {
  getUserStore = getter
}

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      // 使用store清除认证状态
      if (getUserStore) {
        try {
          const userStore = getUserStore()
          userStore.clearAuth()
        } catch (e) {
          // 如果store不可用，直接清除localStorage
          localStorage.removeItem('access_token')
          localStorage.removeItem('token_expiry')
          localStorage.removeItem('user_info')
        }
      } else {
        // 直接清除localStorage
        localStorage.removeItem('access_token')
        localStorage.removeItem('token_expiry')
        localStorage.removeItem('user_info')
      }
      
      // 只在非登录页面时跳转
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    
    // 处理网络错误
    if (!error.response) {
      console.error('网络错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// 用户相关API
export const authAPI = {
  // 用户注册
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  
  // 用户登录
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  // 获取当前用户信息
  getCurrentUser: () => api.get('/auth/me'),
  
  // 用户登出
  logout: () => api.post('/auth/logout'),
}

// 角色相关API
export const charactersAPI = {
  // 获取角色列表
  getCharacters: (params?: {
    page?: number
    limit?: number
    search?: string
    tags?: string[]
    is_public?: boolean
  }) => api.get('/characters', { params }),
  
  // 获取角色详情
  getCharacter: (id: string) => api.get(`/characters/${id}`),
  
  // 创建角色
  createCharacter: (data: {
    name: string
    description: string
    avatar_url?: string
    system_prompt: string
    greeting: string
    tags: string[]
    is_public: boolean
  }) => api.post('/characters', data),
  
  // 更新角色
  updateCharacter: (id: string, data: any) => api.put(`/characters/${id}`, data),
  
  // 删除角色
  deleteCharacter: (id: string) => api.delete(`/characters/${id}`),
  
  // 获取我的角色
  getMyCharacters: (params?: { page?: number; limit?: number }) =>
    api.get('/characters/my/list', { params }),
}

// 会话相关API
export const conversationsAPI = {
  // 获取会话列表
  getConversations: (params?: {
    page?: number
    limit?: number
    character_id?: string
  }) => api.get('/conversations', { params }),
  
  // 获取会话详情
  getConversation: (id: string) => api.get(`/conversations/${id}`),
  
  // 删除会话
  deleteConversation: (id: string) => api.delete(`/conversations/${id}`),
  
  // 更新会话摘要
  updateConversationSummary: (id: string, summary: string) =>
    api.put(`/conversations/${id}/summary`, { summary }),
}

// 消息相关API
export const messagesAPI = {
  // 创建会话
  createConversation: (data: {
    character_id: string
    session_prompt?: string
  }) => api.post('/messages/conversations', data),
  
  // 获取消息列表
  getMessages: (conversationId: string, params?: {
    page?: number
    limit?: number
  }) => api.get(`/messages/conversations/${conversationId}/messages`, { params }),
  
  // 发送消息（流式响应）
  sendMessage: (conversationId: string, data: { content: string; stream?: boolean }) => {
    return fetch(`http://localhost:8000/api/messages/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: JSON.stringify(data),
    })
  },
  
  // 删除消息
  deleteMessage: (id: string) => api.delete(`/messages/${id}`),
}

export default api