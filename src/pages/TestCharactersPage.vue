<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">角色API测试页面</h1>
    
    <button 
      @click="testAPI" 
      class="bg-blue-500 text-white px-4 py-2 rounded mb-4"
      :disabled="loading"
    >
      {{ loading ? '测试中...' : '测试角色API' }}
    </button>
    
    <div v-if="result" class="mt-4">
      <h2 class="text-lg font-semibold mb-2">测试结果:</h2>
      <pre class="bg-gray-100 p-4 rounded overflow-auto">{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
    
    <div v-if="error" class="mt-4 text-red-600">
      <h2 class="text-lg font-semibold mb-2">错误信息:</h2>
      <pre class="bg-red-100 p-4 rounded overflow-auto">{{ error }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { charactersAPI } from '@/services/api'

const loading = ref(false)
const result = ref(null)
const error = ref('')

const testAPI = async () => {
  loading.value = true
  result.value = null
  error.value = ''
  
  try {
    console.log('开始测试角色API...')
    console.log('API基础URL:', 'http://localhost:8000/api')
    
    // 先测试基础连接
    const healthResponse = await fetch('http://localhost:8000/health')
    console.log('健康检查响应状态:', healthResponse.status)
    
    if (!healthResponse.ok) {
      throw new Error(`健康检查失败: ${healthResponse.status}`)
    }
    
    // 然后测试角色API
    const response = await charactersAPI.getCharacters({
      page: 1,
      limit: 12,
      is_public: true
    })
    
    console.log('API响应:', response)
    result.value = {
      health_check: 'OK',
      characters_api: response
    }
    
  } catch (err: any) {
    console.error('API测试失败:', err)
    console.error('错误类型:', err.constructor.name)
    console.error('错误代码:', err.code)
    console.error('网络状态:', navigator.onLine ? '在线' : '离线')
    
    const errorInfo = {
      message: err.message,
      code: err.code,
      response: err.response?.data,
      status: err.response?.status,
      network_online: navigator.onLine
    }
    
    error.value = JSON.stringify(errorInfo, null, 2)
  } finally {
    loading.value = false
  }
}
</script>