<script setup>
import { ref, onMounted } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api';
import { useNotification } from '../composables/useNotification';
import { Plus, Edit, Trash2, User, Mail, Save, X, ShieldCheck } from 'lucide-vue-next';

const { showToast } = useNotification();

// STATE
const users = ref([]);
const showModal = ref(false);
const isEditing = ref(false);

const form = ref({
  id: null,
  username: '',
  email: '',
  password: ''
});

// API CALLS
const fetchUsers = async () => {
  try {
    const response = await api.get('users/');
    users.value = response.data;
  } catch (error) {
    showToast('error', 'Gagal memuat data user');
  }
};

const saveUser = async () => {
  try {
    if (isEditing.value) {
      // Edit: Kirim password hanya jika diisi
      const payload = { username: form.value.username, email: form.value.email };
      if (form.value.password) payload.password = form.value.password;
      
      await api.patch(`users/${form.value.id}/`, payload);
      showToast('success', 'User berhasil diupdate');
    } else {
      // Create
      await api.post('users/', form.value);
      showToast('success', 'User baru berhasil dibuat');
    }
    closeModal();
    fetchUsers();
  } catch (error) {
    showToast('error', 'Gagal menyimpan data');
  }
};

const deleteUser = async (id) => {
  if (!confirm("Yakin hapus user ini?")) return;
  try {
    await api.delete(`users/${id}/`);
    fetchUsers();
    showToast('success', 'User berhasil dihapus');
  } catch (error) {
    showToast('error', 'Gagal menghapus user');
  }
};

// MODAL LOGIC
const openModal = (user = null) => {
  if (user) {
    isEditing.value = true;
    form.value = { ...user, password: '' }; // Password kosong saat edit
  } else {
    isEditing.value = false;
    form.value = { id: null, username: '', email: '', password: '' };
  }
  showModal.value = true;
};

const closeModal = () => showModal.value = false;

onMounted(() => {
  fetchUsers();
});
</script>

<template>
  <MainLayout>
    <div class="pt-24"></div>
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">User Management</h1>
        <p class="text-gray-500">Kelola akses pengguna aplikasi.</p>
      </div>
      <button @click="openModal()" class="bg-[#65a30d] hover:bg-[#4d7c0f] text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow transition font-bold">
        <Plus :size="18" /> Tambah User
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-left text-sm border-collapse">
        <thead class="bg-gray-50 text-gray-600 font-bold uppercase text-xs">
          <tr>
            <th class="p-4 border-b w-16">ID</th>
            <th class="p-4 border-b">Username</th>
            <th class="p-4 border-b">Email</th>
            <th class="p-4 border-b text-center w-32">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition">
            <td class="p-4 font-mono text-gray-500">#{{ user.id }}</td>
            <td class="p-4">
              <div class="flex items-center gap-3">
                <div class="bg-[#8bc34a] p-2 rounded-full text-white">
                  <User :size="16" />
                </div>
                <span class="font-bold text-gray-700">{{ user.username }}</span>
              </div>
            </td>
            <td class="p-4 text-gray-600">
              <div class="flex items-center gap-2">
                <Mail :size="14" /> {{ user.email || '-' }}
              </div>
            </td>
            <td class="p-4 text-center">
              <div class="flex justify-center gap-2">
                <button @click="openModal(user)" class="text-blue-500 hover:bg-blue-50 p-2 rounded transition" title="Edit">
                  <Edit :size="18" />
                </button>
                <button @click="deleteUser(user.id)" class="text-red-500 hover:bg-red-50 p-2 rounded transition" title="Hapus">
                  <Trash2 :size="18" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-md relative animate-fade-in-up">
          <div class="p-6 border-b flex justify-between items-center">
            <h3 class="text-xl font-bold text-gray-800 flex items-center gap-2">
              <ShieldCheck :size="20" class="text-blue-600"/>
              {{ isEditing ? 'Edit User' : 'Tambah User Baru' }}
            </h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><X :size="24" /></button>
          </div>
          
          <form @submit.prevent="saveUser" class="p-6 space-y-4">
            <div>
              <label class="label">Username</label>
              <input v-model="form.username" type="text" class="input" required placeholder="Contoh: admin_bali">
            </div>
            <div>
              <label class="label">Email</label>
              <input v-model="form.email" type="email" class="input" required placeholder="user@guestpro.com">
            </div>
            
            <div>
              <label class="label">Password</label>
              <input v-model="form.password" type="password" class="input" :placeholder="isEditing ? 'Isi hanya jika ingin ubah password' : '********'">
              <p v-if="!isEditing" class="text-xs text-gray-400 mt-1">Minimal 8 karakter.</p>
            </div>

            <div class="pt-4 flex justify-end gap-3 border-t">
              <button type="button" @click="closeModal" class="px-4 py-2 bg-white border rounded-lg text-sm font-medium hover:bg-gray-50">Batal</button>
              <button type="submit" class="px-4 py-2 bg-[#65a30d] text-white rounded-lg text-sm font-bold hover:bg-[#4d7c0f] flex items-center gap-2">
                <Save :size="16" /> Simpan
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </MainLayout>
</template>

<style scoped>
.label { @apply block text-xs font-semibold text-gray-500 mb-1; }
.input { @apply w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-[#65a30d] outline-none; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out; }
</style>