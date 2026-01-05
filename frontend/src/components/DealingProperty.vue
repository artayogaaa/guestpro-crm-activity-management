<script setup>
import { ref, onMounted, nextTick } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api';
import { useNotification } from '../composables/useNotification';
import { 
  Briefcase, Search, ExternalLink, Plus, Trash2,
  FileText, Calendar as CalendarIcon, DollarSign, Loader2, Save, X, Edit
} from 'lucide-vue-next';

const { showToast } = useNotification();
const deals = ref([]);
const isLoading = ref(false);
const searchQuery = ref('');

// State untuk Edit Spreadsheet
const editingCell = ref(null);
const inputRefs = ref({});

// State untuk Modal Edit Produk
const showProductModal = ref(false);
const selectedDealForEdit = ref(null);
const formProductEdit = ref([]); // Array detail sementara

// ==========================================
// API & DATA
// ==========================================
const fetchDeals = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('deals/');
    deals.value = response.data;
  } catch (error) {
    showToast('error', 'Gagal memuat data deals');
  } finally {
    isLoading.value = false;
  }
};

// ==========================================
// LOGIC SPREADSHEET EDIT (GENERAL)
// ==========================================
const editCell = (dealId, field) => {
  editingCell.value = { id: dealId, field: field };
  nextTick(() => {
    const el = inputRefs.value[`${dealId}-${field}`];
    if (el) el.focus();
  });
};

const isEditing = (dealId, field) => {
  return editingCell.value && editingCell.value.id === dealId && editingCell.value.field === field;
};

const saveCell = async (deal, field) => {
  editingCell.value = null;
  try {
    const payload = { [field]: deal[field] };
    await api.patch(`deals/${deal.deal_id}/`, payload);
    showToast('success', 'Data tersimpan');
  } catch (error) {
    showToast('error', 'Gagal menyimpan');
    fetchDeals(); // Revert
  }
};

const setInputRef = (el, dealId, field) => {
  if (el) inputRefs.value[`${dealId}-${field}`] = el;
};

// ==========================================
// LOGIC EDIT PRODUCT (MODAL)
// ==========================================
const openProductModal = (deal) => {
  selectedDealForEdit.value = deal;
  // Deep copy details agar tidak reaktif langsung ke tabel sebelum save
  formProductEdit.value = JSON.parse(JSON.stringify(deal.details));
  showProductModal.value = true;
};

const addProductRow = () => {
  formProductEdit.value.push({ package: '', product: '', product_amount: 0, product_amount_by: 'Month', initiation: '', initiation_amount: 0 });
};

const removeProductRow = (index) => {
  formProductEdit.value.splice(index, 1);
};

const saveProductChanges = async () => {
  if (!selectedDealForEdit.value) return;
  try {
    // Kirim full payload details
    await api.patch(`deals/${selectedDealForEdit.value.deal_id}/`, {
        details: formProductEdit.value
    });
    showToast('success', 'Produk & Paket diperbarui');
    showProductModal.value = false;
    fetchDeals();
  } catch (error) {
    showToast('error', 'Gagal update produk');
  }
};

// ==========================================
// FORMATTERS
// ==========================================
const formatCurrency = (value) => {
  if (!value) return '-';
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(value);
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('id-ID', options);
};

onMounted(() => {
  fetchDeals();
});
</script>

<template>
  <MainLayout>
    <div class="flex flex-col h-[calc(100vh-100px)]">
      
      <div class="mb-6 flex justify-between items-end">
        <div>
          <h1 class="text-2xl font-bold text-gray-800 tracking-tight flex items-center gap-2">
            Dealing Property
          </h1>
          <p class="text-sm text-gray-500 mt-1">Kelola data closing dan finance.</p>
        </div>
        <div class="relative">
          <Search :size="16" class="absolute left-3 top-2.5 text-gray-400"/>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari Property..." 
            class="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none w-64 transition"
          >
        </div>
      </div>

      <div class="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex flex-col relative">
        <div class="overflow-auto flex-1">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-gray-50 text-gray-600 font-semibold uppercase sticky top-0 z-20 shadow-sm border-b">
              <tr>
                <th class="p-3 border-r border-gray-200 min-w-[200px] bg-gray-50 sticky left-0 z-30">Property Name</th>
                
                <th class="p-3 border-r border-gray-200 min-w-[120px]">Deal Type</th>
                <th class="p-3 border-r border-gray-200 min-w-[150px]">Project Manager</th>
                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Rooms</th>
                <th class="p-3 border-r border-gray-200 min-w-[200px]">Notes</th>

                <th class="p-3 border-r border-gray-200 min-w-[350px] bg-blue-50/50">Products & Packages (Total Value)</th>

                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Inv. Issued</th>
                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Subs. Chg</th>
                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Is Paid</th>
                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Partial</th>
                <th class="p-3 border-r border-gray-200 min-w-[80px] text-center">Inv. Sent</th>

                <th class="p-3 border-r border-gray-200 min-w-[120px]">NIK / NPWP</th>
                <th class="p-3 border-r border-gray-200 min-w-[120px]">Link Invoice</th>
                <th class="p-3 border-r border-gray-200 min-w-[130px]">Paid Date</th>
                <th class="p-3 border-r border-gray-200 min-w-[120px]">Link Bukti Bayar</th>
                <th class="p-3 border-r border-gray-200 min-w-[120px]">PIC Finance</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-100">
              <tr v-for="deal in deals" :key="deal.deal_id" class="group hover:bg-gray-50 transition-colors">
                
                <td class="p-3 border-r border-gray-200 font-bold text-gray-800 sticky left-0 bg-white group-hover:bg-gray-50 z-10">
                  {{ deal.lead_property }}
                  <div class="text-[10px] text-gray-400 font-normal mt-0.5">{{ deal.pic_lead_name || 'No PIC' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'deal_type')">
                  <div v-if="isEditing(deal.deal_id, 'deal_type')" class="h-full">
                    <select :ref="(el) => setInputRef(el, deal.deal_id, 'deal_type')" v-model="deal.deal_type" @blur="saveCell(deal, 'deal_type')" @change="saveCell(deal, 'deal_type')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs">
                      <option>New Deal</option><option>Migration</option><option>Update Package</option><option>Refreshment Training</option><option>Upselling</option><option>Room Update</option>
                    </select>
                  </div>
                  <div v-else class="p-3 h-full flex items-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-600 border border-gray-200">{{ deal.deal_type }}</span></div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'project_manager')">
                  <input v-if="isEditing(deal.deal_id, 'project_manager')" type="text" v-model="deal.project_manager" :ref="(el) => setInputRef(el, deal.deal_id, 'project_manager')" @blur="saveCell(deal, 'project_manager')" @keydown.enter="saveCell(deal, 'project_manager')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                  <div v-else class="p-3 h-full text-gray-700 truncate min-h-[40px] flex items-center">{{ deal.project_manager || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer text-center" @click="editCell(deal.deal_id, 'room')">
                  <input v-if="isEditing(deal.deal_id, 'room')" type="number" v-model="deal.room" :ref="(el) => setInputRef(el, deal.deal_id, 'room')" @blur="saveCell(deal, 'room')" @keydown.enter="saveCell(deal, 'room')" class="w-full h-full p-2 text-center bg-white border border-green-500 outline-none text-xs"/>
                  <div v-else class="p-3 h-full font-mono font-bold">{{ deal.room }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'notes')">
                  <input v-if="isEditing(deal.deal_id, 'notes')" type="text" v-model="deal.notes" :ref="(el) => setInputRef(el, deal.deal_id, 'notes')" @blur="saveCell(deal, 'notes')" @keydown.enter="saveCell(deal, 'notes')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                  <div v-else class="p-3 h-full text-gray-500 italic truncate max-w-[200px]" :title="deal.notes">{{ deal.notes || '-' }}</div>
                </td>

                <td class="p-0 border-r border-gray-100 bg-blue-50/10 cursor-pointer hover:bg-blue-50 transition relative group/edit" @click="openProductModal(deal)">
                  <div class="absolute top-1 right-1 opacity-0 group-hover/edit:opacity-100">
                     <Edit :size="14" class="text-blue-400"/>
                  </div>
                  <div class="p-2 space-y-2">
                    <div v-for="detail in deal.details" :key="detail.deal_detail_id" class="flex justify-between items-start border-b border-gray-100 pb-1 last:border-0 last:pb-0">
                       <div>
                          <div class="font-bold text-gray-800">{{ detail.package }}</div>
                          <div class="text-[10px] text-gray-500">{{ detail.product }}</div>
                       </div>
                       <div class="text-right font-mono">
                          <div class="font-bold text-gray-700">{{ formatCurrency(detail.product_amount) }} <span class="text-[9px] text-gray-400 font-sans">/ {{ detail.product_amount_by }}</span></div>
                          <div v-if="detail.initiation_amount > 0" class="text-[10px] text-gray-400">+ Init: {{ formatCurrency(detail.initiation_amount) }}</div>
                       </div>
                    </div>
                    <div v-if="deal.details.length === 0" class="text-gray-400 italic text-center p-2">Klik untuk tambah produk</div>
                  </div>
                </td>

                <td class="border-r border-gray-100 text-center bg-gray-50/30"><input type="checkbox" v-model="deal.invoice_issued" @change="saveCell(deal, 'invoice_issued')" class="rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer"></td>
                <td class="border-r border-gray-100 text-center bg-gray-50/30"><input type="checkbox" v-model="deal.subscribe_changed" @change="saveCell(deal, 'subscribe_changed')" class="rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer"></td>
                <td class="border-r border-gray-100 text-center bg-gray-50/30"><input type="checkbox" v-model="deal.is_paid" @change="saveCell(deal, 'is_paid')" class="rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer"></td>
                <td class="border-r border-gray-100 text-center bg-gray-50/30"><input type="checkbox" v-model="deal.is_partial_payment" @change="saveCell(deal, 'is_partial_payment')" class="rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer"></td>
                <td class="border-r border-gray-100 text-center bg-gray-50/30"><input type="checkbox" v-model="deal.is_invoice_send_to_customer" @change="saveCell(deal, 'is_invoice_send_to_customer')" class="rounded border-gray-300 text-green-600 focus:ring-green-500 cursor-pointer"></td>

                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'nik_npwp')">
                   <input v-if="isEditing(deal.deal_id, 'nik_npwp')" type="text" v-model="deal.nik_npwp" :ref="(el) => setInputRef(el, deal.deal_id, 'nik_npwp')" @blur="saveCell(deal, 'nik_npwp')" @keydown.enter="saveCell(deal, 'nik_npwp')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                   <div v-else class="p-3 h-full truncate text-blue-600 hover:underline max-w-[120px]">{{ deal.nik_npwp || '-' }}</div>
                </td>
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'link_invoice')">
                   <input v-if="isEditing(deal.deal_id, 'link_invoice')" type="text" v-model="deal.link_invoice" :ref="(el) => setInputRef(el, deal.deal_id, 'link_invoice')" @blur="saveCell(deal, 'link_invoice')" @keydown.enter="saveCell(deal, 'link_invoice')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                   <div v-else class="p-3 h-full flex items-center gap-1"><ExternalLink v-if="deal.link_invoice" :size="12" class="text-blue-500"/><span class="truncate max-w-[120px]">{{ deal.link_invoice || '-' }}</span></div>
                </td>
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'paid_date')">
                   <input v-if="isEditing(deal.deal_id, 'paid_date')" type="date" v-model="deal.paid_date" :ref="(el) => setInputRef(el, deal.deal_id, 'paid_date')" @blur="saveCell(deal, 'paid_date')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                   <div v-else class="p-3 h-full text-gray-700 whitespace-nowrap flex items-center">{{ formatDate(deal.paid_date) }}</div>
                </td>
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'link_payment_receipt')">
                   <input v-if="isEditing(deal.deal_id, 'link_payment_receipt')" type="text" v-model="deal.link_payment_receipt" :ref="(el) => setInputRef(el, deal.deal_id, 'link_payment_receipt')" @blur="saveCell(deal, 'link_payment_receipt')" @keydown.enter="saveCell(deal, 'link_payment_receipt')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                   <div v-else class="p-3 h-full truncate text-blue-600 hover:underline max-w-[120px]">{{ deal.link_payment_receipt || '-' }}</div>
                </td>
                <td class="p-0 border-r border-gray-100 cursor-pointer" @click="editCell(deal.deal_id, 'pic_penerima_bukti_bayar')">
                   <input v-if="isEditing(deal.deal_id, 'pic_penerima_bukti_bayar')" type="text" v-model="deal.pic_penerima_bukti_bayar" :ref="(el) => setInputRef(el, deal.deal_id, 'pic_penerima_bukti_bayar')" @blur="saveCell(deal, 'pic_penerima_bukti_bayar')" @keydown.enter="saveCell(deal, 'pic_penerima_bukti_bayar')" class="w-full h-full p-2 bg-white border border-green-500 outline-none text-xs"/>
                   <div v-else class="p-3 h-full text-gray-700 truncate">{{ deal.pic_penerima_bukti_bayar || '-' }}</div>
                </td>

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
            
            <div class="space-y-3">
              <div v-for="(detail, index) in formProductEdit" :key="index" class="bg-white p-3 rounded border shadow-sm relative">
                <button type="button" @click="removeProductRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">
                  <div><label class="label">Package Name</label><input v-model="detail.package" type="text" class="input-sm" placeholder="e.g. Pro Plan"></div>
                  <div><label class="label">Product(s)</label><input v-model="detail.product" type="text" class="input-sm" placeholder="e.g. PMS, CM"></div>
                  <div>
                    <label class="label">Product Amount</label>
                    <div class="flex gap-2">
                      <input v-model="detail.product_amount" type="number" class="input-sm">
                      <select v-model="detail.product_amount_by" class="input-sm w-20"><option>Month</option><option>Year</option><option>One-time</option></select>
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div><label class="label">Initiation (Training)</label><input v-model="detail.initiation" type="text" class="input-sm" placeholder="e.g. Onsite"></div>
                  <div><label class="label">Initiation Amount</label><input v-model="detail.initiation_amount" type="number" class="input-sm"></div>
                </div>
              </div>
            </div>

            <button @click="addProductRow" class="mt-4 w-full py-2 border-2 border-dashed border-gray-300 text-gray-500 rounded-lg hover:border-green-500 hover:text-green-600 transition font-bold text-xs flex justify-center items-center gap-2">
               <Plus :size="14"/> Add Another Product
            </button>
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
/* Scrollbar Minimalis */
::-webkit-scrollbar { height: 8px; width: 8px; }
::-webkit-scrollbar-track { background: #f9fafb; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* Input Reset */
input[type="text"], input[type="number"], input[type="date"], select { font-family: inherit; font-size: 0.75rem; }
.label { @apply block text-[10px] font-bold text-gray-500 mb-1 uppercase; }
.input-sm { @apply w-full border border-gray-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-green-500 outline-none; }
.animate-fade-in-up { animation: fadeInUp 0.2s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>