<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
import { useUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const userStore = useUserStore()

// 应用启动时初始化用户状态
onMounted(() => {
  userStore.initializeAuth()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar />
    <main>
      <router-view />
    </main>
  </div>
</template>