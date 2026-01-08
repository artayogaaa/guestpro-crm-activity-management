<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router'; 
import { 
  AlignJustify, Share2, LayoutGrid, ChevronDown, Settings, LogOut,
  CheckCircle, XCircle, AlertCircle, Minus, Plus
} from 'lucide-vue-next';
import logoImg from '../assets/logo.png';

// Import Composables (Global State)
import { useSidebar } from '../composables/useSidebar';
import { useNotification } from '../composables/useNotification';

const router = useRouter();
const { toggleSidebar } = useSidebar();
const { notification } = useNotification();

// State Dropdown User
const isProfileMenuOpen = ref(false);
const toggleProfileMenu = () => isProfileMenuOpen.value = !isProfileMenuOpen.value;

// State untuk Padding Setting
const showPaddingControl = ref(false);
const navbarPaddingX = ref(parseInt(localStorage.getItem('navbarPaddingX')) || 24); // Default 24 (px-6)
const navbarHeight = ref(parseInt(localStorage.getItem('navbarHeight')) || 120); // Default 80 (h-20)

// Toggle Padding Control Panel
const togglePaddingControl = () => {
  showPaddingControl.value = !showPaddingControl.value;
};

// Adjust Padding
const increasePadding = () => {
  if (navbarPaddingX.value < 96) {
    navbarPaddingX.value += 8;
    savePaddingSettings();
  }
};

const decreasePadding = () => {
  if (navbarPaddingX.value > 8) {
    navbarPaddingX.value -= 8;
    savePaddingSettings();
  }
};

// Adjust Height
const increaseHeight = () => {
  if (navbarHeight.value < 120) {
    navbarHeight.value += 4;
    savePaddingSettings();
  }
};

const decreaseHeight = () => {
  if (navbarHeight.value > 64) {
    navbarHeight.value -= 4;
    savePaddingSettings();
  }
};

// Reset to Default
const resetPadding = () => {
  navbarPaddingX.value = 24;
  navbarHeight.value = 80;
  savePaddingSettings();
};

// Save to LocalStorage
const savePaddingSettings = () => {
  localStorage.setItem('navbarPaddingX', navbarPaddingX.value.toString());
  localStorage.setItem('navbarHeight', navbarHeight.value.toString());
};

// Dynamic Style untuk Navbar
const navbarStyle = computed(() => ({
  height: `${navbarHeight.value}px`,
  paddingLeft: `${navbarPaddingX.value}px`,
  paddingRight: `${navbarPaddingX.value}px`
}));

// Ambil Username dari LocalStorage
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
  <header 
    class="bg-white flex items-center justify-between border-b-2 border-[#8bc34a] fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :style="navbarStyle"
  >
    
    <!-- Left Section (1/3) -->
    <div class="flex items-center gap-2 sm:gap-4 md:gap-6 flex-1 min-w-0">
      <button 
        @click="toggleSidebar" 
        class="text-gray-400 hover:text-gray-600 transition focus:outline-none flex-shrink-0"
      >
        <AlignJustify :size="20" />
      </button>

      <div class="border border-[#65a30d] text-[#65a30d] px-2 sm:px md:px-3 py-2 rounded text-xs sm:text-sm font-light whitespace-nowrap flex-shrink-0">
        {{ currentDate }}
      </div>

      <!-- Padding Control Button -->
      <button
        @click="togglePaddingControl"
        class="text-gray-400 hover:text-gray-600 transition focus:outline-none flex-shrink-0 hidden sm:block"
        title="Adjust Navbar Spacing"
      >
        <Settings :size="20" />
      </button>
    </div>

    <!-- Center Section (1/3) - Logo -->
    <div class="flex justify-center flex-1 min-w-0">
      <img :src="logoImg" alt="GuestPro" class="h-6 sm:h-7 md: w-30 h-7 object-contain" />
    </div>

    <!-- Right Section (1/3) -->
    <div class="flex items-center justify-end gap-2 sm:gap-4 flex-1 min-w-0 relative h-full">
      
      <!-- Notification Toast -->
      <Teleport to="body">
        <Transition name="slide-cover">
          <div 
            v-if="notification.show"
            class="fixed top-0 right-0 z-[9999] flex items-center p-3 sm:p-4 bg-white rounded-bl-xl shadow-2xl border-l-4 min-w-[280px] sm:min-w-[320px]"
            :class="{
              'border-green-500': notification.type === 'success',
              'border-red-500': notification.type === 'error',
              'border-amber-500': notification.type === 'warning',
            }"
            :style="{ height: `${navbarHeight}px` }"
          >
            <div class="mr-3 flex-shrink-0">
              <CheckCircle v-if="notification.type === 'success'" class="text-green-500 h-6 w-6 sm:h-8 sm:w-8" />
              <XCircle v-if="notification.type === 'error'" class="text-red-500 h-6 w-6 sm:h-8 sm:w-8" />
              <AlertCircle v-if="notification.type === 'warning'" class="text-amber-500 h-6 w-6 sm:h-8 sm:w-8" />
            </div>
            
            <div class="min-w-0">
              <h4 
                class="font-bold text-xs sm:text-sm truncate" 
                :class="{
                  'text-green-800': notification.type === 'success',
                  'text-red-800': notification.type === 'error',
                  'text-amber-800': notification.type === 'warning'
                }"
              >
                {{ notification.type === 'success' ? 'Berhasil!' : notification.type === 'error' ? 'Gagal!' : 'Perhatian!' }}
              </h4>
              <p class="text-xs sm:text-sm text-gray-600 leading-tight">{{ notification.message }}</p>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Profile Menu -->
      <div class="flex items-center gap-2 sm:gap-4 transition-opacity duration-300" :class="{ 'opacity-0 pointer-events-none': notification.show }">
        <div class="relative">
          <div 
            @click="toggleProfileMenu" 
            class="flex items-center gap-1 sm:gap-2 md:gap-3 pl-1 sm:pl-2 cursor-pointer hover:bg-gray-50 p-1 pr-1 sm:pr-2 rounded-full border border-transparent hover:border-gray-100 transition select-none"
          >
            <span class="text-gray-700 font-medium text-xs sm:text-sm hidden lg:block ml-2 truncate max-w-[100px]">
              {{ currentUsername }}
            </span>

            <div class="flex items-center gap-1">
               <img 
                 :src="defaultAvatar" 
                 class="h-8 w-8 sm:h-9 sm:w-9 rounded-full border border-gray-200 object-cover flex-shrink-0" 
               />
               <ChevronDown 
                 :size="14" 
                 class="text-gray-500 transition-transform duration-200 flex-shrink-0" 
                 :class="{ 'rotate-180': isProfileMenuOpen }" 
               />
            </div>
          </div>

          <!-- Dropdown Menu -->
          <div 
            v-if="isProfileMenuOpen" 
            class="absolute right-0 mt-2 w-44 sm:w-48 bg-white rounded-lg shadow-xl border border-gray-100 py-2 z-50"
          >
            <a 
              href="#" 
              class="flex items-center gap-3 px-4 py-2 text-xs sm:text-sm text-gray-700 hover:bg-gray-50 transition"
            >
              <Settings :size="16" /> Settings
            </a>
            <div class="border-t border-gray-100 my-1"></div>
            <button 
              @click="handleLogout" 
              class="w-full flex items-center gap-3 px-4 py-2 text-xs sm:text-sm text-red-600 hover:bg-red-50 transition text-left"
            >
              <LogOut :size="16" /> Logout
            </button>
          </div>
          
          <div 
            v-if="isProfileMenuOpen" 
            @click="isProfileMenuOpen = false" 
            class="fixed inset-0 z-40 cursor-default"
          ></div>
        </div>
      </div>
    </div>

    <!-- Padding Control Panel -->
    <Transition name="slide-down">
      <div 
        v-if="showPaddingControl" 
        class="absolute left-1/2 transform -translate-x-1/2 bg-white rounded-b-xl shadow-2xl border border-gray-200 p-4 z-[60] w-[90%] max-w-md"
        :style="{ top: `${navbarHeight}px` }"
      >
        <h3 class="font-bold text-sm text-gray-700 mb-3 flex items-center gap-2">
          <Settings :size="16" class="text-[#65a30d]" />
          Navbar Settings
        </h3>
        
        <!-- Horizontal Padding Control -->
        <div class="mb-4">
          <label class="text-xs text-gray-600 font-semibold mb-2 block">
            Horizontal Padding: <span class="text-[#65a30d]">{{ navbarPaddingX }}px</span>
          </label>
          <div class="flex items-center gap-3">
            <button 
              @click="decreasePadding" 
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded transition disabled:opacity-30"
              :disabled="navbarPaddingX <= 8"
            >
              <Minus :size="16" />
            </button>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-[#65a30d] transition-all duration-300"
                :style="{ width: `${(navbarPaddingX / 96) * 100}%` }"
              ></div>
            </div>
            <button 
              @click="increasePadding" 
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded transition disabled:opacity-30"
              :disabled="navbarPaddingX >= 96"
            >
              <Plus :size="16" />
            </button>
          </div>
        </div>

        <!-- Height Control -->
        <div class="mb-4">
          <label class="text-xs text-gray-600 font-semibold mb-2 block">
            Navbar Height: <span class="text-[#65a30d]">{{ navbarHeight }}px</span>
          </label>
          <div class="flex items-center gap-3">
            <button 
              @click="decreaseHeight" 
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded transition disabled:opacity-30"
              :disabled="navbarHeight <= 64"
            >
              <Minus :size="16" />
            </button>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-[#65a30d] transition-all duration-300"
                :style="{ width: `${((navbarHeight - 64) / 56) * 100}%` }"
              ></div>
            </div>
            <button 
              @click="increaseHeight" 
              class="p-2 bg-gray-100 hover:bg-gray-200 rounded transition disabled:opacity-30"
              :disabled="navbarHeight >= 120"
            >
              <Plus :size="16" />
            </button>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-2">
          <button 
            @click="resetPadding" 
            class="flex-1 px-3 py-2 text-xs font-semibold text-gray-600 border border-gray-300 rounded hover:bg-gray-50 transition"
          >
            Reset Default
          </button>
          <button 
            @click="showPaddingControl = false" 
            class="flex-1 px-3 py-2 text-xs font-semibold text-white bg-[#65a30d] rounded hover:bg-[#558b0a] transition"
          >
            Close
          </button>
        </div>
      </div>
    </Transition>

    <!-- Overlay -->
    <div 
      v-if="showPaddingControl" 
      @click="showPaddingControl = false" 
      class="fixed inset-0 bg-black/20 z-[55]"
    ></div>

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
  transform: translateX(100%);
  opacity: 0;
}

/* Animasi Slide Down untuk Control Panel */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  transform: translateX(-50%) translateY(-20px);
  opacity: 0;
}
</style>