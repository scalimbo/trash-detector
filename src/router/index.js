import { createRouter, createWebHistory } from 'vue-router'
// import CameraCapture from '../views/HomeView.vue'
import CameraCapture from '@/components/CameraCapture.vue'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/camera',
      name: 'camera',
      component: CameraCapture,
      props: true, // Enable props to pass data to the component
      meta: {
        title: 'Camera Capture',
      },
    },
  ],
})

export default router
