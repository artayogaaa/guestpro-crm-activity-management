<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; 
import { CheckCircle, XCircle, AlertCircle } from 'lucide-vue-next'; 

// Import logo
import logoImg from '../assets/logo.png'; 

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
  <div class="min-h-screen flex items-center justify-center bg-gray-100 relative overflow-hidden">
    
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

    <!-- MAIN CONTAINER -->
    <div class="w-full max-w-4xl bg-white shadow-xl rounded-xl overflow-hidden grid grid-cols-1 md:grid-cols-2">

      <!-- LEFT IMAGE SIDE -->
      <div class="hidden md:flex flex-col justify-center bg-gradient-to-br from-[#8BC34A] to-[#7CB342] p-10 text-white">
        <h2 class="text-2xl font-bold mb-3">
          Welcome to GuestPro Internal App
        </h2>
        <p class="text-sm opacity-90">
          Please use your credentials to login.<br />
          Manage your guest experience efficiently and professionally.
        </p>
      </div>

      <!-- FORM SIDE -->
      <div class="p-10 flex flex-col justify-center">
        <div class="mb-6 flex justify-center">
          <img :src="logoImg" alt="Logo GuestPro" class="h-12 object-contain" />
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="username" class="block text-xs font-medium text-gray-500 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              class="w-full bg-white border border-gray-300 rounded px-4 py-3 focus:ring-1 focus:ring-[#8BC34A] focus:border-[#8BC34A] outline-none transition text-sm"
              placeholder=""
            />
          </div>

          <div class="relative">
            <label for="password" class="block text-xs font-medium text-gray-500 mb-2">
              Password
            </label>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="w-full bg-white border border-gray-300 rounded px-4 py-3 pr-12 focus:ring-1 focus:ring-[#8BC34A] focus:border-[#8BC34A] outline-none transition text-sm"
              placeholder=""
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
            >
              <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>

          <div class="pt-2">
            <button
              type="submit"
              :disabled="processing"
              class="w-full px-6 py-3 rounded bg-[#8BC34A] text-white font-bold hover:bg-[#7CB342] disabled:opacity-50 disabled:cursor-not-allowed transition duration-200 uppercase tracking-wide text-sm"
            >
              {{ processing ? 'Loading...' : 'LOGIN' }}
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