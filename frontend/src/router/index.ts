import { createRouter, createWebHashHistory } from 'vue-router'
import ProfileView from '@/views/ProfileView.vue'
import ResumeGeneratorView from '@/views/ResumeGeneratorView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: ProfileView },
    { path: '/generate', component: ResumeGeneratorView },
  ],
})

export default router
