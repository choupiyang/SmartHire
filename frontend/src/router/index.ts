/**
 * 路由配置
 * 根据设备类型自动切换移动端/桌面端视图
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useDeviceStore } from '@stores/device';

// 移动端路由
const mobileRoutes: RouteRecordRaw[] = [
  {
    path: '/radar',
    name: 'mobile-radar',
    component: () => import('@views/mobile/RadarView.vue'),
    meta: {
      title: '五维雷达',
    },
  },
  {
    path: '/analysis',
    name: 'mobile-analysis',
    component: () => import('@views/mobile/AnalysisView.vue'),
    meta: {
      title: '数据分析',
    },
  },
  {
    path: '/profile',
    name: 'mobile-profile',
    component: () => import('@views/mobile/ProfileView.vue'),
    meta: {
      title: '我的',
    },
  },
];

// 首页路由 - 使用别名保持URL一致
const homeRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    // 动态导入组件
    component: () => import('@views/shared/HomeView.vue'),
    meta: {
      title: '智雇家',
    },
  },
];

// 桌面端路由 - 无前缀（保持原有路径）
const desktopRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'desktop-home',
    component: () => import('@views/desktop/HomeView.vue'),
    meta: {
      title: '智雇家',
    },
  },
  {
    path: '/dashboard',
    name: 'desktop-dashboard',
    component: () => import('@views/desktop/DashboardView.vue'),
    meta: {
      title: '数据仪表板',
    },
  },
  {
    path: '/detail/:id',
    name: 'desktop-detail',
    component: () => import('@views/desktop/DetailView.vue'),
    meta: {
      title: '详情',
    },
  },
  {
    path: '/settings',
    name: 'desktop-settings',
    component: () => import('@views/desktop/SettingsView.vue'),
    meta: {
      title: '设置',
    },
  },
];

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...homeRoutes,       // 首页路由
    ...mobileRoutes,    // 移动端路由
    ...desktopRoutes,   // 桌面端路由
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: '/',
    },
  ],
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} | 智雇家`;
  }

  next();
});

// 滚动行为
router.afterEach((to, from) => {
  // 如果是同一页面，不滚动
  if (to.path === from.path) {
    return;
  }

  // 滚动到顶部
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
  });
});

export default router;
