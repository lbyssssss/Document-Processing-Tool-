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
  {
    path: '/annotation',
    name: 'Annotation',
    component: () => import('@/views/AnnotationView.vue'),
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/SearchView.vue'),
  },
  {
    path: '/page',
    name: 'Page',
    component: () => import('@/views/PageView.vue'),
  },
  {
    path: '/batch',
    name: 'Batch',
    component: () => import('@/views/BatchView.vue'),
  },
  {
    path: '/status',
    name: 'Status',
    component: () => import('@/views/status/StatusView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
