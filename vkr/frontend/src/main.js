import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useAuthStore } from './store/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Инициализация хранилища auth
const authStore = useAuthStore()
authStore.init().finally(() => {
  // Монтируем приложение после инициализации хранилища
  app.mount('#app')
})