<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const showUserMenu = ref(false)

// 导航到不同页面
const goToHome = () => {
  router.push('/')
}

const goToCharacters = () => {
  router.push('/characters')
}

const goToLogin = () => {
  router.push('/login')
}

const goToCreateCharacter = () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  router.push('/characters/create')
}

// 处理登出
const handleLogout = async () => {
  try {
    await userStore.logout()
    showUserMenu.value = false
  } catch (error) {
    console.error('登出失败:', error)
  }
}

// 点击外部关闭菜单
const closeUserMenu = () => {
  showUserMenu.value = false
}
</script>

<template>
  <nav class="bg-white shadow-lg sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo和品牌 -->
        <div class="flex items-center cursor-pointer" @click="goToHome">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
          </div>
          <div class="ml-3">
            <h1 class="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI角色扮演
            </h1>
          </div>
        </div>

        <!-- 导航链接 -->
        <div class="hidden md:block">
          <div class="ml-10 flex items-baseline space-x-4">
            <button
              @click="goToHome"
              class="text-gray-700 hover:text-purple-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              首页
            </button>
            <button
              @click="goToCharacters"
              class="text-gray-700 hover:text-purple-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              角色广场
            </button>
            <button
              v-if="userStore.isLoggedIn"
              @click="goToCreateCharacter"
              class="text-gray-700 hover:text-purple-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              创建角色
            </button>
          </div>
        </div>

        <!-- 用户区域 -->
        <div class="flex items-center space-x-4">
          <!-- 登录状态指示器 -->
          <div v-if="userStore.loading" class="flex items-center space-x-2">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-500"></div>
            <span class="text-sm text-gray-600">加载中...</span>
          </div>
          
          <!-- 未登录状态 -->
          <div v-else-if="!userStore.isLoggedIn" class="flex items-center space-x-2">
            <button
              @click="goToLogin"
              class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
            >
              登录 / 注册
            </button>
          </div>
          
          <!-- 已登录状态 -->
          <div v-else class="relative">
            <!-- 用户信息按钮 -->
            <button
              @click="showUserMenu = !showUserMenu"
              class="flex items-center space-x-3 text-gray-700 hover:text-purple-600 focus:outline-none focus:text-purple-600 transition-colors"
            >
              <!-- 用户头像 -->
              <div class="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
                <span class="text-white text-sm font-medium">
                  {{ userStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
                </span>
              </div>
              
              <!-- 用户名 -->
              <span class="hidden sm:block text-sm font-medium">
                {{ userStore.user?.username || '用户' }}
              </span>
              
              <!-- 下拉箭头 -->
              <svg 
                class="w-4 h-4 transition-transform" 
                :class="{ 'rotate-180': showUserMenu }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            <!-- 用户菜单下拉 -->
            <div 
              v-if="showUserMenu" 
              class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
              @click.stop
            >
              <!-- 用户信息 -->
              <div class="px-4 py-2 border-b border-gray-100">
                <p class="text-sm font-medium text-gray-900">{{ userStore.user?.username }}</p>
                <p class="text-sm text-gray-500">{{ userStore.user?.email }}</p>
              </div>
              
              <!-- 菜单项 -->
              <button
                @click="goToCreateCharacter(); closeUserMenu()"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
              >
                创建角色
              </button>
              
              <button
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                退出登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 点击外部关闭菜单的遮罩 -->
    <div 
      v-if="showUserMenu" 
      class="fixed inset-0 z-40" 
      @click="closeUserMenu"
    ></div>
  </nav>
</template>

<style scoped>
.rotate-180 {
  transform: rotate(180deg);
}
</style>