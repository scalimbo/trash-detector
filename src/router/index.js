import { createRouter, createWebHistory } from 'vue-router'
// import CameraCapture from '../views/HomeView.vue'
import CameraCapture from '@/components/CameraCapture.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CameraCapture,
    },
  ],
})

export default router
