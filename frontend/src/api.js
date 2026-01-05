import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
});

// 1. REQUEST INTERCEPTOR: Selipkan Token sebelum kirim
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 2. RESPONSE INTERCEPTOR: Handle Token Mati (401)
api.interceptors.response.use(
  (response) => response, // Jika sukses, lewatkan saja
  async (error) => {
    const originalRequest = error.config;

    // Cek jika Error 401 dan belum pernah dicoba refresh sebelumnya (_retry)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Tandai biar gak looping infinite

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
          throw new Error("No refresh token");
        }

        // Minta token baru ke Backend
        // Kita pakai axios biasa (bukan instance 'api') biar gak kena interceptor ini lagi
        const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
          refresh: refreshToken
        });

        if (response.status === 200) {
          // 1. Simpan Token Baru
          const newAccessToken = response.data.access;
          localStorage.setItem('access_token', newAccessToken);

          // 2. Update Header default & request yang gagal tadi
          api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

          // 3. Ulangi Request Awal
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Jika Refresh Token juga mati (atau tidak ada), paksa Logout
        console.error("Session expired. Please login again.");
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login'; // Redirect ke halaman login
      }
    }

    return Promise.reject(error);
  }
);

export default api;