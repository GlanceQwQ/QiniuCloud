<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { charactersAPI } from '@/services/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 如果用户未登录，重定向到登录页
if (!userStore.isLoggedIn) {
  router.push('/login')
}

const loading = ref(false)
const errors = ref<Record<string, string>>({})

// 表单数据
const form = reactive({
  name: '',
  description: '',
  avatar: '',
  personality: '',
  background: '',
  tags: [] as string[],
  is_public: true
})

// 标签输入
const tagInput = ref('')

// 预设标签
const presetTags = [
  '友善', '幽默', '智慧', '冒险', '浪漫', '神秘',
  '可爱', '成熟', '活泼', '温柔', '严肃', '搞笑',
  '助手', '老师', '朋友', '导师', '伙伴', '顾问'
]

// 表单验证
const validateForm = () => {
  errors.value = {}
  
  if (!form.name.trim()) {
    errors.value.name = '角色名称不能为空'
  } else if (form.name.length > 50) {
    errors.value.name = '角色名称不能超过50个字符'
  }
  
  if (!form.description.trim()) {
    errors.value.description = '角色描述不能为空'
  } else if (form.description.length > 200) {
    errors.value.description = '角色描述不能超过200个字符'
  }
  
  if (!form.personality.trim()) {
    errors.value.personality = '性格特点不能为空'
  } else if (form.personality.length > 500) {
    errors.value.personality = '性格特点不能超过500个字符'
  }
  
  if (form.background && form.background.length > 1000) {
    errors.value.background = '背景故事不能超过1000个字符'
  }
  
  if (form.tags.length === 0) {
    errors.value.tags = '请至少选择一个标签'
  }
  
  return Object.keys(errors.value).length === 0
}

// 添加标签
const addTag = (tag?: string) => {
  const tagToAdd = tag || tagInput.value.trim()
  if (tagToAdd && !form.tags.includes(tagToAdd) && form.tags.length < 10) {
    form.tags.push(tagToAdd)
    tagInput.value = ''
  }
}

// 移除标签
const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

// 生成随机头像
const generateAvatar = () => {
  const prompts = [
    'cute anime character portrait',
    'friendly cartoon character',
    'professional avatar illustration',
    'kawaii anime style character',
    'modern character design'
  ]
  const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)]
  form.avatar = `https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=${encodeURIComponent(randomPrompt)}&image_size=square`
}

// 提交表单
const submitForm = async () => {
  if (!validateForm()) {
    return
  }
  
  try {
    loading.value = true
    
    // 如果没有设置头像，生成一个默认头像
    if (!form.avatar) {
      generateAvatar()
    }
    
    // 构建系统提示词和问候语
    const systemPrompt = `你是${form.name.trim()}。${form.description.trim()}\n\n性格特点：${form.personality.trim()}${form.background ? `\n\n背景故事：${form.background.trim()}` : ''}`
    const greeting = `你好！我是${form.name.trim()}。${form.description.trim()}`
    
    await charactersAPI.createCharacter({
      name: form.name.trim(),
      description: form.description.trim(),
      avatar_url: form.avatar,
      system_prompt: systemPrompt,
      greeting: greeting,
      tags: form.tags,
      is_public: form.is_public
    })
    
    // 创建成功，跳转到角色列表
    router.push('/characters')
    
  } catch (error: any) {
    console.error('创建角色失败:', error)
    if (error.response?.data?.detail) {
      errors.value.submit = error.response.data.detail
    } else {
      errors.value.submit = '创建角色失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 初始化时生成一个默认头像
generateAvatar()
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 头部 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">创建角色</h1>
            <p class="mt-2 text-gray-600">设计你的专属AI角色，开始独特的对话体验</p>
          </div>
          <button
            @click="router.push('/characters')"
            class="text-gray-600 hover:text-gray-800 font-medium"
          >
            返回角色列表
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <form @submit.prevent="submitForm" class="space-y-8">
        <!-- 基本信息 -->
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">基本信息</h2>
          
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- 头像预览 -->
            <div class="lg:col-span-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">角色头像</label>
              <div class="space-y-4">
                <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    :src="form.avatar"
                    alt="角色头像"
                    class="w-full h-full object-cover"
                    @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
                  />
                </div>
                <div class="space-y-2">
                  <input
                    v-model="form.avatar"
                    type="url"
                    placeholder="输入头像URL"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                  />
                  <button
                    type="button"
                    @click="generateAvatar"
                    class="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    生成随机头像
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 基本信息表单 -->
            <div class="lg:col-span-2 space-y-4">
              <!-- 角色名称 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">角色名称 *</label>
                <input
                  v-model="form.name"
                  type="text"
                  placeholder="给你的角色起个名字"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  :class="{ 'border-red-500': errors.name }"
                />
                <p v-if="errors.name" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
              </div>
              
              <!-- 角色描述 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">角色描述 *</label>
                <textarea
                  v-model="form.description"
                  rows="3"
                  placeholder="简单描述你的角色是什么样的"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  :class="{ 'border-red-500': errors.description }"
                ></textarea>
                <p v-if="errors.description" class="mt-1 text-sm text-red-600">{{ errors.description }}</p>
                <p class="mt-1 text-sm text-gray-500">{{ form.description.length }}/200</p>
              </div>
              
              <!-- 公开设置 -->
              <div>
                <label class="flex items-center space-x-3">
                  <input
                    v-model="form.is_public"
                    type="checkbox"
                    class="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <span class="text-sm font-medium text-gray-700">公开角色（其他用户可以发现和使用）</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- 性格特点 -->
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">性格特点</h2>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">性格描述 *</label>
            <textarea
              v-model="form.personality"
              rows="4"
              placeholder="详细描述角色的性格特点、说话方式、行为习惯等"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              :class="{ 'border-red-500': errors.personality }"
            ></textarea>
            <p v-if="errors.personality" class="mt-1 text-sm text-red-600">{{ errors.personality }}</p>
            <p class="mt-1 text-sm text-gray-500">{{ form.personality.length }}/500</p>
          </div>
        </div>

        <!-- 背景故事 -->
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">背景故事</h2>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">背景描述（可选）</label>
            <textarea
              v-model="form.background"
              rows="5"
              placeholder="描述角色的背景故事、经历、世界观等"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              :class="{ 'border-red-500': errors.background }"
            ></textarea>
            <p v-if="errors.background" class="mt-1 text-sm text-red-600">{{ errors.background }}</p>
            <p class="mt-1 text-sm text-gray-500">{{ form.background.length }}/1000</p>
          </div>
        </div>

        <!-- 标签设置 -->
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">标签设置</h2>
          
          <!-- 已选标签 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">已选标签 *</label>
            <div class="flex flex-wrap gap-2 min-h-[2.5rem] p-3 border border-gray-300 rounded-lg" :class="{ 'border-red-500': errors.tags }">
              <span
                v-for="(tag, index) in form.tags"
                :key="index"
                class="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
              >
                {{ tag }}
                <button
                  type="button"
                  @click="removeTag(index)"
                  class="ml-2 text-purple-500 hover:text-purple-700"
                >
                  ×
                </button>
              </span>
              <span v-if="form.tags.length === 0" class="text-gray-400 text-sm">请选择或添加标签</span>
            </div>
            <p v-if="errors.tags" class="mt-1 text-sm text-red-600">{{ errors.tags }}</p>
            <p class="mt-1 text-sm text-gray-500">{{ form.tags.length }}/10</p>
          </div>
          
          <!-- 预设标签 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">预设标签</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in presetTags"
                :key="tag"
                type="button"
                @click="addTag(tag)"
                :disabled="form.tags.includes(tag) || form.tags.length >= 10"
                class="px-3 py-1 border border-gray-300 rounded-full text-sm font-medium transition-all"
                :class="{
                  'bg-gray-100 text-gray-400 cursor-not-allowed': form.tags.includes(tag) || form.tags.length >= 10,
                  'bg-white text-gray-700 hover:bg-gray-50': !form.tags.includes(tag) && form.tags.length < 10
                }"
              >
                {{ tag }}
              </button>
            </div>
          </div>
          
          <!-- 自定义标签 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">自定义标签</label>
            <div class="flex space-x-2">
              <input
                v-model="tagInput"
                type="text"
                placeholder="输入自定义标签"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                @keyup.enter="addTag()"
                :disabled="form.tags.length >= 10"
              />
              <button
                type="button"
                @click="addTag()"
                :disabled="!tagInput.trim() || form.tags.length >= 10"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                添加
              </button>
            </div>
          </div>
        </div>

        <!-- 提交错误 -->
        <div v-if="errors.submit" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-red-600 text-sm">{{ errors.submit }}</p>
        </div>

        <!-- 提交按钮 -->
        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="router.push('/characters')"
            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              创建中...
            </span>
            <span v-else>创建角色</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>