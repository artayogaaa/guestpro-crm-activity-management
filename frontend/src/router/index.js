import { createRouter, createWebHistory } from 'vue-router';

// 1. IMPORT COMPONENT ASLI (Bukan Placeholder lagi)
import Login from '../components/Login.vue';
import Leads from '../components/Leads.vue';
import DealingProperty from '../components/DealingProperty.vue';

// Pastikan file ini ada di folder components Anda!
// Jika belum ada, buat file Dashboard.vue dan UserManagement.vue (lihat kode di bawah)
import Dashboard from '../components/Dashboard.vue'; 
import UserManagement from '../components/UserManagement.vue';

const routes = [
  { 
    path: '/login', 
    name: 'Login', 
    component: Login,
    meta: { layout: 'empty' } 
  },
  { 
    path: '/', 
    name: 'Dashboard', 
    component: Dashboard, // Sekarang menggunakan component asli
    meta: { requiresAuth: true }
  },
  { 
    path: '/leads', 
    name: 'Leads', 
    component: Leads, 
    meta: { requiresAuth: true }
  },
  { 
    path: '/dealing-property', 
    name: 'DealingProperty', 
    component: DealingProperty, 
    meta: { requiresAuth: true }
  },
  { 
    path: '/users', 
    name: 'UserManagement', 
    component: UserManagement, // Sekarang menggunakan component asli
    meta: { requiresAuth: true }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router;