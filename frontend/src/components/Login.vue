<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; 
import { CheckCircle, XCircle, AlertCircle, Eye, EyeOff } from 'lucide-vue-next'; 

import logoImg from '../assets/logo.png';
import dashboardImg from '../assets/placeholder-dashboard.png';
import googlePlayBadge from '../assets/google-play-badge.png'; 

const username = ref(''); 
const password = ref('');
const processing = ref(false);
const showPassword = ref(false);

const notification = ref({
  show: false,
  type: 'success',
  message: ''
});

const router = useRouter(); 

const showToast = (type, message) => {
  notification.value = { show: true, type: type, message: message };
  setTimeout(() => { notification.value.show = false; }, 3000);
};

const handleLogin = async () => {
  if (!username.value || !password.value) {
    showToast('warning', 'Harap isi Username dan Password!');
    return;
  }

  try {
    processing.value = true;
    notification.value.show = false;
    
    const response = await axios.post('http://127.0.0.1:8000/api/token/', {
      username: username.value, 
      password: password.value
    });

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('username', username.value);
    
    showToast('success', 'Login Berhasil! Mengalihkan...');
    
    setTimeout(() => { router.push('/'); }, 1500);

  } catch (error) {
    console.error("Login Gagal:", error.response ? error.response.data : error.message);
    showToast('error', 'Username atau password salah');
  } finally {
    processing.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 relative overflow-hidden">
    
    <!-- NOTIFICATION TOAST -->
    <Transition name="slide-fade">
      <div 
        v-if="notification.show" 
        class="fixed top-5 right-5 z-50 flex items-center p-4 bg-white rounded-xl shadow-2xl border-l-4 min-w-[300px]"
        :class="{
          'border-[#8BC34A]': notification.type === 'success',
          'border-red-500': notification.type === 'error',
          'border-amber-500': notification.type === 'warning'
        }"
      >
        <div class="mr-3">
          <CheckCircle v-if="notification.type === 'success'" class="text-[#8BC34A] h-8 w-8" />
          <XCircle v-if="notification.type === 'error'" class="text-red-500 h-8 w-8" />
          <AlertCircle v-if="notification.type === 'warning'" class="text-amber-500 h-8 w-8" />
        </div>
        
        <div>
          <h4 
            class="font-bold text-sm" 
            :class="{
              'text-[#7CB342]': notification.type === 'success',
              'text-red-800': notification.type === 'error',
              'text-amber-800': notification.type === 'warning'
            }"
          >
            {{ 
              notification.type === 'success' ? 'Berhasil!' : 
              notification.type === 'error' ? 'Gagal!' : 'Perhatian!' 
            }}
          </h4>
          <p class="text-sm text-gray-600">{{ notification.message }}</p>
        </div>
      </div>
    </Transition>

    <!-- LEFT SIDE - IMAGE/BRANDING -->
    <div class="hidden lg:flex lg:w-2/3 h-screen relative">
      <div class="absolute inset-0 bg-gradient-to-br from-gray-100 to-gray-200">
        <!-- Dashboard image -->
        <div class="absolute inset-0">
          <img :src="dashboardImg" alt="Dashboard Preview" class="w-full h-full object-cover" />
        </div>
      </div>
    </div>

    <div class="w-full lg:w-1/3 h-screen flex items-center bg-white justify-center px-10 lg:px-16">
      <div class="w-full max-w-sm">
        <!-- Logo -->
        <div class="mb-10 flex items-center justify-start">
          <div class="flex items-center">
            <div class="absolute top-50 left-50">
              <img :src="logoImg" alt="Get it on Google Play" class="h-10" />
            </div>
            <div>
              <span class="text-2xl font-bold text-[#8BC34A]">Guest</span>
              <span class="text-2xl font-bold text-[#7CB342]">Pro</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label for="username" class="block text-xs font-normal text-gray-600 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="w-full bg-white border border-gray-300 px-4 py-3 focus:ring-2 focus:ring-[#8BC34A] focus:border-transparent outline-none transition text-xs"
              placeholder=""
            />
          </div>

          <!-- Password -->
          <div class="relative">
            <label for="password" class="block text-xs font-normal text-gray-600 mb-2">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="w-full bg-white border border-gray-300 px-4 py-3 pr-12 focus:ring-2 focus:ring-[#8BC34A] focus:border-transparent outline-none transition text-sm"
                placeholder=""
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <Eye v-if="!showPassword" class="w-5 h-5" />
                <EyeOff v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Login Button -->
          <div class="pt-3">
            <button
              type="submit"
              :disabled="processing"
              class="w-full px-6 py-3 rounded bg-[#8BC34A] text-white font-semibold hover:bg-[#7CB342] disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 uppercase tracking-wide text-sm"
            >
              {{ processing ? 'LOADING...' : 'LOGIN' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slide-fade-enter-active { 
  transition: all 0.3s ease-out; 
}
.slide-fade-leave-active { 
  transition: all 0.4s cubic-bezier(1, 0.5, 0.8, 1); 
}
.slide-fade-enter-from, 
.slide-fade-leave-to { 
  transform: translateX(20px); 
  opacity: 0; 
}
</style>