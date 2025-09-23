<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isLogin = ref(true) // true: 登录, false: 注册
const loading = ref(false)
const errorMessage = ref('')

// 登录表单
const loginForm = reactive({
  email: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 切换登录/注册模式
const toggleMode = () => {
  isLogin.value = !isLogin.value
  errorMessage.value = ''
  // 清空表单
  Object.assign(loginForm, { email: '', password: '' })
  Object.assign(registerForm, { username: '', email: '', password: '', confirmPassword: '' })
}

// 处理登录
const handleLogin = async () => {
  if (!loginForm.email || !loginForm.password) {
    errorMessage.value = '请填写邮箱和密码'
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''
    
    await userStore.login({
      email: loginForm.email,
      password: loginForm.password
    })
    
    // 登录成功，跳转到原来要访问的页面或首页
    const redirectPath = (route.query.redirect as string) || '/'
    router.push(redirectPath)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    errorMessage.value = '请填写所有必填字段'
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  if (registerForm.password.length < 6) {
    errorMessage.value = '密码长度至少6位'
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''
    
    await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    })
    
    // 注册成功，跳转到原来要访问的页面或首页
    const redirectPath = (route.query.redirect as string) || '/'
    router.push(redirectPath)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 处理表单提交
const handleSubmit = () => {
  if (isLogin.value) {
    handleLogin()
  } else {
    handleRegister()
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
      <!-- 标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">
          {{ isLogin ? '欢迎回来' : '加入我们' }}
        </h1>
        <p class="text-gray-600">
          {{ isLogin ? '登录您的账户开始AI角色扮演' : '创建账户体验AI角色扮演' }}
        </p>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
        {{ errorMessage }}
      </div>

      <!-- 登录表单 -->
      <form v-if="isLogin" @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            v-model="loginForm.email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请输入邮箱地址"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input
            v-model="loginForm.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请输入密码"
          />
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
          <input
            v-model="registerForm.username"
            type="text"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请输入用户名"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            v-model="registerForm.email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请输入邮箱地址"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input
            v-model="registerForm.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请输入密码（至少6位）"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
          <input
            v-model="registerForm.confirmPassword"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            placeholder="请再次输入密码"
          />
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <!-- 切换登录/注册 -->
      <div class="mt-8 text-center">
        <p class="text-gray-600">
          {{ isLogin ? '还没有账户？' : '已有账户？' }}
          <button
            @click="toggleMode"
            class="text-purple-600 hover:text-purple-700 font-medium ml-1 transition-colors"
          >
            {{ isLogin ? '立即注册' : '立即登录' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>