<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api';
import { useNotification } from '../composables/useNotification';
import { 
  Search, Plus, Trash2, DollarSign, Loader2, Save, X, Edit,
  ChevronLeft, ChevronRight, ExternalLink
} from 'lucide-vue-next';

const { showToast } = useNotification();
const deals = ref([]);
const isLoading = ref(false);

// --- DATA CONSTANT ---
const picList = [
  'EKA', 'SURYA', 'ANGGA', 'RUSDIANA', 'WIRA', 'YOGA', 
  'WAHYU', 'WULAN', 'TRISNA', 'SURYANI', 'WIDI', 'NIA', 'system'
];

const ProjectManagerList = [
  'EKA', 'SURYA', 'ANGGA', 'RUSDIANA', 'WIRA', 'YOGA'
];
// --- STATE FILTER ---
const searchQuery = ref('');
const filterStartDate = ref('');
const filterEndDate = ref('');
const filterDealBy = ref('');

// State Edit
const editingCell = ref(null);
const inputRefs = ref({});

// State Modal Product
const showProductModal = ref(false);
const selectedDealForEdit = ref(null);
const formProductEdit = ref([]); 

// ==========================================
// COMPUTED
// ==========================================
const uniqueDealByOptions = computed(() => {
    const pics = deals.value.map(d => d.deal_by).filter(p => p); 
    return [...new Set(pics)]; 
});

const filteredDeals = computed(() => {
    const result = deals.value.filter(deal => {
        const matchSearch =
            !searchQuery.value ||
            (deal.lead_property &&
                deal.lead_property.toLowerCase().includes(searchQuery.value.toLowerCase()));

        const matchDealBy =
            !filterDealBy.value || deal.deal_by === filterDealBy.value;

        let matchDate = true;
        if (filterStartDate.value || filterEndDate.value) {
            const dealDate = new Date(deal.dealDate).setHours(0, 0, 0, 0);
            const start = filterStartDate.value
                ? new Date(filterStartDate.value).setHours(0, 0, 0, 0)
                : null;
            const end = filterEndDate.value
                ? new Date(filterEndDate.value).setHours(0, 0, 0, 0)
                : null;

            if (start && dealDate < start) matchDate = false;
            if (end && dealDate > end) matchDate = false;
        }

        return matchSearch && matchDealBy && matchDate;
    });
    return result.sort(
        (a, b) =>
            new Date(a.date).setHours(0, 0, 0, 0) -
            new Date(b.date).setHours(0, 0, 0, 0)
    );
});


// ==========================================
// ACTIONS
// ==========================================
const fetchDeals = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('deals/');
    deals.value = response.data;
  } catch (error) { showToast('error', 'Gagal memuat data deals'); } 
  finally { isLoading.value = false; }
};

// ==========================================
// SPREADSHEET EDIT
// ==========================================
const editCell = (dealId, field) => {
  editingCell.value = { id: dealId, field: field };
  nextTick(() => { const el = inputRefs.value[`${dealId}-${field}`]; if (el) el.focus(); });
};
const isEditing = (dealId, field) => editingCell.value && editingCell.value.id === dealId && editingCell.value.field === field;
const saveCell = async (deal, field) => {
  editingCell.value = null;
  try { await api.patch(`deals/${deal.deal_id}/`, { [field]: deal[field] }); showToast('success', 'Tersimpan'); } 
  catch (error) { showToast('error', 'Gagal simpan'); }
};
const setInputRef = (el, dealId, field) => { if (el) inputRefs.value[`${dealId}-${field}`] = el; };

// ==========================================
// MODAL PRODUCT
// ==========================================
const openProductModal = (deal) => {
  selectedDealForEdit.value = deal;
  formProductEdit.value = JSON.parse(JSON.stringify(deal.details));
  showProductModal.value = true;
};
const addProductRow = () => { 
  formProductEdit.value.push({ 
    package: '', 
    product_initiation: '', // Field Backend
    product_initiation_amount: 0, // Field Backend
    product_initiation_amount_by: 'Month' // Field Backend
  }); 
};

// 2. Tambah Initiation (One-time)
const addInitiationRow = () => { 
  formProductEdit.value.push({ 
    package: 'Initiation', 
    product_initiation: '', // Field Backend
    product_initiation_amount: 0, // Field Backend
    product_initiation_amount_by: 'One-time Cost' // Field Backend (Ini yang tadi kosong)
  }); 
};
const removeProductRow = (index) => { formProductEdit.value.splice(index, 1); };
const saveProductChanges = async () => {
  if (!selectedDealForEdit.value) return;
  try {
    await api.patch(`deals/${selectedDealForEdit.value.deal_id}/`, { details: formProductEdit.value });
    showToast('success', 'Update Berhasil'); showProductModal.value = false; fetchDeals();
  } catch (error) { showToast('error', 'Gagal update'); }
};

// ==========================================
// HELPERS
// ==========================================
const formatCurrency = (value) => value ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value) : '-';
const formatDate = (dateString) => dateString ? new Date(dateString).toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' }) : '-';
const getProductsOnly = (details) => details.filter(d => d.package !== 'Initiation');
const getInitiationsOnly = (details) => details.filter(d => d.package === 'Initiation');

onMounted(() => fetchDeals());
</script>

<template>
  <MainLayout>
    <div class="pt-24"></div>
    <div class="flex flex-col h-[calc(100vh-80px)] bg-gray-50 p-4">
      
      <div class="mb-6">
         <h1 class="text-2xl font-bold text-gray-800 mb-4">Dealing Property</h1>
         
         <div class="bg-white p-4 rounded shadow-sm border border-gray-200 flex flex-wrap justify-between items-center gap-4">
            
            <div class="flex items-center gap-3">
                <div class="relative">
                    <input v-model="searchQuery" type="text" placeholder="Search..." class="pl-3 pr-10 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-green-500 outline-none w-64 h-10">
                    <button class="absolute right-0 top-0 h-10 w-10 bg-[#8bc34a] hover:bg-[#7cb342] text-white rounded-r flex items-center justify-center transition">
                        <Search :size="18"/>
                    </button>
                </div>

                <select v-model="filterDealBy" class="h-10 border border-gray-300 rounded px-3 text-sm focus:ring-2 focus:ring-green-500 outline-none bg-white">
                    <option value="">All Sales</option>
                    <option v-for="pic in uniqueDealByOptions" :key="pic" :value="pic">{{ pic }}</option>
                </select>
                
                <button @click="() => { searchQuery=''; filterDealBy=''; }" class="w-16 py-2.5 bg-[#8bc34a] hover:bg-[#7cb342] text-white text-[12px] rounded shadow-sm transition">Reset</button>
            </div>

            <div class="flex items-center gap-2 text-sm text-gray-600">
                <span>1-{{ filteredDeals.length }} of {{ filteredDeals.length }}</span>
                <div class="flex border rounded overflow-hidden">
                    <button class="p-2 bg-gray-100 hover:bg-gray-200 border-r"><ChevronLeft :size="16"/></button>
                    <button class="p-2 bg-gray-100 hover:bg-gray-200"><ChevronRight :size="16"/></button>
                </div>
            </div>
         </div>
      </div>

      <div class="bg-white border-t-4 border-[#8bc34a] rounded shadow-sm overflow-hidden flex-1 flex flex-col relative">
        <div class="overflow-auto flex-1">
          <table class="w-full text-left text-sm border-collapse">
            <thead class="bg-white text-gray-700 font-bold uppercase text-[10px] leading-normal border-b border-gray-200 sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.05)]">
              <tr class="">
                <th class="p-4 border-r border-gray-100 min-w-[100px] bg-white text-center">Action</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Deal Type</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Deal by</th>
                <th class="p-4 border-r border-gray-100 min-w-[110px]">Deal Date</th>
                <th class="p-4 border-r border-gray-100 min-w-[200px]">Nama Property</th>
                <th class="p-4 border-r border-gray-100 min-w-[200px]">Management</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Owner/PIC</th>
                <th class="p-4 border-r border-gray-100 min-w-[250px]">Alamat</th>
                <th class="p-4 border-r border-gray-100 min-w-[130px]">Phone</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Email</th>
                <th class="p-4 border-r border-gray-100 min-w-[80px] text-center">Rooms</th>
                <th class="p-4 border-r border-gray-100 min-w-[250px] bg-blue-50/30">Products</th>
                <th class="p-4 border-r border-gray-100 min-w-[200px] bg-green-50/30">Initiation</th>
                <th class="p-4 border-r border-gray-100 min-w-[200px]">Notes</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">NIK/NPWP</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Project Manager</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Link Invoice</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Account Manager</th>
                <th class="p-4 border-r border-gray-100 min-w-[90px] text-center">Inv. Issued</th>
                <th class="p-4 border-r border-gray-100 min-w-[90px] text-center">Sub. Chg</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Paid Date</th>
                <th class="p-4 border-r border-gray-100 min-w-[80px] text-center">Paid</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Bukti Bayar</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">PIC Finance</th>
                <th class="p-4 border-r border-gray-100 min-w-[90px] text-center">Partial</th>
                <th class="p-4 border-r border-gray-100 min-w-[120px]">Next Pay</th>
                <th class="p-4 border-r border-gray-100 min-w-[150px]">Receipt Link</th>
                <th class="p-4 border-r border-gray-100 min-w-[90px] text-center">Inv. Sent</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-100">
              <tr v-for="deal in filteredDeals" :key="deal.deal_id" class="group hover:bg-blue-50/10 even:bg-gray-50/50 transition-colors">
                
                <td class="p-3 border-r border-gray-200 text-center align-middle bg-white group-hover:bg-blue-50/10 sticky left-0 z-10">
                    <div class="flex flex-col gap-1.5 items-center">
                        <button @click="openProductModal(deal)" class="w-16 py-1 bg-[#8bc34a] hover:bg-[#7cb342] text-white text-[10px] rounded shadow-sm transition">
                            Edit
                        </button>
                    </div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'deal_type')">
                  <div v-if="isEditing(deal.deal_id, 'deal_type')" class="h-full">
                    <select :ref="(el) => setInputRef(el, deal.deal_id, 'deal_type')" v-model="deal.deal_type" @blur="saveCell(deal, 'deal_type')" @change="saveCell(deal, 'deal_type')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black">
                      <option>New Deal</option><option>Migration</option><option>Update Package</option><option>Refreshment Training</option><option>Upselling</option><option>Room Update</option>
                    </select>
                  </div>
                  <div v-else class="p-4 h-full flex items-center text-black text-[12px]">{{ deal.deal_type }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'deal_by')">
                  <div v-if="isEditing(deal.deal_id, 'deal_by')" class="h-full">
                    <select :ref="(el) => setInputRef(el, deal.deal_id, 'deal_by')" v-model="deal.deal_by" @blur="saveCell(deal, 'deal_by')" @change="saveCell(deal, 'deal_by')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black">
                        <option value="" disabled>-- Select --</option>
                        <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                        <option v-if="deal.deal_by && !picList.includes(deal.deal_by)" :value="deal.deal_by">{{ deal.deal_by }}</option>
                    </select>
                  </div>
                  <div v-else class="p-4 h-full text-black text-[12px] flex items-center">{{ deal.deal_by || '-' }}</div>
                </td>

                <td class="p-4 border-r border-gray-100 text-black text-[12px] whitespace-nowrap">{{ formatDate(deal.date) }}</td>

                <td class="p-4 border-r border-gray-100 text-black text-[12px]">{{ deal.lead_property }}</td>
                <td class="p-4 border-r border-gray-100 text-black text-[12px]">{{ deal.management }}</td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'pic_lead_name')">
                    <input v-if="isEditing(deal.deal_id, 'pic_lead_name')" type="text" v-model="deal.pic_lead_name" :ref="(el) => setInputRef(el, deal.deal_id, 'pic_lead_name')" @blur="saveCell(deal, 'pic_lead_name')" @keydown.enter="saveCell(deal, 'pic_lead_name')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.pic_lead_name || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'lead_address')">
                    <textarea v-if="isEditing(deal.deal_id, 'lead_address')" v-model="deal.lead_address" :ref="(el) => setInputRef(el, deal.deal_id, 'lead_address')" @blur="saveCell(deal, 'lead_address')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black min-h-[50px]"></textarea>
                    <div v-else class="p-4 h-full truncate max-w-[250px] text-black text-[12px]" :title="deal.lead_address">{{ deal.lead_address || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'pic_lead_contact')">
                    <input v-if="isEditing(deal.deal_id, 'pic_lead_contact')" type="text" v-model="deal.pic_lead_contact" :ref="(el) => setInputRef(el, deal.deal_id, 'pic_lead_contact')" @blur="saveCell(deal, 'pic_lead_contact')" @keydown.enter="saveCell(deal, 'pic_lead_contact')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.pic_lead_contact || '-' }}</div>
                </td>

                 <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'pic_lead_email')">
                    <input v-if="isEditing(deal.deal_id, 'pic_lead_email')" type="text" v-model="deal.pic_lead_email" :ref="(el) => setInputRef(el, deal.deal_id, 'pic_lead_email')" @blur="saveCell(deal, 'pic_lead_email')" @keydown.enter="saveCell(deal, 'pic_lead_email')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.pic_lead_email || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer text-center" @click="editCell(deal.deal_id, 'room')">
                    <input v-if="isEditing(deal.deal_id, 'room')" type="number" v-model="deal.room" :ref="(el) => setInputRef(el, deal.deal_id, 'room')" @blur="saveCell(deal, 'room')" @keydown.enter="saveCell(deal, 'room')" class="w-full h-full p-3 text-center bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full text-black text-[12px]">{{ deal.room }}</div>
                </td>

                <td class="p-3 border-r border-gray-100 bg-blue-50/20 align-top">
                    <ul class="list-none space-y-1">
                        <li v-for="d in getProductsOnly(deal.details)" :key="d.deal_detail_id" class="text-xs">
                            <div class="font-bold text-gray-800">{{ d.product_initiation }}</div>
                            <div class="text-[10px] text-gray-500">{{ formatCurrency(d.product_initiation_amount) }} / {{d.product_initiation_amount_by}}</div>
                        </li>
                    </ul>
                </td>

                <td class="p-3 border-r border-gray-100 bg-green-50/20 align-middle">
                    <ul class="list-none space-y-1">
                        <li v-for="d in getInitiationsOnly(deal.details)" :key="d.deal_detail_id" class="text-xs">
                            <div class="text-[11px] text-black-800">{{ d.product_initiation }}</div>
                            <div class="text-[10px] text-gray-500">{{ formatCurrency(d.product_initiation_amount) }}</div>
                        </li>
                    </ul>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'notes')">
                    <textarea v-if="isEditing(deal.deal_id, 'notes')" v-model="deal.notes" :ref="(el) => setInputRef(el, deal.deal_id, 'notes')" @blur="saveCell(deal, 'notes')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black min-h-[60px]"></textarea>
                    <div v-else class="p-4 h-full text-black text-[12px] truncate max-w-[200px] whitespace-nowrap" :title="deal.notes">{{ deal.notes || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'nik_npwp')">
                    <input v-if="isEditing(deal.deal_id, 'nik_npwp')" type="text" v-model="deal.nik_npwp" :ref="(el) => setInputRef(el, deal.deal_id, 'nik_npwp')" @blur="saveCell(deal, 'nik_npwp')" @keydown.enter="saveCell(deal, 'nik_npwp')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.nik_npwp || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'project_manager')">
                    <div v-if="isEditing(deal.deal_id, 'project_manager')" class="h-full">
                        <select 
                            :ref="(el) => setInputRef(el, deal.deal_id, 'project_manager')" 
                            v-model="deal.project_manager" 
                            @blur="saveCell(deal, 'project_manager')" 
                            @change="saveCell(deal, 'project_manager')" 
                            class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"
                        >
                            <option value="" disabled>-- Pilih PM --</option>
                            <option v-for="pm in ProjectManagerList" :key="pm" :value="pm">{{ pm }}</option>
                        </select>
                    </div>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.project_manager || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'link_invoice')">
                    <input v-if="isEditing(deal.deal_id, 'link_invoice')" type="text" v-model="deal.link_invoice" :ref="(el) => setInputRef(el, deal.deal_id, 'link_invoice')" @blur="saveCell(deal, 'link_invoice')" @keydown.enter="saveCell(deal, 'link_invoice')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full flex items-center gap-1"><ExternalLink v-if="deal.link_invoice" :size="12" class="text-black"/><span class="truncate max-w-[140px] text-black hover:underline text-[12px]">{{ deal.link_invoice || '-' }}</span></div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'account_manager')">
                    <div v-if="isEditing(deal.deal_id, 'account_manager')" class="h-full">
                        <select 
                            :ref="(el) => setInputRef(el, deal.deal_id, 'account_manager')" 
                            v-model="deal.account_manager" 
                            @blur="saveCell(deal, 'account_manager')" 
                            @change="saveCell(deal, 'account_manager')" 
                            class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"
                        >
                            <option value="" disabled>-- Pilih PM --</option>
                            <option v-for="pm in picList" :key="pm" :value="pm">{{ pm }}</option>
                        </select>
                    </div>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.account_manager || '-' }}</div>
                </td>

                <td class="border-r border-gray-100 text-center bg-gray-50/20"><input type="checkbox" v-model="deal.invoice_issued" @change="saveCell(deal, 'invoice_issued')" class="rounded border-gray-300 text-green-600 focus:ring-green-500"></td>
                <td class="border-r border-gray-100 text-center bg-gray-50/20"><input type="checkbox" v-model="deal.subscribe_changed" @change="saveCell(deal, 'subscribe_changed')" class="rounded border-gray-300 text-green-600 focus:ring-green-500"></td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'paid_date')">
                    <input v-if="isEditing(deal.deal_id, 'paid_date')" type="date" v-model="deal.paid_date" :ref="(el) => setInputRef(el, deal.deal_id, 'paid_date')" @blur="saveCell(deal, 'paid_date')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full text-black text-[12px] whitespace-nowrap flex items-center">{{ formatDate(deal.paid_date) }}</div>
                </td>

                <td class="border-r border-gray-100 text-center bg-gray-50/20"><input type="checkbox" v-model="deal.is_paid" @change="saveCell(deal, 'is_paid')" class="rounded border-gray-300 text-green-600 focus:ring-green-500"></td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'link_payment_receipt')">
                    <input v-if="isEditing(deal.deal_id, 'link_payment_receipt')" type="text" v-model="deal.link_payment_receipt" :ref="(el) => setInputRef(el, deal.deal_id, 'link_payment_receipt')" @blur="saveCell(deal, 'link_payment_receipt')" @keydown.enter="saveCell(deal, 'link_payment_receipt')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black hover:underline max-w-[140px] text-[12px]">{{ deal.link_payment_receipt || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'pic_penerima_bukti_bayar')">
                    <input v-if="isEditing(deal.deal_id, 'pic_penerima_bukti_bayar')" type="text" v-model="deal.pic_penerima_bukti_bayar" :ref="(el) => setInputRef(el, deal.deal_id, 'pic_penerima_bukti_bayar')" @blur="saveCell(deal, 'pic_penerima_bukti_bayar')" @keydown.enter="saveCell(deal, 'pic_penerima_bukti_bayar')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black text-[12px]">{{ deal.pic_penerima_bukti_bayar || '-' }}</div>
                </td>

                <td class="border-r border-gray-100 text-center bg-gray-50/20"><input type="checkbox" v-model="deal.is_partial_payment" @change="saveCell(deal, 'is_partial_payment')" class="rounded border-gray-300 text-green-600 focus:ring-green-500"></td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'next_payment_date')">
                    <input v-if="isEditing(deal.deal_id, 'next_payment_date')" type="date" v-model="deal.next_payment_date" :ref="(el) => setInputRef(el, deal.deal_id, 'next_payment_date')" @blur="saveCell(deal, 'next_payment_date')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full text-black text-[12px] whitespace-nowrap flex items-center">{{ formatDate(deal.next_payment_date) }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'link_payment_receipt_2')">
                    <input v-if="isEditing(deal.deal_id, 'link_payment_receipt_2')" type="text" v-model="deal.link_payment_receipt_2" :ref="(el) => setInputRef(el, deal.deal_id, 'link_payment_receipt_2')" @blur="saveCell(deal, 'link_payment_receipt_2')" @keydown.enter="saveCell(deal, 'link_payment_receipt_2')" class="w-full h-full p-3 bg-white border-2 border-green-500 outline-none text-[12px] text-black"/>
                    <div v-else class="p-4 h-full truncate text-black hover:underline max-w-[140px] text-[12px]">{{ deal.link_payment_receipt_2 || '-' }}</div>
                </td>

                <td class="border-r border-gray-100 text-center bg-gray-50/20"><input type="checkbox" v-model="deal.is_invoice_send_to_customer" @change="saveCell(deal, 'is_invoice_send_to_customer')" class="rounded border-gray-300 text-green-600 focus:ring-green-500"></td>

              </tr>
              <tr v-if="filteredDeals.length === 0">
                  <td colspan="25" class="p-12 text-center text-gray-400 italic bg-gray-50/30">Tidak ada data yang sesuai filter.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="isLoading" class="absolute inset-0 bg-white/80 flex items-center justify-center z-50"><Loader2 class="animate-spin text-green-600" :size="32"/></div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showProductModal" class="fixed inset-0 z-[150] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl relative animate-fade-in-up">
          <div class="bg-green-600 p-4 border-b rounded-t-xl flex justify-between items-center text-white">
            <h3 class="font-bold text-lg flex items-center gap-2"><DollarSign :size="20"/> Manage Products & Packages</h3>
            <button @click="showProductModal = false" class="hover:text-green-200"><X :size="24"/></button>
          </div>
          
          <div class="p-6 max-h-[70vh] overflow-y-auto bg-gray-50">
            <div class="mb-4 text-sm text-gray-600 font-bold">Property: {{ selectedDealForEdit?.lead_property }}</div>
            
            <div class="mb-6">
                <div class="flex justify-between items-center mb-2 border-b pb-1"><h4 class="text-xs font-bold text-blue-700 uppercase">Main Products (Recurring)</h4></div>
                <div class="space-y-2">
                    <template v-for="(detail, index) in formProductEdit" :key="index">
                        <div v-if="detail.package !== 'Initiation'" class="bg-white p-3 rounded border shadow-sm relative">
                            <button type="button" @click="removeProductRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                                <div><label class="label">Package Name</label><input v-model="detail.package" type="text" class="input-sm" placeholder="e.g. Pro Plan"></div>
                                <div><label class="label">Product(s)</label><input v-model="detail.product_initiation" type="text" class="input-sm" placeholder="e.g. PMS, CM"></div>
                                <div><label class="label">Amount</label><div class="flex gap-2"><input v-model="detail.product_initiation_amount" type="number" class="input-sm"><select v-model="detail.product_initiation_amount_by" class="input-sm w-24"><option>Month</option><option>Year</option></select></div></div>
                            </div>
                        </div>
                    </template>
                </div>
                <button @click="addProductRow" class="mt-2 w-full py-2 border-2 border-dashed border-blue-200 text-blue-500 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition font-bold text-xs flex justify-center items-center gap-2"><Plus :size="14"/> Add Product</button>
            </div>

            <div>
                <div class="flex justify-between items-center mb-2 border-b pb-1"><h4 class="text-xs font-bold text-green-700 uppercase">Initiation (One-time)</h4></div>
                <div class="space-y-2">
                    <template v-for="(detail, index) in formProductEdit" :key="index">
                        <div v-if="detail.package === 'Initiation'" class="bg-white p-3 rounded border shadow-sm relative">
                            <button type="button" @click="removeProductRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div><label class="label">Service Name</label><input v-model="detail.product_initiation" type="text" class="input-sm" placeholder="e.g. Visit Training"></div>
                                <div><label class="label">Amount</label><div class="relative"><input v-model="detail.product_initiation_amount" type="number" class="input-sm pr-24"><span class="absolute right-2 top-1.5 text-[10px] text-gray-400 font-bold bg-gray-100 px-1 rounded">One-time Cost</span></div></div>
                            </div>
                        </div>
                    </template>
                </div>
                <button @click="addInitiationRow" class="mt-2 w-full py-2 border-2 border-dashed border-green-200 text-green-500 rounded-lg hover:border-green-500 hover:bg-green-50 transition font-bold text-xs flex justify-center items-center gap-2"><Plus :size="14"/> Add Initiation</button>
            </div>
          </div>

          <div class="p-4 border-t bg-white rounded-b-xl flex justify-end gap-3">
            <button @click="showProductModal = false" class="px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm font-bold text-gray-600">Batal</button>
            <button @click="saveProductChanges" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-bold flex items-center gap-2"><Save :size="16"/> Simpan Perubahan</button>
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
input[type="text"], input[type="number"], input[type="date"], select, textarea { font-family: inherit; font-size: 0.75rem; }
.label { @apply block text-[10px] font-bold text-gray-500 mb-1 uppercase; }
.input-sm { @apply w-full border border-gray-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-green-500 outline-none; }
.animate-fade-in-up { animation: fadeInUp 0.2s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>