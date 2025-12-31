import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/views/project/ProjectList.vue'),
        meta: { title: '项目管理', icon: 'Folder' },
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/project/ProjectDetail.vue'),
        meta: { title: '项目详情', hidden: true },
      },
      {
        path: 'cases/:id/edit',
        name: 'CaseEdit',
        component: () => import('@/views/case/CaseEdit.vue'),
        meta: { title: '用例编辑', hidden: true },
      },
      {
        path: 'suites',
        name: 'SuiteList',
        component: () => import('@/views/suite/SuiteList.vue'),
        meta: { title: '测试集', icon: 'Collection' },
      },
      {
        path: 'suites/:id',
        name: 'SuiteDetail',
        component: () => import('@/views/suite/SuiteDetail.vue'),
        meta: { title: '测试集详情', hidden: true },
      },
      {
        path: 'schedules',
        name: 'ScheduleList',
        component: () => import('@/views/schedule/ScheduleList.vue'),
        meta: { title: '定时任务', icon: 'Clock' },
      },
      {
        path: 'executions',
        name: 'ExecutionList',
        component: () => import('@/views/execution/ExecutionList.vue'),
        meta: { title: '执行历史', icon: 'Document' },
      },
      {
        path: 'executions/:id',
        name: 'ExecutionDetail',
        component: () => import('@/views/execution/ExecutionDetail.vue'),
        meta: { title: '执行详情', hidden: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - ApiPilot` : 'ApiPilot'
  next()
})

export default router
