<script setup>
import { ref, onMounted } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api'; 
import { Plus, Trash2, Edit, X, AlertTriangle } from 'lucide-vue-next';

// --- IMPORT GLOBAL NOTIFICATION ---
import { useNotification } from '../composables/useNotification';

// Gunakan showToast dari global
const { showToast } = useNotification();

const activities = ref([]);
const showFormModal = ref(false);
const showDeleteModal = ref(false);
const isEditing = ref(false);
const itemToDelete = ref(null);
const form = ref({ id: null, title: '', description: '', date: '', status: 'pending' });

// --- API CALLS ---
const fetchActivities = async () => {
  try {
    const response = await api.get('activities/');
    activities.value = response.data;
  } catch (error) {
    showToast('error', 'Gagal memuat data aktivitas');
  }
};

const createActivity = async () => {
  if(!form.value.title || !form.value.date) {
    showToast('warning', 'Judul dan Tanggal wajib diisi!');
    return;
  }
  try {
    await api.post('activities/', form.value);
    closeFormModal();
    fetchActivities(); 
    showToast('success', 'Aktivitas berhasil ditambahkan!'); // <-- Ini akan muncul di Navbar
  } catch (error) {
    showToast('error', 'Gagal menyimpan data');
  }
};

const updateActivity = async () => {
  if(!form.value.title || !form.value.date) {
    showToast('warning', 'Judul dan Tanggal wajib diisi!');
    return;
  }
  try {
    await api.put(`activities/${form.value.id}/`, form.value);
    closeFormModal();
    fetchActivities();
    showToast('success', 'Aktivitas berhasil diperbarui!'); // <-- Ini akan muncul di Navbar
  } catch (error) {
    showToast('error', 'Gagal mengupdate data');
  }
};

const confirmDelete = (id) => {
  itemToDelete.value = id;
  showDeleteModal.value = true;
};

const executeDelete = async () => {
  try {
    await api.delete(`activities/${itemToDelete.value}/`);
    fetchActivities();
    showDeleteModal.value = false;
    itemToDelete.value = null;
    showToast('success', 'Aktivitas berhasil dihapus'); // <-- Ini akan muncul di Navbar
  } catch (error) {
    showToast('error', 'Gagal menghapus data');
    showDeleteModal.value = false;
  }
};

// --- MODAL LOGIC ---
const openFormModal = (item = null) => {
  if (item) { isEditing.value = true; form.value = { ...item }; } 
  else { isEditing.value = false; form.value = { id: null, title: '', description: '', date: '', status: 'pending' }; }
  showFormModal.value = true;
};
const closeFormModal = () => showFormModal.value = false;
const handleSubmit = () => isEditing.value ? updateActivity() : createActivity();

onMounted(() => { fetchActivities(); });
</script>

<template>
  <MainLayout>
    <div class="pt-24"></div>
    <div class="flex justify-between items-center mb-6 py-1">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Activity List</h1>
        <p class="text-gray-500">Kelola kegiatan harian Anda di sini.</p>
      </div>
      <button @click="openFormModal()" class="bg-[#8bc34a] hover:bg-[#7cb342] text-white text-xs px-4 py-2 flex items-center gap-2 transition">
        <Plus :size="20" /> Tambah Data
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead class="bg-gray-50 text-gray-600 uppercase text-xs font-bold">
          <tr>
            <th class="p-4 border-b">Judul Aktivitas</th>
            <th class="p-4 border-b">Tanggal</th>
            <th class="p-4 border-b">Status</th>
            <th class="p-4 border-b text-center">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="item in activities" :key="item.id" class="hover:bg-gray-50 transition">
            <td class="p-4">
              <div class="font-medium text-gray-800">{{ item.title }}</div>
              <div class="text-sm text-gray-500 truncate max-w-xs">{{ item.description }}</div>
            </td>
            <td class="p-4 text-gray-600">{{ item.date }}</td>
            <td class="p-4">
              <span class="px-3 py-1 rounded text-xs font-semibold" :class="item.status === 'completed' ? 'bg-[#8bc34a] text-white' : 'bg-amber-100 text-amber-700'">
                {{ item.status === 'completed' ? 'Selesai' : 'Pending' }}
              </span>
            </td>
            <td class="p-4 text-center">
              <div class="flex justify-center gap-2">
                <button @click="openFormModal(item)" class="text-blue-500 hover:bg-blue-50 p-2 rounded transition"><Edit :size="18" /></button>
                <button @click="confirmDelete(item.id)" class="text-red-500 hover:bg-red-50 p-2 rounded transition"><Trash2 :size="18" /></button>
              </div>
            </td>
          </tr>
          <tr v-if="activities.length === 0">
            <td colspan="4" class="p-8 text-center text-gray-400">Belum ada data aktivitas.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showFormModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-50 p-4 backdrop-blur-sm">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 relative animate-fade-in-up">
        <button @click="closeFormModal" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600"><X :size="20" /></button>
        <h3 class="text-xl font-bold text-gray-800 mb-4">{{ isEditing ? 'Edit Aktivitas' : 'Tambah Aktivitas Baru' }}</h3>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div><label class="block text-sm text-gray-700 mb-1">Judul</label><input v-model="form.title" type="text" class="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-[#65a30d]" placeholder="Judul"></div>
          <div><label class="block text-sm text-gray-700 mb-1">Deskripsi</label><textarea v-model="form.description" rows="3" class="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-[#65a30d]" placeholder="Deskripsi"></textarea></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-sm text-gray-700 mb-1">Tanggal</label><input v-model="form.date" type="date" class="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-[#65a30d]"></div>
            <div><label class="block text-sm text-gray-700 mb-1">Status</label><select v-model="form.status" class="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-[#65a30d]"><option value="pending">Pending</option><option value="completed">Selesai</option></select></div>
          </div>
          <div class="pt-4 flex gap-3">
            <button type="button" @click="closeFormModal" class="flex-1 bg-gray-100 py-2 rounded-lg">Batal</button>
            <button type="submit" class="flex-1 bg-[#8bc34a] text-white py-2 rounded-lg">Simpan</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDeleteModal" class="fixed inset-0 z-[70] flex items-center justify-center bg-black bg-opacity-40 p-4 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center relative animate-bounce-in">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4"><AlertTriangle :size="32" class="text-red-600" /></div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">Hapus Aktivitas?</h3>
        <p class="text-gray-500 text-sm mb-6">Tindakan ini tidak dapat dibatalkan.</p>
        <div class="flex gap-3 justify-center">
          <button @click="showDeleteModal = false" class="px-5 py-2.5 rounded-lg bg-gray-100 font-medium hover:bg-gray-200">Batal</button>
          <button @click="executeDelete" class="px-5 py-2.5 rounded-lg bg-red-600 text-white font-medium hover:bg-red-700 shadow-lg shadow-red-200">Ya, Hapus</button>
        </div>
      </div>
    </div>

  </MainLayout>
</template>

<style scoped>

@keyframes bounceIn { 0% { opacity: 0; transform: scale(0.3); } 50% { opacity: 1; transform: scale(1.05); } 70% { transform: scale(0.9); } 100% { transform: scale(1); } }
.animate-bounce-in { animation: bounceIn 0.4s cubic-bezier(0.215, 0.610, 0.355, 1.000); }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out; }
</style>