import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import router from './router'
import { useUserStore } from './stores/user'
import { setUserStoreGetter } from './services/api'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 设置API服务的store获取函数
setUserStoreGetter(() => useUserStore())

// 初始化用户认证状态
const userStore = useUserStore()
userStore.initializeAuth()

app.mount('#app')
