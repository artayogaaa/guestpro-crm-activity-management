import { ref } from 'vue';

// State dibuat di luar fungsi agar bersifat GLOBAL (bisa diakses semua file)
const notification = ref({
  show: false,
  type: 'success', // success, error, warning
  message: ''
});

export function useNotification() {
  
  const showToast = (type, message) => {
    notification.value = { show: true, type, message };
    
    // Hilang otomatis setelah 3 detik
    setTimeout(() => {
      notification.value.show = false;
    }, 3000);
  };

  return {
    notification,
    showToast
  };
}