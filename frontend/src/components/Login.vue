<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; 
// Tambahkan AlertCircle untuk icon peringatan
import { CheckCircle, XCircle, AlertCircle } from 'lucide-vue-next'; 

// Import logo
import logoImg from '../assets/logo.png'; 

const username = ref(''); 
const password = ref('');

const notification = ref({
  show: false,
  type: 'success', // success, error, atau warning
  message: ''
});

const router = useRouter(); 

const showToast = (type, message) => {
  notification.value = { show: true, type: type, message: message };
  // Hilang otomatis setelah 3 detik
  setTimeout(() => { notification.value.show = false; }, 3000);
};

const handleLogin = async () => {
  // 1. VALIDASI MANUAL (Pengganti 'required' HTML)
  if (!username.value || !password.value) {
    showToast('warning', 'Harap isi Username dan Password!');
    return; // Stop, jangan lanjut kirim ke backend
  }

  try {
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
  }
};
</script>

<template>
  <div class="flex min-h-screen bg-gray-50 font-sans relative overflow-hidden">
    
    <Transition name="slide-fade">
      <div 
        v-if="notification.show" 
        class="fixed top-5 right-5 z-50 flex items-center p-4 bg-white rounded-xl shadow-2xl border-l-4 min-w-[300px]"
        :class="{
          'border-green-500': notification.type === 'success',
          'border-red-500': notification.type === 'error',
          'border-amber-500': notification.type === 'warning'
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
            {{ 
              notification.type === 'success' ? 'Berhasil!' : 
              notification.type === 'error' ? 'Gagal!' : 'Perhatian!' 
            }}
          </h4>
          <p class="text-sm text-gray-600">{{ notification.message }}</p>
        </div>
      </div>
    </Transition>

    <div 
      class="hidden lg:flex w-1/2 bg-cover bg-center rounded-r-3xl relative" 
      style="background-image: url('https://images.unsplash.com/photo-1594953763841-fcfb036660a4?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')"
    >
      <div class="absolute inset-0 bg-black opacity-10 rounded-r-3xl"></div>
    </div>

    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 lg:p-12">
      <div class="w-full max-w-md bg-white p-6 md:p-8 rounded-lg">
        
        <div class="flex justify-center mb-8">
          <img :src="logoImg" alt="Logo GuestPro" class="h-16 object-contain" />
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              id="username"
              v-model="username" 
              type="text" 
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 outline-none"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              id="password"
              v-model="password" 
              type="password" 
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-150 outline-none"
              placeholder="••••••••"
            />
          </div>

          <div class="flex items-center">
            <input id="remember-me" type="checkbox" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded">
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">Remember me</label>
          </div>

          <button type="submit" class="w-full bg-green-700 text-white py-3 px-4 rounded-lg hover:bg-green-800 transition duration-200 font-semibold text-lg shadow-md">
            Login
          </button>
        </form>

      </div>
    </div>

  </div>
</template>

<style scoped>
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.4s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateX(20px); opacity: 0; }
</style>