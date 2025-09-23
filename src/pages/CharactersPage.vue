<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { charactersAPI } from '@/services/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

interface Character {
  id: string
  name: string
  description: string
  avatar_url: string
  tags: string[]
  is_public: boolean
  creator_id: string | null
  created_at: string
}

const characters = ref<Character[]>([])
const myCharacters = ref<Character[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedTags = ref<string[]>([])
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 12
const activeTab = ref<'all' | 'my'>('all')
const showDeleteModal = ref(false)
const characterToDelete = ref<Character | null>(null)

// 所有可用标签
const availableTags = ref<string[]>([])

// 当前显示的角色列表
const currentCharacters = computed(() => {
  return activeTab.value === 'all' ? characters.value : myCharacters.value
})

// 过滤后的角色列表
const filteredCharacters = computed(() => {
  let filtered = currentCharacters.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(char => 
      char.name.toLowerCase().includes(query) ||
      char.description.toLowerCase().includes(query)
    )
  }
  
  // 标签过滤
  if (selectedTags.value.length > 0) {
    filtered = filtered.filter(char => 
      selectedTags.value.some(tag => char.tags.includes(tag))
    )
  }
  
  return filtered
})

// 获取角色列表
const fetchCharacters = async () => {
  console.log('开始获取角色列表...')
  loading.value = true
  try {
    const response = await charactersAPI.getCharacters({
      page: currentPage.value,
      limit: pageSize,
      is_public: true
    })
    
    console.log('API响应:', response)
    console.log('角色数量:', response.characters?.length || 0)
    
    characters.value = response.characters || []
    totalPages.value = Math.ceil((response.total || 0) / pageSize)
    
    // 收集所有标签
    const allTags = new Set<string>()
    characters.value.forEach(char => {
      if (char.tags) {
        char.tags.forEach(tag => allTags.add(tag))
      }
    })
    availableTags.value = Array.from(allTags)
    
  } catch (error) {
    console.error('获取角色列表失败:', error)
    console.error('错误详情:', error.response?.data || error.message)
  } finally {
    loading.value = false
  }
}

// 获取我的角色列表
const fetchMyCharacters = async () => {
  if (!userStore.isLoggedIn) return
  
  loading.value = true
  try {
    const response = await charactersAPI.getMyCharacters({
      page: currentPage.value,
      limit: pageSize
    })
    
    myCharacters.value = response.characters || []
    totalPages.value = Math.ceil((response.total || 0) / pageSize)
    
    // 收集我的角色标签
    const allTags = new Set<string>()
    myCharacters.value.forEach(char => {
      if (char.tags) {
        char.tags.forEach(tag => allTags.add(tag))
      }
    })
    availableTags.value = Array.from(allTags)
    
  } catch (error) {
    console.error('获取我的角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 删除角色
const deleteCharacter = async (character: Character) => {
  try {
    await charactersAPI.deleteCharacter(character.id)
    // 从列表中移除
    myCharacters.value = myCharacters.value.filter(c => c.id !== character.id)
    showDeleteModal.value = false
    characterToDelete.value = null
  } catch (error) {
    console.error('删除角色失败:', error)
    alert('删除角色失败，请稍后重试')
  }
}

// 显示删除确认对话框
const confirmDelete = (character: Character) => {
  characterToDelete.value = character
  showDeleteModal.value = true
}

// 编辑角色
const editCharacter = (character: Character) => {
  router.push(`/characters/${character.id}/edit`)
}

// 开始对话
const startChat = (character: Character) => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  router.push(`/chat/${character.id}`)
}

// 切换标签选择
const toggleTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag)
  }
}

// 清除所有过滤
const clearFilters = () => {
  searchQuery.value = ''
  selectedTags.value = []
}

// 切换标签页
const switchTab = (tab: 'all' | 'my') => {
  activeTab.value = tab
  currentPage.value = 1
  clearFilters()
  if (tab === 'all') {
    fetchCharacters()
  } else {
    fetchMyCharacters()
  }
}

// 分页
const changePage = (page: number) => {
  currentPage.value = page
  if (activeTab.value === 'all') {
    fetchCharacters()
  } else {
    fetchMyCharacters()
  }
}

onMounted(() => {
  fetchCharacters()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 头部 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">角色发现</h1>
            <p class="mt-2 text-gray-600">探索各种有趣的AI角色，开始你的专属对话</p>
          </div>
          <div v-if="userStore.isLoggedIn">
            <button
              @click="router.push('/characters/create')"
              class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
            >
              创建角色
            </button>
          </div>
          <div v-else class="text-center">
            <p class="text-sm text-gray-600 mb-2">想要创建自己的角色？</p>
            <button
              @click="router.push('/login')"
              class="bg-white text-purple-600 px-6 py-2 rounded-lg font-medium border-2 border-purple-200 hover:border-purple-300 hover:bg-purple-50 transition-all"
            >
              登录/注册
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 标签页 -->
      <div v-if="userStore.isLoggedIn" class="mb-8">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button
              @click="switchTab('all')"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm',
                activeTab === 'all'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              所有角色
            </button>
            <button
              @click="switchTab('my')"
              :class="[
                'py-2 px-1 border-b-2 font-medium text-sm',
                activeTab === 'my'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              我的角色
            </button>
          </nav>
        </div>
      </div>

      <!-- 搜索和过滤 -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <!-- 搜索框 -->
        <div class="mb-6">
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索角色名称或描述..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>

        <!-- 标签过滤 -->
        <div class="mb-4">
          <h3 class="text-sm font-medium text-gray-700 mb-3">按标签筛选</h3>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in availableTags"
              :key="tag"
              @click="toggleTag(tag)"
              :class="[
                'px-3 py-1 rounded-full text-sm font-medium transition-all',
                selectedTags.includes(tag)
                  ? 'bg-purple-100 text-purple-700 border-2 border-purple-300'
                  : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
              ]"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <!-- 清除过滤 -->
        <div v-if="searchQuery || selectedTags.length > 0" class="flex items-center justify-between">
          <p class="text-sm text-gray-600">
            找到 {{ filteredCharacters.length }} 个角色
          </p>
          <button
            @click="clearFilters"
            class="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            清除所有过滤
          </button>
        </div>
      </div>

      <!-- 角色网格 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        <p class="mt-2 text-gray-600">加载中...</p>
      </div>

      <div v-else-if="filteredCharacters.length === 0" class="text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8l-4 4m0 0l-4-4m4 4V3" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">没有找到角色</h3>
        <p class="text-gray-600">尝试调整搜索条件或清除过滤器</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="character in filteredCharacters"
          :key="character.id"
          class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden group cursor-pointer"
          @click="startChat(character)"
        >
          <!-- 角色头像 -->
          <div class="aspect-square bg-gradient-to-br from-purple-100 to-pink-100 relative overflow-hidden">
            <img
              :src="character.avatar_url || 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
              :alt="character.name"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
              @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
            />
          </div>

          <!-- 角色信息 -->
          <div class="p-4">
            <h3 class="font-semibold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
              {{ character.name }}
            </h3>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">
              {{ character.description }}
            </p>
            
            <!-- 标签 -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span
                v-for="tag in character.tags.slice(0, 3)"
                :key="tag"
                class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {{ tag }}
              </span>
              <span
                v-if="character.tags.length > 3"
                class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                +{{ character.tags.length - 3 }}
              </span>
            </div>
            
            <!-- 按钮区域 -->
            <div v-if="activeTab === 'my' && userStore.isLoggedIn" class="space-y-2">
              <!-- 管理按钮 -->
              <div class="flex space-x-2">
                <button
                  @click.stop="editCharacter(character)"
                  class="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-600 transition-all"
                >
                  编辑
                </button>
                <button
                  @click.stop="confirmDelete(character)"
                  class="flex-1 bg-red-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-red-600 transition-all"
                >
                  删除
                </button>
              </div>
              <!-- 开始对话按钮 -->
              <button
                class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
                @click.stop="startChat(character)"
              >
                开始对话
              </button>
            </div>
            <div v-else>
              <!-- 开始对话按钮 -->
              <button
                class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 px-4 rounded-lg text-sm font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
                @click.stop="startChat(character)"
              >
                开始对话
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="mt-12 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button
            v-for="page in totalPages"
            :key="page"
            @click="changePage(page)"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-all',
              page === currentPage
                ? 'bg-purple-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            ]"
          >
            {{ page }}
          </button>
        </nav>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">确认删除角色</h3>
        <p class="text-gray-600 mb-6">
          确定要删除角色 "{{ characterToDelete?.name }}" 吗？此操作无法撤销。
        </p>
        <div class="flex space-x-4">
          <button
            @click="showDeleteModal = false"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-all"
          >
            取消
          </button>
          <button
            @click="deleteCharacter(characterToDelete!)"
            class="flex-1 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all"
          >
            删除
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
</style>