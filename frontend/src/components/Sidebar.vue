<script setup>
import { 
  Home, Users, Calendar, Settings, LogOut,
  LayoutGrid, ShoppingCart, TrendingUp, FolderOpen, Bell, MessageSquare, Briefcase, 
  ChevronLeft, ChevronRight, UserCog, 
  Table
} from 'lucide-vue-next';
import { useRouter } from 'vue-router';
import { useSidebar } from '../composables/useSidebar';

const { isSidebarOpen, isSidebarCollapsed, toggleSidebar, toggleSidebarCollapse } = useSidebar();
const router = useRouter();

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  router.push('/login');
};

// DAFTAR MENU UPDATED
const menuItems = [
  { name: 'Dashboard', icon: Home, route: '/' },
  { name: 'Leads / Contacts', icon: Users, route: '/leads' },
  // --- MENU BARU ---
  { name: 'Dealing Property', icon: Briefcase, route: '/dealing-property' },
  { name: 'Lead Table', icon: Table, route: '/leadTable' },
  { name: 'User Management', icon: UserCog, route: '/users' },
];
</script>

<template>
  <aside 
    class="bg-white text-gray-800 flex flex-col h-screen fixed left-0 top-0 shadow-lg z-40 pt-20 transition-all duration-300 ease-in-out border-r border-gray-200"
    :class="{ 
      'w-16': isSidebarCollapsed,         /* Lebar saat collapsed (ikon saja) */
      'w-56': !isSidebarCollapsed,        /* Lebar saat expanded (ada teks) */
      'translate-x-0': isSidebarOpen,     /* Geser masuk */
      '-translate-x-full': !isSidebarOpen /* Geser keluar total */
    }"
  >
    
    <nav class="flex-1 px-1 py-4 space-y-1 pt-12">
      <router-link 
        v-for="item in menuItems" 
        :key="item.name" 
        :to="item.route" 
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-blue-100 hover:text-blue-700 transition relative group"
        :class="{
            'justify-center': isSidebarCollapsed, 
            'bg-blue-50 text-blue-700 font-semibold': $route.path === item.route && isSidebarCollapsed,
            'bg-blue-50 text-blue-700 font-semibold pl-4': $route.path === item.route && !isSidebarCollapsed
        }"
      >
        <component :is="item.icon" :size="18" />
        <span v-if="!isSidebarCollapsed" class="font-medium text-sm whitespace-nowrap">{{ item.name }}</span>
        
        <div v-if="isSidebarCollapsed" class="absolute left-full ml-4 whitespace-nowrap bg-gray-700 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 z-50 shadow-lg">
            {{ item.name }}
        </div>
      </router-link>
    </nav>

    <div class="px-3 py-4 border-t border-gray-200 text-sm">
      <button 
        @click="toggleSidebarCollapse" 
        class="absolute -right-3 top-1/2 -translate-y-1/2 text-white p-1 rounded-full shadow-md bg-[#8bc34a] hover:bg-[#7cb342] transition"
        :class="{ 'hidden': !isSidebarOpen }"
      >
        <ChevronLeft :size="16" v-if="!isSidebarCollapsed" />
        <ChevronRight :size="16" v-else />
      </button>

    </div>
  </aside>
</template>

<style scoped>
/* Menghilangkan border dan background default router-link-active */
.router-link-active {
  /* Class `bg-blue-50 text-blue-700 font-semibold` sudah di inline */
}

/* Tooltip style - make it show on hover when collapsed */
nav a div {
    /* Style inline di atas sudah menangani posisi, tapi ini backup untuk transisi halus */
    transition: opacity 0.2s ease, left 0.2s ease;
}

nav a:hover div {
    /* Sedikit animasi geser saat muncul */
    left: calc(100% + 0.5rem); 
}
</style>