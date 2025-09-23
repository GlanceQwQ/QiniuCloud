<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messagesAPI, charactersAPI, conversationsAPI } from '@/services/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 允许游客访问聊天页面，无需强制登录

interface Character {
  id: string
  name: string
  description: string
  avatar_url: string
  personality: string
  background: string
  tags: string[]
}

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  created_at: string
}

interface Conversation {
  id: string
  title: string
  character_id: string
  created_at: string
  updated_at: string
}

const characterId = route.params.characterId as string
const conversationId = ref<string | null>(route.params.conversationId as string || null)

const character = ref<Character | null>(null)
const conversation = ref<Conversation | null>(null)
const messages = ref<Message[]>([])
const loading = ref(false)
const sending = ref(false)
const messageInput = ref('')
const messagesContainer = ref<HTMLElement>()

// 错误状态
const error = ref('')

// 计算属性
const canSendMessage = computed(() => {
  return messageInput.value.trim() && !sending.value
})

// 获取角色信息
const fetchCharacter = async () => {
  try {
    const response = await charactersAPI.getCharacter(characterId)
    character.value = response
  } catch (err: any) {
    console.error('获取角色信息失败:', err)
    error.value = '角色不存在或已被删除'
  }
}

// 获取或创建会话
const fetchOrCreateConversation = async () => {
  try {
    if (conversationId.value) {
      // 获取现有会话
      const response = await conversationsAPI.getConversation(conversationId.value)
      conversation.value = response
    } else {
      // 创建新会话
      const response = await messagesAPI.createConversation({
        character_id: characterId,
        session_prompt: `与${character.value?.name || '角色'}的对话`
      })
      conversation.value = response
      conversationId.value = response.id
      
      // 更新URL
      router.replace(`/chat/${characterId}/${response.id}`)
    }
  } catch (err: any) {
    console.error('获取或创建会话失败:', err)
    error.value = '无法创建对话会话'
  }
}

// 获取消息列表
const fetchMessages = async () => {
  if (!conversationId.value) return
  
  try {
    loading.value = true
    const response = await messagesAPI.getMessages(conversationId.value)
    messages.value = response.messages
    
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (err: any) {
    console.error('获取消息失败:', err)
    error.value = '获取消息失败'
  } finally {
    loading.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!canSendMessage.value || !conversationId.value) return
  
  const content = messageInput.value.trim()
  messageInput.value = ''
  
  // 添加用户消息到界面
  const userMessage: Message = {
    id: `temp-${Date.now()}`,
    content,
    role: 'user',
    created_at: new Date().toISOString()
  }
  messages.value.push(userMessage)
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  try {
    sending.value = true
    
    // 添加临时的AI消息占位符
    const aiMessage: Message = {
      id: `temp-ai-${Date.now()}`,
      content: '',
      role: 'assistant',
      created_at: new Date().toISOString()
    }
    messages.value.push(aiMessage)
    
    await nextTick()
    scrollToBottom()
    
    // 发送消息并获取流式响应
    const response = await messagesAPI.sendMessage(conversationId.value, {
      content,
      stream: true
    })
    
    // 处理流式响应
    if (response.body) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') {
                break
              }
              
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  // 更新AI消息内容
                  const lastMessage = messages.value[messages.value.length - 1]
                  if (lastMessage.role === 'assistant') {
                    lastMessage.content += parsed.content
                    await nextTick()
                    scrollToBottom()
                  }
                }
              } catch (e) {
                // 忽略解析错误
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
    }
    
  } catch (err: any) {
    console.error('发送消息失败:', err)
    
    // 移除用户消息和AI占位符
    messages.value = messages.value.filter(msg => 
      !msg.id.startsWith('temp-')
    )
    
    error.value = '发送消息失败，请稍后重试'
  } finally {
    sending.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 处理输入框回车事件
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 清除错误
const clearError = () => {
  error.value = ''
}

// 返回角色列表
const goBack = () => {
  router.push('/characters')
}

// 初始化
onMounted(async () => {
  await fetchCharacter()
  if (character.value) {
    await fetchOrCreateConversation()
    if (conversationId.value) {
      await fetchMessages()
    }
  }
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- 错误提示 -->
    <div v-if="error" class="bg-red-50 border-b border-red-200 px-4 py-3">
      <div class="flex items-center justify-between max-w-4xl mx-auto">
        <p class="text-red-600 text-sm">{{ error }}</p>
        <button @click="clearError" class="text-red-500 hover:text-red-700">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 头部 -->
    <div class="bg-white shadow-sm border-b flex-shrink-0">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="goBack"
              class="text-gray-600 hover:text-gray-800 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <div v-if="character" class="flex items-center space-x-3">
              <img
                :src="character.avatar_url"
                :alt="character.name"
                class="w-10 h-10 rounded-full object-cover"
                @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
              />
              <div>
                <h1 class="text-lg font-semibold text-gray-900">{{ character.name }}</h1>
                <p class="text-sm text-gray-600">{{ character.description }}</p>
              </div>
            </div>
            
            <div v-else class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gray-200 rounded-full animate-pulse"></div>
              <div>
                <div class="h-4 bg-gray-200 rounded w-24 animate-pulse mb-1"></div>
                <div class="h-3 bg-gray-200 rounded w-32 animate-pulse"></div>
              </div>
            </div>
          </div>
          
          <!-- 角色标签 -->
          <div v-if="character" class="hidden sm:flex flex-wrap gap-2">
            <span
              v-for="tag in character.tags.slice(0, 3)"
              :key="tag"
              class="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息区域 -->
    <div class="flex-1 overflow-hidden">
      <div
        ref="messagesContainer"
        class="h-full overflow-y-auto px-4 sm:px-6 lg:px-8 py-6"
      >
        <div class="max-w-4xl mx-auto space-y-6">
          <!-- 加载状态 -->
          <div v-if="loading" class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500"></div>
            <p class="mt-2 text-gray-600 text-sm">加载消息中...</p>
          </div>
          
          <!-- 欢迎消息 -->
          <div v-else-if="messages.length === 0" class="text-center py-12">
            <div v-if="character" class="space-y-4">
              <img
                :src="character.avatar_url"
                :alt="character.name"
                class="w-20 h-20 rounded-full object-cover mx-auto"
                @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
              />
              <div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">开始与{{ character.name }}对话</h3>
                <p class="text-gray-600 mb-4">{{ character.description }}</p>
                <div class="bg-gray-100 rounded-lg p-4 max-w-md mx-auto">
                  <p class="text-sm text-gray-700 font-medium mb-2">性格特点：</p>
                  <p class="text-sm text-gray-600">{{ character.personality }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 消息列表 -->
          <div v-else class="space-y-6">
            <div
              v-for="message in messages"
              :key="message.id"
              :class="[
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              ]"
            >
              <div
                :class="[
                  'max-w-xs sm:max-w-md lg:max-w-lg xl:max-w-xl flex',
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                ]"
              >
                <!-- 头像 -->
                <div class="flex-shrink-0">
                  <img
                    v-if="message.role === 'assistant'"
                    :src="character?.avatar_url"
                    :alt="character?.name"
                    class="w-8 h-8 rounded-full object-cover"
                    @error="$event.target.src = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20anime%20character%20placeholder&image_size=square'"
                  />
                  <div
                    v-else
                    class="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-sm font-medium"
                  >
                    {{ userStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
                  </div>
                </div>
                
                <!-- 消息内容 -->
                <div
                  :class="[
                    'mx-3 px-4 py-3 rounded-2xl',
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                      : 'bg-white shadow-sm border border-gray-200 text-gray-900'
                  ]"
                >
                  <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
                  <p
                    :class="[
                      'text-xs mt-2',
                      message.role === 'user' ? 'text-purple-100' : 'text-gray-500'
                    ]"
                  >
                    {{ formatTime(message.created_at) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="bg-white border-t flex-shrink-0">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-end space-x-4">
          <div class="flex-1">
            <textarea
              v-model="messageInput"
              placeholder="输入消息..."
              rows="1"
              class="w-full px-4 py-3 border border-gray-300 rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              :disabled="sending || !character"
              @keydown="handleKeydown"
              style="min-height: 48px; max-height: 120px;"
            ></textarea>
          </div>
          <button
            @click="sendMessage"
            :disabled="!canSendMessage"
            class="flex-shrink-0 w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full flex items-center justify-center hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="sending" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 自动调整textarea高度 */
textarea {
  field-sizing: content;
}
</style>