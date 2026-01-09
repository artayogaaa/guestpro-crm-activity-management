<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api';
import { useNotification } from '../composables/useNotification';
import { 
  Search, Plus, Trash2, Edit, Loader2, Save, X,
  ChevronLeft, ChevronRight, ExternalLink, Users
} from 'lucide-vue-next';

const { showToast } = useNotification();
const leads = ref([]);
const isLoading = ref(false);

// --- DATA CONSTANT ---
const picList = [
  'EKA', 'SURYA', 'ANGGA', 'RUSDIANA', 'WIRA', 'YOGA', 
  'WAHYU', 'WULAN', 'TRISNA', 'SURYANI', 'WIDI', 'NIA'
];

const sourceOptions = [
  'Website', 'Referral', 'Reff', 'Reff No Commission', 
  'Social Media', 'Affiliate', 'Cold Calling', 'Canvassing',
  'Campaign', 'Free Trial', 'Relational'
];

const statusKanbanOptions = [
  { value: 'lead_generation', label: 'Lead Generation' },
  { value: 'follow_up', label: 'Follow Up' },
  { value: 'quotation', label: 'Quotation' },
  { value: 'deals', label: 'Deals' },
  { value: 'onboarding', label: 'Onboarding' },
  { value: 'retention', label: 'Retention' }
];

// --- STATE FILTER ---
const searchQuery = ref('');
const filterGpPic = ref('');
const filterStatus = ref('');
const filterSource = ref('');

// State Edit
const editingCell = ref(null);
const inputRefs = ref({});

// State Modal PICs
const showPicsModal = ref(false);
const selectedLeadForPics = ref(null);
const formPicsEdit = ref([]);

// State for PIC Details Popup
const showPicsPopup = ref(false);
const picsPopupData = ref([]);
const popupPosition = ref({ top: 0, left: 0 });

// ==========================================
// COMPUTED
// ==========================================
const uniqueGpPicOptions = computed(() => {
  const pics = leads.value.map(l => l.gp_pic).filter(p => p);
  return [...new Set(pics)];
});

const uniqueSourceOptions = computed(() => {
  const sources = leads.value.map(l => l.source).filter(s => s);
  return [...new Set(sources)];
});

const filteredLeads = computed(() => {
  const result = leads.value.filter(lead => {
    const matchSearch = !searchQuery.value || 
      (lead.property && lead.property.toLowerCase().includes(searchQuery.value.toLowerCase()));
    
    const matchGpPic = !filterGpPic.value || lead.gp_pic === filterGpPic.value;
    const matchStatus = !filterStatus.value || lead.status_kanban === filterStatus.value;
    const matchSource = !filterSource.value || lead.source === filterSource.value;

    return matchSearch && matchGpPic && matchStatus && matchSource;
  });
  
  return result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
});

// ==========================================
// ACTIONS
// ==========================================
const fetchLeads = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('leads/table_view/');
    leads.value = response.data;
  } catch (error) {
    showToast('error', 'Gagal memuat data leads');
  } finally {
    isLoading.value = false;
  }
};

const deleteLead = async (leadId) => {
  if (!confirm('Apakah Anda yakin ingin menghapus lead ini?')) return;
  
  try {
    await api.delete(`leads/${leadId}/`);
    showToast('success', 'Lead berhasil dihapus');
    fetchLeads();
  } catch (error) {
    showToast('error', 'Gagal menghapus lead');
  }
};

// ==========================================
// SPREADSHEET EDIT
// ==========================================
const editCell = (leadId, field) => {
  editingCell.value = { id: leadId, field: field };
  nextTick(() => {
    const el = inputRefs.value[`${leadId}-${field}`];
    if (el) el.focus();
  });
};

const isEditing = (leadId, field) => {
  return editingCell.value && 
    editingCell.value.id === leadId && 
    editingCell.value.field === field;
};

const saveCell = async (lead, field) => {
  editingCell.value = null;
  try {
    await api.patch(`leads/${lead.lead_id}/`, { [field]: lead[field] });
    showToast('success', 'Tersimpan');
    fetchLeads(); // Refresh to get updated computed fields
  } catch (error) {
    showToast('error', 'Gagal simpan');
  }
};

const setInputRef = (el, leadId, field) => {
  if (el) inputRefs.value[`${leadId}-${field}`] = el;
};

// ==========================================
// MODAL PICs
// ==========================================
const openPicsModal = async (lead) => {
  selectedLeadForPics.value = lead;
  
  // Fetch full lead data with PICs
  try {
    const response = await api.get(`leads/${lead.lead_id}/`);
    formPicsEdit.value = JSON.parse(JSON.stringify(response.data.pics || []));
    showPicsModal.value = true;
  } catch (error) {
    showToast('error', 'Gagal memuat data PICs');
  }
};

const addPicRow = () => {
  formPicsEdit.value.push({
    pic_name: '',
    phone_number: '',
    whatsapp: '',
    email: ''
  });
};

const removePicRow = (index) => {
  formPicsEdit.value.splice(index, 1);
};

const savePicsChanges = async () => {
  if (!selectedLeadForPics.value) return;
  
  try {
    await api.put(`leads/${selectedLeadForPics.value.lead_id}/`, {
      ...selectedLeadForPics.value,
      pics: formPicsEdit.value
    });
    showToast('success', 'PICs berhasil diupdate');
    showPicsModal.value = false;
    fetchLeads();
  } catch (error) {
    showToast('error', 'Gagal update PICs');
  }
};

// Show PICs Popup on Double Click
const showPicsDetails = async (event, lead) => {
  if (lead.total_pics <= 1) return; // Only show if more than 1 PIC
  
  try {
    const response = await api.get(`leads/${lead.lead_id}/`);
    picsPopupData.value = response.data.pics || [];
    
    // Position popup near the clicked element
    const rect = event.target.getBoundingClientRect();
    const popupHeight = 400; // Estimated max height
    const popupWidth = 450;
    
    // Check if popup fits below cursor
    const spaceBelow = window.innerHeight - rect.bottom;
    const spaceAbove = rect.top;
    
    let top, left;
    
    // Decide vertical position
    if (spaceBelow >= popupHeight || spaceBelow >= spaceAbove) {
      // Show below
      top = rect.bottom + window.scrollY + 5;
    } else {
      // Show above
      top = rect.top + window.scrollY - popupHeight - 5;
    }
    
    // Decide horizontal position (keep within viewport)
    left = rect.left + window.scrollX;
    if (left + popupWidth > window.innerWidth) {
      left = window.innerWidth - popupWidth - 20;
    }
    if (left < 10) {
      left = 10;
    }
    
    popupPosition.value = { top, left };
    showPicsPopup.value = true;
  } catch (error) {
    showToast('error', 'Gagal memuat detail PICs');
  }
};

const closePicsPopup = () => {
  showPicsPopup.value = false;
  picsPopupData.value = [];
};

// ==========================================
// HELPERS
// ==========================================
const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const getStatusBadgeClass = (status) => {
  const statusMap = {
    'lead_generation': 'bg-blue-100 text-blue-700',
    'follow_up': 'bg-yellow-100 text-yellow-700',
    'quotation': 'bg-purple-100 text-purple-700',
    'deals': 'bg-green-100 text-green-700',
    'onboarding': 'bg-cyan-100 text-cyan-700',
    'retention': 'bg-pink-100 text-pink-700'
  };
  return statusMap[status] || 'bg-gray-100 text-gray-700';
};

const getStatusLabel = (status) => {
  const found = statusKanbanOptions.find(s => s.value === status);
  return found ? found.label : status;
};

onMounted(() => fetchLeads());
</script>

<template>
  <MainLayout>
    <div class="pt-20"></div>
    <div class="flex flex-col h-[calc(100vh-80px)] bg-gray-50 py-4">
      
      <!-- Header & Filters -->
      <div class="mb-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-4">Lead Database</h1>
        
        <div class="bg-white p-4 rounded shadow-sm border border-gray-200 flex flex-wrap justify-between items-center gap-4">
          
          <!-- Search & Filters -->
          <div class="flex items-center gap-3 flex-wrap">
            <!-- Search -->
            <div class="relative">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Search Lead..." 
                class="pl-3 pr-10 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-lime-500 outline-none w-64 h-10"
              >
              <button class="absolute right-0 top-0 h-10 w-10 bg-[#8bc34a] hover:bg-[#7cb342] text-white rounded-r flex items-center justify-center transition">
                <Search :size="18"/>
              </button>
            </div>

            <!-- Filter GP PIC -->
            <select 
              v-model="filterGpPic" 
              class="h-10 border border-gray-300 rounded px-3 text-sm focus:ring-2 focus:ring-lime-500 outline-none bg-white"
            >
              <option value="">All GP PIC</option>
              <option v-for="pic in uniqueGpPicOptions" :key="pic" :value="pic">
                {{ pic }}
              </option>
            </select>

            <!-- Filter Status -->
            <select 
              v-model="filterStatus" 
              class="h-10 border border-gray-300 rounded px-3 text-sm focus:ring-2 focus:ring-lime-500 outline-none bg-white"
            >
              <option value="">All Status</option>
              <option v-for="status in statusKanbanOptions" :key="status.value" :value="status.value">
                {{ status.label }}
              </option>
            </select>

            <!-- Filter Source -->
            <select 
              v-model="filterSource" 
              class="h-10 border border-gray-300 rounded px-3 text-sm focus:ring-2 focus:ring-lime-500 outline-none bg-white"
            >
              <option value="">All Source</option>
              <option v-for="source in uniqueSourceOptions" :key="source" :value="source">
                {{ source }}
              </option>
            </select>
            
            <!-- Reset Button -->
            <button 
              @click="() => { searchQuery=''; filterGpPic=''; filterStatus=''; filterSource=''; }" 
              class="w-16 py-2.5 bg-[#8bc34a] hover:bg-[#7cb342] text-white text-[12px] rounded shadow-sm transition"
            >
              Reset
            </button>
          </div>

          <!-- Pagination Info -->
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <span>1-{{ filteredLeads.length }} of {{ filteredLeads.length }}</span>
            <div class="flex border rounded overflow-hidden">
              <button class="p-2 bg-gray-100 hover:bg-gray-200 border-r">
                <ChevronLeft :size="16"/>
              </button>
              <button class="p-2 bg-gray-100 hover:bg-gray-200">
                <ChevronRight :size="16"/>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white border-t-4 border-t-lime-500 rounded shadow-sm overflow-hidden flex-1 flex flex-col relative">
        <div class="overflow-auto flex-1">
          <table class="w-full text-left text-sm border-collapse">
            <thead class="bg-white text-gray-700 font-bold uppercase text-[10px] leading-normal border-b border-gray-200 sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.05)]">
              <tr>
                <th class="p-4 border-r border-gray-100 min-w-[120px] bg-white text-center">Action</th>
                <th class="p-4 border-r border-gray-100 min-w-[200px]">Property Name</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Source</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Type</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">GP PIC</th>
                <th class="p-4 border-r border-gray-100 min-w-[110px]">Date In</th>
                <th class="p-4 border-r border-gray-100 min-w-[130px]">Status</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">First PIC Name</th>
                <th class="p-4 border-r border-gray-100 min-w-[130px]">Phone</th>
                <th class="p-4 border-r border-gray-100 min-w-[130px]">WhatsApp</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Email</th>
                <th class="p-4 border-r border-gray-100 min-w-[80px] text-center">Total PICs</th>
                <th class="p-4 border-r border-gray-100 min-w-[250px]">Address</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Coordinates</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Referral/Affiliate By</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Commission</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-100">
              <tr 
                v-for="lead in filteredLeads" 
                :key="lead.lead_id" 
                class="group hover:bg-lime-50/10 even:bg-gray-50/50 transition-colors"
              >
                
                <!-- Action Column -->
                <td class="p-3 border-r border-gray-200 text-center align-middle bg-white group-hover:bg-lime-50/10 sticky left-0 z-10">
                  <div class="flex flex-col gap-1.5 items-center">
                    <button 
                      @click="openPicsModal(lead)" 
                      class="w-20 py-1 bg-[#8bc34a] hover:bg-blue-600 text-white text-[10px] rounded shadow-sm transition flex items-center justify-center gap-1"
                    >
                      <Users :size="12"/> PICs
                    </button>
                    <button 
                      @click="deleteLead(lead.lead_id)" 
                      class="w-20 py-1 bg-white-500 hover:bg-gray-600  border border-gray-300 text-black hover:text-white text-[10px] rounded shadow-sm transition flex items-center justify-center gap-1"
                    >
                      <Trash2 :size="12"/> Delete
                    </button>
                  </div>
                </td>

                <!-- Property Name (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'property')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'property')" 
                    type="text" 
                    v-model="lead.property" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'property')" 
                    @blur="saveCell(lead, 'property')" 
                    @keydown.enter="saveCell(lead, 'property')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black font-bold"
                  />
                  <div v-else class="p-4 h-full text-black text-[12px] font-bold">
                    {{ lead.property }}
                  </div>
                </td>

                <!-- Source (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'source')">
                  <div v-if="isEditing(lead.lead_id, 'source')" class="h-full">
                    <select 
                      :ref="(el) => setInputRef(el, lead.lead_id, 'source')" 
                      v-model="lead.source" 
                      @blur="saveCell(lead, 'source')" 
                      @change="saveCell(lead, 'source')" 
                      class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                    >
                      <option value="" disabled>-- Select --</option>
                      <option v-for="src in sourceOptions" :key="src" :value="src">
                        {{ src }}
                      </option>
                    </select>
                  </div>
                  <div v-else class="p-4 h-full text-black text-[12px]">
                    {{ lead.source || '-' }}
                  </div>
                </td>

                <!-- Type (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'type')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'type')" 
                    type="text" 
                    v-model="lead.type" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'type')" 
                    @blur="saveCell(lead, 'type')" 
                    @keydown.enter="saveCell(lead, 'type')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                  />
                  <div v-else class="p-4 h-full text-black text-[12px]">
                    {{ lead.type || '-' }}
                  </div>
                </td>

                <!-- GP PIC (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'gp_pic')">
                  <div v-if="isEditing(lead.lead_id, 'gp_pic')" class="h-full">
                    <select 
                      :ref="(el) => setInputRef(el, lead.lead_id, 'gp_pic')" 
                      v-model="lead.gp_pic" 
                      @blur="saveCell(lead, 'gp_pic')" 
                      @change="saveCell(lead, 'gp_pic')" 
                      class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                    >
                      <option v-for="pic in picList" :key="pic" :value="pic">
                        {{ pic }}
                      </option>
                    </select>
                  </div>
                  <div v-else class="p-4 h-full text-black text-[12px] font-semibold">
                    {{ lead.gp_pic }}
                  </div>
                </td>

                <!-- Date In (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'date_in')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'date_in')" 
                    type="date" 
                    v-model="lead.date_in" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'date_in')" 
                    @blur="saveCell(lead, 'date_in')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                  />
                  <div v-else class="p-4 h-full text-black text-[12px] whitespace-nowrap">
                    {{ formatDate(lead.date_in) }}
                  </div>
                </td>

                <!-- Status Kanban (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'status_kanban')">
                  <div v-if="isEditing(lead.lead_id, 'status_kanban')" class="h-full">
                    <select 
                      :ref="(el) => setInputRef(el, lead.lead_id, 'status_kanban')" 
                      v-model="lead.status_kanban" 
                      @blur="saveCell(lead, 'status_kanban')" 
                      @change="saveCell(lead, 'status_kanban')" 
                      class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                    >
                      <option v-for="status in statusKanbanOptions" :key="status.value" :value="status.value">
                        {{ status.label }}
                      </option>
                    </select>
                  </div>
                  <div v-else class="p-4 h-full flex items-center">
                    <span 
                      class="px-2 py-1 rounded text-[10px] font-bold"
                      :class="getStatusBadgeClass(lead.status_kanban)"
                    >
                      {{ getStatusLabel(lead.status_kanban) }}
                    </span>
                  </div>
                </td>

                <!-- Read-only PIC fields -->
                <td class="p-4 border-r border-gray-100 text-black text-[12px]">
                  {{ lead.first_pic_name }}
                </td>
                <td class="p-4 border-r border-gray-100 text-black text-[12px]">
                  {{ lead.first_pic_phone }}
                </td>
                <td class="p-4 border-r border-gray-100 text-black text-[12px]">
                  {{ lead.first_pic_whatsapp }}
                </td>
                <td class="p-4 border-r border-gray-100 text-black text-[12px]">
                  {{ lead.first_pic_email }}
                </td>
                <td 
                  class="p-4 border-r border-gray-100 text-center cursor-pointer hover:bg-blue-50 transition-colors" 
                  @dblclick="showPicsDetails($event, lead)"
                  :title="lead.total_pics > 1 ? 'Double-click to see all PICs' : ''"
                >
                  <span 
                    class="inline-block px-2 py-1 rounded-full text-[10px] font-bold"
                    :class="lead.total_pics > 1 ? 'bg-blue-100 text-blue-700 cursor-pointer' : 'bg-gray-100 text-gray-600'"
                  >
                    {{ lead.total_pics }}
                  </span>
                </td>

                <!-- Address (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'address')">
                  <textarea 
                    v-if="isEditing(lead.lead_id, 'address')" 
                    v-model="lead.address" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'address')" 
                    @blur="saveCell(lead, 'address')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black min-h-[60px]"
                  ></textarea>
                  <div v-else class="p-4 h-full text-black text-[12px] truncate max-w-[250px]" :title="lead.address">
                    {{ lead.address || '-' }}
                  </div>
                </td>

                <!-- Coordinates (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'coordinates')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'coordinates')" 
                    type="text" 
                    v-model="lead.coordinates" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'coordinates')" 
                    @blur="saveCell(lead, 'coordinates')" 
                    @keydown.enter="saveCell(lead, 'coordinates')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black font-mono"
                  />
                  <div v-else class="p-4 h-full text-black text-[11px] font-mono">
                    {{ lead.coordinates || '-' }}
                  </div>
                </td>

                <!-- Referral/Affiliate By (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'referral_or_affiliate_by')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'referral_or_affiliate_by')" 
                    type="text" 
                    v-model="lead.referral_or_affiliate_by" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'referral_or_affiliate_by')" 
                    @blur="saveCell(lead, 'referral_or_affiliate_by')" 
                    @keydown.enter="saveCell(lead, 'referral_or_affiliate_by')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                  />
                  <div v-else class="p-4 h-full text-black text-[12px]">
                    {{ lead.referral_or_affiliate_by || '-' }}
                  </div>
                </td>

                <!-- Commission Amount (Editable) -->
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(lead.lead_id, 'commission_amount')">
                  <input 
                    v-if="isEditing(lead.lead_id, 'commission_amount')" 
                    type="text" 
                    v-model="lead.commission_amount" 
                    :ref="(el) => setInputRef(el, lead.lead_id, 'commission_amount')" 
                    @blur="saveCell(lead, 'commission_amount')" 
                    @keydown.enter="saveCell(lead, 'commission_amount')" 
                    class="w-full h-full p-3 bg-white border-2 border-lime-500 outline-none text-[12px] text-black"
                  />
                  <div v-else class="p-4 h-full text-black text-[12px]">
                    {{ lead.commission_amount || '-' }}
                  </div>
                </td>

              </tr>
              
              <!-- Empty State -->
              <tr v-if="filteredLeads.length === 0">
                <td colspan="17" class="p-12 text-center text-gray-400 italic bg-gray-50/30">
                  Tidak ada data yang sesuai filter.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Loading Overlay -->
        <div v-if="isLoading" class="absolute inset-0 bg-white/80 flex items-center justify-center z-50">
          <Loader2 class="animate-spin text-lime-600" :size="32"/>
        </div>
      </div>
    </div>

    <!-- PICs Modal -->
    <Teleport to="body">
      <div v-if="showPicsModal" class="fixed inset-0 z-[150] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl relative animate-fade-in-up">
          <div class="bg-blue-600 p-4 border-b rounded-t-xl flex justify-between items-center text-white">
            <h3 class="font-bold text-lg flex items-center gap-2">
              <Users :size="20"/> Manage PICs
            </h3>
            <button @click="showPicsModal = false" class="hover:text-blue-200">
              <X :size="24"/>
            </button>
          </div>
          
          <div class="p-6 max-h-[70vh] overflow-y-auto bg-gray-50">
            <div class="mb-4 text-sm text-gray-600 font-bold">
              Property: {{ selectedLeadForPics?.property }}
            </div>
            
            <div class="space-y-3">
              <div 
                v-for="(pic, index) in formPicsEdit" 
                :key="index" 
                class="bg-white p-4 rounded border shadow-sm relative"
              >
                <button 
                  type="button" 
                  @click="removePicRow(index)" 
                  class="absolute top-2 right-2 text-red-400 hover:text-red-600"
                >
                  <Trash2 :size="16"/>
                </button>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label class="label">PIC Name</label>
                    <input 
                      v-model="pic.pic_name" 
                      type="text" 
                      class="input-sm" 
                      placeholder="Enter name"
                    >
                  </div>
                  <div>
                    <label class="label">Phone Number</label>
                    <input 
                      v-model="pic.phone_number" 
                      type="text" 
                      class="input-sm" 
                      placeholder="Enter phone"
                    >
                  </div>
                  <div>
                    <label class="label">WhatsApp</label>
                    <input 
                      v-model="pic.whatsapp" 
                      type="text" 
                      class="input-sm" 
                      placeholder="Enter WhatsApp"
                    >
                  </div>
                  <div>
                    <label class="label">Email</label>
                    <input 
                      v-model="pic.email" 
                      type="email" 
                      class="input-sm" 
                      placeholder="Enter email"
                    >
                  </div>
                </div>
              </div>
            </div>
            
            <button 
              @click="addPicRow" 
              class="mt-4 w-full py-2 border-2 border-dashed border-blue-200 text-blue-500 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition font-bold text-xs flex justify-center items-center gap-2"
            >
              <Plus :size="14"/> Add PIC
            </button>
          </div>

          <div class="p-4 border-t bg-white rounded-b-xl flex justify-end gap-3">
            <button 
              @click="showPicsModal = false" 
              class="px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm font-bold text-gray-600"
            >
              Batal
            </button>
            <button 
              @click="savePicsChanges" 
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-bold flex items-center gap-2"
            >
              <Save :size="16"/> Simpan Perubahan
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- PICs Details Popup -->
    <Teleport to="body">
      <div v-if="showPicsPopup" class="fixed inset-0 z-[200]" @click="closePicsPopup">
        <div 
          class="absolute bg-white rounded-lg shadow-2xl border-2 border-blue-500 p-4 min-w-[400px] max-w-[500px] animate-fade-in"
          :style="{ top: `${popupPosition.top}px`, left: `${popupPosition.left}px` }"
          @click.stop
        >
          <div class="flex justify-between items-center mb-3 pb-2 border-b">
            <h4 class="font-bold text-sm text-gray-700 flex items-center gap-2">
              <Users :size="16" class="text-blue-600"/> All PICs ({{ picsPopupData.length }})
            </h4>
            <button @click="closePicsPopup" class="text-gray-400 hover:text-gray-600">
              <X :size="18"/>
            </button>
          </div>
          
          <div class="space-y-3 max-h-[400px] overflow-y-auto">
            <div 
              v-for="(pic, index) in picsPopupData" 
              :key="index"
              class="bg-gray-50 p-3 rounded border border-gray-200"
            >
              <div class="font-bold text-xs text-blue-700 mb-2 flex items-center gap-1">
                <span class="bg-blue-100 text-blue-700 rounded-full w-5 h-5 flex items-center justify-center text-[10px]">
                  {{ index + 1 }}
                </span>
                {{ pic.pic_name || 'Unnamed PIC' }}
              </div>
              <div class="grid grid-cols-1 gap-1 text-[11px] text-gray-600">
                <div v-if="pic.phone_number" class="flex items-start gap-1">
                  <span class="font-semibold min-w-[70px]">Phone:</span>
                  <span>{{ pic.phone_number }}</span>
                </div>
                <div v-if="pic.whatsapp" class="flex items-start gap-1">
                  <span class="font-semibold min-w-[70px]">WhatsApp:</span>
                  <span>{{ pic.whatsapp }}</span>
                </div>
                <div v-if="pic.email" class="flex items-start gap-1">
                  <span class="font-semibold min-w-[70px]">Email:</span>
                  <span class="break-all">{{ pic.email }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-3 pt-2 border-t text-center">
            <button 
              @click="closePicsPopup" 
              class="text-xs text-gray-500 hover:text-gray-700 font-semibold"
            >
              Close (or click outside)
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </MainLayout>
</template>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar { height: 8px; width: 8px; }
::-webkit-scrollbar-track { background: #f9fafb; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* Input Reset */
input[type="text"], 
input[type="number"], 
input[type="date"], 
input[type="email"],
select, 
textarea { 
  font-family: inherit; 
  font-size: 0.75rem; 
}

.label { 
  @apply block text-[10px] font-bold text-gray-500 mb-1 uppercase; 
}

.input-sm { 
  @apply w-full border border-gray-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-blue-500 outline-none; 
}

.animate-fade-in-up { 
  animation: fadeInUp 0.2s ease-out; 
}

@keyframes fadeInUp { 
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  } 
  to { 
    opacity: 1; 
    transform: translateY(0); 
  } 
}

.animate-fade-in {
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>