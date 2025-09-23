<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- 页面标题 -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">编辑角色</h1>
        <p class="text-gray-600">修改你的AI角色设定</p>
      </div>

      <!-- 编辑表单 -->
      <div class="bg-white rounded-xl shadow-lg p-8">
        <form @submit.prevent="updateCharacter" class="space-y-6">
          <!-- 角色名称 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              角色名称 *
            </label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="给你的AI角色起个名字"
            />
          </div>

          <!-- 角色描述 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              角色描述 *
            </label>
            <textarea
              v-model="form.description"
              required
              rows="3"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              placeholder="简单描述一下这个角色的特点"
            ></textarea>
          </div>

          <!-- 头像URL -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              头像链接
            </label>
            <input
              v-model="form.avatar_url"
              type="url"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="https://example.com/avatar.jpg"
            />
            <p class="text-sm text-gray-500 mt-1">可选，留空将使用默认头像</p>
          </div>

          <!-- 系统提示词 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              系统提示词 *
            </label>
            <textarea
              v-model="form.system_prompt"
              required
              rows="4"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              placeholder="定义角色的性格、背景和行为方式"
            ></textarea>
            <p class="text-sm text-gray-500 mt-1">这将决定AI如何扮演这个角色</p>
          </div>

          <!-- 问候语 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              问候语 *
            </label>
            <textarea
              v-model="form.greeting"
              required
              rows="2"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              placeholder="角色的开场白"
            ></textarea>
          </div>

          <!-- 标签 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              标签
            </label>
            <div class="flex flex-wrap gap-2 mb-3">
              <span
                v-for="(tag, index) in form.tags"
                :key="index"
                class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-800"
              >
                {{ tag }}
                <button
                  type="button"
                  @click="removeTag(index)"
                  class="ml-2 text-purple-600 hover:text-purple-800"
                >
                  ×
                </button>
              </span>
            </div>
            <div class="flex gap-2">
              <input
                v-model="newTag"
                type="text"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="添加标签"
                @keyup.enter="addTag"
              />
              <button
                type="button"
                @click="addTag"
                class="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-all"
              >
                添加
              </button>
            </div>
          </div>

          <!-- 公开设置 -->
          <div class="flex items-center">
            <input
              v-model="form.is_public"
              type="checkbox"
              id="is_public"
              class="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500"
            />
            <label for="is_public" class="ml-2 text-sm text-gray-700">
              公开角色（其他用户可以看到并使用）
            </label>
          </div>

          <!-- 按钮组 -->
          <div class="flex space-x-4 pt-6">
            <button
              type="button"
              @click="$router.go(-1)"
              class="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50"
            >
              {{ loading ? '保存中...' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { charactersAPI } from '@/services/api'
import { useUserStore } from '@/stores/user'
import { toast } from 'sonner'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const newTag = ref('')

// 表单数据
const form = ref({
  name: '',
  description: '',
  avatar_url: '',
  system_prompt: '',
  greeting: '',
  tags: [] as string[],
  is_public: false
})

// 获取角色详情
const fetchCharacter = async () => {
  try {
    const characterId = route.params.id as string
    const response = await charactersAPI.getCharacter(characterId)
    
    // 填充表单数据
    form.value = {
      name: response.name,
      description: response.description,
      avatar_url: response.avatar_url || '',
      system_prompt: response.system_prompt,
      greeting: response.greeting,
      tags: response.tags || [],
      is_public: response.is_public
    }
  } catch (error: any) {
    console.error('获取角色详情失败:', error)
    toast.error('获取角色详情失败')
    router.push('/characters')
  }
}

// 添加标签
const addTag = () => {
  if (newTag.value.trim() && !form.value.tags.includes(newTag.value.trim())) {
    form.value.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

// 移除标签
const removeTag = (index: number) => {
  form.value.tags.splice(index, 1)
}

// 更新角色
const updateCharacter = async () => {
  if (!userStore.isLoggedIn) {
    toast.error('请先登录')
    return
  }

  loading.value = true
  try {
    const characterId = route.params.id as string
    await charactersAPI.updateCharacter(characterId, form.value)
    
    toast.success('角色更新成功！')
    router.push('/characters')
  } catch (error: any) {
    console.error('更新角色失败:', error)
    const message = error.response?.data?.detail || '更新角色失败'
    toast.error(message)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取角色详情
onMounted(() => {
  fetchCharacter()
})
</script>