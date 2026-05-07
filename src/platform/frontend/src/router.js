import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import FingerprintView from './views/FingerprintView.vue'
import EncryptView from './views/EncryptView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/fingerprint', component: FingerprintView },
  { path: '/encrypt', component: EncryptView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
