import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/conversion',
    name: 'Conversion',
    component: () => import('@/views/ConversionView.vue'),
  },
  {
    path: '/merge',
    name: 'Merge',
    component: () => import('@/views/MergeView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
