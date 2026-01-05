<script setup>
import Navbar from '../components/Navbar.vue';
import Sidebar from '../components/Sidebar.vue';
import { useSidebar } from '../composables/useSidebar';

// Ambil kedua state
const { isSidebarOpen, isSidebarCollapsed } = useSidebar();
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    
    <Navbar />
    <Sidebar />

    <div class="flex flex-1">
      <main 
        class="flex-1 p-8 transition-all duration-300 ease-in-out"
        :class="{
          'ml-16': isSidebarOpen && isSidebarCollapsed,    /* Jika terbuka & ikon saja */
          'ml-56': isSidebarOpen && !isSidebarCollapsed,   /* Jika terbuka & ada teks */
          'ml-0': !isSidebarOpen                          /* Jika tertutup total */
        }"
      >
        <slot />
      </main>
    </div>
    
  </div>
</template>