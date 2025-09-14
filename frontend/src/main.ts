import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { initializeCSRF } from './services/api'

const app = createApp(App)

// 注册 Element Plus
app.use(ElementPlus)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)

// 初始化CSRF token然后挂载应用
initializeCSRF().then(() => {
  app.mount('#app')
}).catch(() => {
  // 即使CSRF初始化失败也要挂载应用
  app.mount('#app')
})
