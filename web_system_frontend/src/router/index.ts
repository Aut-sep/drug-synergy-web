import { createRouter, createWebHistory } from 'vue-router'

const appTitle = '药物协同预测系统'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: () => import('../views/DashboardView.vue'), meta: { title: '系统总览' } },
    { path: '/system-guide', component: () => import('../views/SystemGuideView.vue'), meta: { title: '系统说明' } },
    { path: '/datasets', component: () => import('../views/DatasetsView.vue'), meta: { title: '数据集管理' } },
    { path: '/inference', component: () => import('../views/InferenceView.vue'), meta: { title: '推理工作台' } },
    { path: '/training', component: () => import('../views/TrainingView.vue'), meta: { title: '训练中心' } },
    { path: '/versions', component: () => import('../views/VersionsView.vue'), meta: { title: '版本中心' } },
    { path: '/runs', component: () => import('../views/RunsView.vue'), meta: { title: '任务中心' } },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.afterEach((to) => {
  document.title = `${String(to.meta.title ?? appTitle)} | ${appTitle}`
})

export default router
