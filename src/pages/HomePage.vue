<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { charactersAPI } from '@/services/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

interface Character {
  id: string
  name: string
  description: string
  avatar: string
  tags: string[]
}

const featuredCharacters = ref<Character[]>([])
const loading = ref(false)

// 获取推荐角色
const fetchFeaturedCharacters = async () => {
  try {
    loading.value = true
    const response = await charactersAPI.getCharacters({
      page: 1,
      limit: 6,
      is_public: true
    })
    featuredCharacters.value = response.characters
  } catch (error) {
    console.error('获取推荐角色失败:', error)
  } finally {
    loading.value = false
  }
}

// 开始对话
const startChat = (character: Character) => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  router.push(`/chat/${character.id}`)
}

// 导航到角色发现页
const goToCharacters = () => {
  router.push('/characters')
}

// 导航到登录页
const goToLogin = () => {
  router.push('/login')
}

// 导航到创建角色页
const goToCreateCharacter = () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  router.push('/characters/create')
}

onMounted(() => {
  fetchFeaturedCharacters()
})
</script>

<template>
  <div class="bg-gradient-to-br from-purple-50 via-white to-pink-50">
    <!-- 英雄区域 -->
    <div class="relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute inset-0">
        <div class="absolute top-0 left-0 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div class="absolute top-0 right-0 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-16">
        <div class="text-center">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            与AI角色
            <span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              开启对话
            </span>
          </h1>
          <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            探索无限可能的AI角色世界，与各种个性鲜明的角色进行深度对话，
            或者创建属于你自己的独特AI伙伴
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              @click="goToCharacters"
              class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:from-purple-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              开始探索角色
            </button>
            
            <button
              @click="goToCreateCharacter"
              class="bg-white text-gray-700 px-8 py-4 rounded-2xl font-semibold text-lg border-2 border-gray-200 hover:border-purple-300 hover:text-purple-600 transform hover:scale-105 transition-all duration-200 shadow-lg"
            >
              {{ userStore.isLoggedIn ? '创建我的角色' : '开始创建角色' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 特色功能 -->
    <div class="py-16 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">为什么选择我们？</h2>
          <p class="text-lg text-gray-600">体验前所未有的AI角色扮演对话</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">丰富的角色库</h3>
            <p class="text-gray-600">数百个精心设计的AI角色，涵盖各种性格和背景，总有一个适合你</p>
          </div>
          
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a1 1 0 01-1-1V9a1 1 0 011-1h1a2 2 0 100-4H4a1 1 0 01-1-1V4a1 1 0 011-1h3a1 1 0 001-1v-1a2 2 0 012-2z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">自定义创建</h3>
            <p class="text-gray-600">轻松创建属于你的独特AI角色，定制性格、背景和对话风格</p>
          </div>
          
          <div class="text-center p-6">
            <div class="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">智能对话</h3>
            <p class="text-gray-600">基于先进AI技术，提供自然流畅的对话体验，让每次交流都充满惊喜</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐角色 -->
    <div class="py-16 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">热门角色</h2>
          <p class="text-lg text-gray-600">与这些受欢迎的AI角色开始你的对话之旅</p>
        </div>
        
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <p class="mt-2 text-gray-600">加载中...</p>
        </div>
        
        <div v-else-if="featuredCharacters.length === 0" class="text-center py-12">
          <p class="text-gray-600">暂无推荐角色</p>
        </div>
        
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="character in featuredCharacters"
            :key="character.id"
            class="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-200 overflow-hidden group cursor-pointer transform hover:scale-105"
            @click="startChat(character)"
          >
            <!-- 角色头像 -->
            <div class="aspect-square bg-gradient-to-br from-purple-100 to-pink-100 relative overflow-hidden">
              <img
                :src="character.avatar"
                :alt="character.name"
                class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
              />
            </div>
            
            <!-- 角色信息 -->
            <div class="p-6">
              <h3 class="font-bold text-xl text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
                {{ character.name }}
              </h3>
              <p class="text-gray-600 mb-4 line-clamp-2">
                {{ character.description }}
              </p>
              
              <!-- 标签 -->
              <div class="flex flex-wrap gap-2 mb-4">
                <span
                  v-for="tag in (character.tags || []).slice(0, 3)"
                  :key="tag"
                  class="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full font-medium"
                >
                  {{ tag }}
                </span>
              </div>
              
              <!-- 开始对话按钮 -->
              <button
                class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-4 rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all"
                @click.stop="startChat(character)"
              >
                开始对话
              </button>
            </div>
          </div>
        </div>
        
        <div class="text-center mt-12">
          <button
            @click="goToCharacters"
            class="bg-white text-purple-600 px-8 py-3 rounded-xl font-semibold border-2 border-purple-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
          >
            查看更多角色
          </button>
        </div>
      </div>
    </div>

    <!-- CTA区域 -->
    <div class="py-16 bg-gradient-to-r from-purple-600 to-pink-600">
      <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-white mb-4">
          准备好开始你的AI角色扮演之旅了吗？
        </h2>
        <p class="text-xl text-purple-100 mb-8">
          加入我们，创造属于你的独特角色，开启无限可能的对话体验
        </p>
        
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            @click="goToCreateCharacter"
            class="bg-white text-purple-600 px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-gray-50 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            {{ userStore.isLoggedIn ? '创建角色' : '开始体验' }}
          </button>
          
          <button
            @click="goToCharacters"
            class="bg-transparent text-white px-8 py-4 rounded-2xl font-semibold text-lg border-2 border-white hover:bg-white hover:text-purple-600 transform hover:scale-105 transition-all duration-200"
          >
            先看看角色
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
