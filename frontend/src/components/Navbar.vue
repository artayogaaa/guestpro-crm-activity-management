<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router'; 
import { 
  AlignJustify, Share2, LayoutGrid, ChevronDown, Settings, LogOut,
  CheckCircle, XCircle, AlertCircle 
} from 'lucide-vue-next';
import logoImg from '../assets/logo.png';

// Import Composables (Global State)
import { useSidebar } from '../composables/useSidebar';
import { useNotification } from '../composables/useNotification';

const router = useRouter();
const { toggleSidebar } = useSidebar();    // Untuk tombol menu kiri
const { notification } = useNotification(); // Untuk alert notifikasi

// State Dropdown User
const isProfileMenuOpen = ref(false);
const toggleProfileMenu = () => isProfileMenuOpen.value = !isProfileMenuOpen.value;

// Ambil Username dari LocalStorage (Default 'User' jika null)
const currentUsername = ref(localStorage.getItem('username') || 'User');

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username'); 
  
  router.push('/login');
};

// Tanggal Hari Ini
const currentDate = computed(() => {
  const date = new Date();
  return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
});

const defaultAvatar = "https://ui-avatars.com/api/?name=User&background=f3f4f6&color=6b7280&size=128";
</script>

<template>
  <header class="h-20 bg-white flex items-center justify-between px-6 border-b-2 border-[#65a30d] fixed top-0 left-0 right-0 z-50">
    
    <div class="flex items-center gap-6 w-1/3">
      <button 
        @click="toggleSidebar" 
        class="text-gray-400 hover:text-gray-600 transition focus:outline-none"
      >
        <AlignJustify :size="24" />
      </button>

      <div class="border border-[#65a30d] text-[#65a30d] px-4 py-1 rounded text-sm font-medium">
        {{ currentDate }}
      </div>
    </div>

    <div class="flex justify-center w-1/3">
      <img :src="logoImg" alt="GuestPro" class="h-8 object-contain" />
    </div>

    <div class="flex items-center justify-end gap-4 w-1/3 relative h-full">
      
      <Teleport to="body">
        <Transition name="slide-cover">
          <div 
            v-if="notification.show"
            class="fixed top-0 right-0 z-[9999] flex items-center p-4 bg-white rounded-bl-xl shadow-2xl border-l-4 min-w-[320px] h-20"
            :class="{
              'border-green-500': notification.type === 'success',
              'border-red-500': notification.type === 'error',
              'border-amber-500': notification.type === 'warning',
            }"
          >
            <div class="mr-3">
              <CheckCircle v-if="notification.type === 'success'" class="text-green-500 h-8 w-8" />
              <XCircle v-if="notification.type === 'error'" class="text-red-500 h-8 w-8" />
              <AlertCircle v-if="notification.type === 'warning'" class="text-amber-500 h-8 w-8" />
            </div>
            
            <div>
              <h4 
                class="font-bold text-sm" 
                :class="{
                  'text-green-800': notification.type === 'success',
                  'text-red-800': notification.type === 'error',
                  'text-amber-800': notification.type === 'warning'
                }"
              >
                {{ notification.type === 'success' ? 'Berhasil!' : notification.type === 'error' ? 'Gagal!' : 'Perhatian!' }}
              </h4>
              <p class="text-sm text-gray-600 leading-tight">{{ notification.message }}</p>
            </div>
          </div>
        </Transition>
      </Teleport>

      <div class="flex items-center gap-4 transition-opacity duration-300" :class="{ 'opacity-0 pointer-events-none': notification.show }">

        <div class="relative">
          <div @click="toggleProfileMenu" class="flex items-center gap-3 pl-2 cursor-pointer hover:bg-gray-50 p-1 pr-2 rounded-full border border-transparent hover:border-gray-100 transition select-none">
            <span class="text-gray-700 font-medium text-sm hidden md:block ml-2">
              {{ currentUsername }}
            </span>

            <div class="flex items-center gap-1">
               <img :src="defaultAvatar" class="h-9 w-9 rounded-full border border-gray-200 object-cover" />
               <ChevronDown :size="14" class="text-gray-500 transition-transform duration-200" :class="{ 'rotate-180': isProfileMenuOpen }" />
            </div>
          </div>

          <div v-if="isProfileMenuOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-2 z-50">
            <a href="#" class="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition"><Settings :size="16" /> Settings</a>
            <div class="border-t border-gray-100 my-1"></div>
            <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition text-left"><LogOut :size="16" /> Logout</button>
          </div>
          
          <div v-if="isProfileMenuOpen" @click="isProfileMenuOpen = false" class="fixed inset-0 z-40 cursor-default"></div>
        </div>

      </div>

    </div>
  </header>
</template>

<style scoped>
/* Animasi Slide Masuk dari Kanan */
.slide-cover-enter-active,
.slide-cover-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-cover-enter-from,
.slide-cover-leave-to {
  transform: translateX(100%); /* Geser keluar ke kanan */
  opacity: 0;
}
</style>