import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/stores/user';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/check-detail/:id',
    name: 'CheckDetail',
    component: () => import('@/views/CheckDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/reports',
    name: 'ReportManage',
    component: () => import('@/views/ReportManageView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const requiresAuth = to.meta.requiresAuth !== false;

  // Initialize user store from localStorage if not already done
  if (!userStore.isLoggedIn) {
    userStore.initializeFromStorage();
  }

  if (requiresAuth && !userStore.isLoggedIn) {
    // Redirect to login if authentication is required
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.name === 'Login' && userStore.isLoggedIn) {
    // Redirect to dashboard if already logged in
    next({ name: 'Dashboard' });
  } else {
    next();
  }
});

export default router;
