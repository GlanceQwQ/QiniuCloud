import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import CharactersPage from '@/pages/CharactersPage.vue'
import CreateCharacterPage from '@/pages/CreateCharacterPage.vue'
import EditCharacterPage from '@/pages/EditCharacterPage.vue'
import ChatPage from '@/pages/ChatPage.vue'
import TestCharactersPage from '@/pages/TestCharactersPage.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { title: '首页' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { 
        title: '登录',
        hideForAuth: true // 已登录用户隐藏此页面
      }
    },
    {
      path: '/characters',
      name: 'characters',
      component: CharactersPage,
      meta: { title: '角色广场' }
    },
    {
      path: '/characters/create',
      name: 'create-character',
      component: CreateCharacterPage,
      meta: { 
        title: '创建角色',
        requiresAuth: true 
      }
    },
    {
      path: '/characters/:id/edit',
      name: 'edit-character',
      component: EditCharacterPage,
      meta: { 
        title: '编辑角色',
        requiresAuth: true 
      }
    },
    {
      path: '/chat/:characterId',
      name: 'chat',
      component: ChatPage,
      meta: { title: '聊天' }
    },
    {
      path: '/chat/:characterId/:conversationId',
      name: 'chat-conversation',
      component: ChatPage,
      meta: { title: '聊天' }
    },
    {
      path: '/test-characters',
      name: 'test-characters',
      component: TestCharactersPage,
      meta: { title: '角色API测试' }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userStore = useUserStore()
  
  // 等待用户状态初始化完成
  if (!userStore.isInitialized) {
    try {
      await userStore.initializeAuth()
    } catch (error) {
      console.error('初始化用户状态失败:', error)
    }
  }
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    // 保存原始路径，登录后跳转回来
    const redirectPath = to.fullPath
    next({
      path: '/login',
      query: { redirect: redirectPath }
    })
    return
  }
  
  // 已登录用户访问登录页，重定向到首页或原来要去的页面
  if (to.meta.hideForAuth && userStore.isLoggedIn) {
    const redirectPath = (to.query.redirect as string) || '/'
    next(redirectPath)
    return
  }
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI角色扮演`
  }
  
  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
})

export default router
