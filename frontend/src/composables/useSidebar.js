import { ref } from 'vue';

const isSidebarOpen = ref(true);    // Status utama: terbuka/tertutup
const isSidebarCollapsed = ref(true); // Status baru: ikon saja / ada teks

export function useSidebar() {
  
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value; // Ini untuk geser total
  };

  const toggleSidebarCollapse = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value; // Ini untuk mode ikon saja
  };

  return {
    isSidebarOpen,
    toggleSidebar,
    isSidebarCollapsed, // <-- Tambahkan ini
    toggleSidebarCollapse // <-- Tambahkan ini
  };
}