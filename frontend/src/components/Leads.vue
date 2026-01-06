<script setup>
import { ref, computed, onMounted } from 'vue';
import MainLayout from '../layouts/MainLayout.vue';
import api from '../api'; 
import { useNotification } from '../composables/useNotification';
import draggable from 'vuedraggable'; 
import { 
  Plus, MapPin, User, Calendar, X, Save, Edit, Trash2, 
  Clock, Calendar as CalendarIcon, Link as LinkIcon, CheckSquare, Square, ChevronDown,
  Briefcase, DollarSign, Package
} from 'lucide-vue-next';
import { watch, nextTick } from 'vue'
import L from 'leaflet'

const { showToast } = useNotification();

// =======================================================================
// DATA CONSTANTS
// =======================================================================
const picList = [
  'EKA', 'SURYA', 'ANGGA', 'RUSDIANA', 'WIRA', 'YOGA', 
  'WAHYU', 'WULAN', 'TRISNA', 'SURYANI', 'WIDI', 'NIA'
];

const inboundSources = [
    'Website', 'Referral', 'Reff', 'Reff No Commission', 
    'Social Media', 'Affiliate'
];

const dealTypes = [
  'New Deal', 'Migration', 'Update Package', 
  'Refreshment Training', 'Upselling', 'Room Update'
];

// =======================================================================
// STATE DATA
// =======================================================================
const allLeads = ref([]);

// KANBAN COLUMNS
const leadsFollowUp = ref([]);
const leadsQuotation = ref([]);
const leadsDeals = ref([]);
const leadsOnboarding = ref([]);
const leadsRetention = ref([]);
const leadsGenInbound = ref([]);
const leadsGenOutbound = ref([]);

// =======================================================================
// MODAL STATES
// =======================================================================

const showFollowUpModal = ref(false);
const draggedItem = ref(null); 
const activeDragTab = ref('followup'); 
const modalMode = ref('drag'); 

const showEditModal = ref(false);
const isEditing = ref(false); 
const addressInput = ref(null);

const showDetailModal = ref(false);
const selectedLead = ref(null);

const showActivityModal = ref(false);
const activityTab = ref('followup'); 
const selectedActivityLead = ref(null);
const activityList = ref([]);
const showPicList = ref(false);

const showInputModal = ref(false);
const isEditingActivity = ref(false);

const showQuotationModal = ref(false);

const showDealModal = ref(false);

// =======================================================================
// HELPER & COMPUTED
// =======================================================================
const autoFixUrl = (targetModel, key) => {
  let url = targetModel[key];
  if (url && !url.match(/^https?:\/\//)) {
    targetModel[key] = 'https://' + url;
  }
};

const isReferralOrAffiliate = computed(() => {
    const s = formLead.value.source;
    return ['Referral', 'Reff', 'Reff No Commission', 'Affiliate'].includes(s);
});

const referralLabel = computed(() => {
    if (formLead.value.source === 'Affiliate') return 'Affiliate By';
    return 'Referral By'; 
});

// =======================================================================
// FORMS
// =======================================================================

const formLead = ref({
  lead_id: null, 
  property: '', 
  source: '', 
  type: '', 
  coordinates: '', 
  address: '', 
  gp_pic: '', 
  date_in: '',
  pics: [] 
});

const formActivity = ref({
  id: null, lead: null, 
  pic_gp: '', pic_lead: '', date: '', start_time: '', end_time: '', 
  objective: 'Sales & Leads', 
  stage: 'Follow Up',
  fu_type: 'Phone Calls/Telephone', notes: '',
  meeting_type: 'Visit Meeting', location: '', latitude: '', longitude: '', mom: '',
  link_quotation: '', is_send: false
});

const formQuotationInitial = ref({
  lead: null, pic_gp: '', date: '', link_quotation: '', is_send: false
});

const formDeal = ref({
  lead: null,
  deal_type: 'New Deal',
  room: 0,
  pic_lead: null, 
  notes: '',
  details: [] 
});

// =======================================================================
// API & LOGIC: LEADS MANAGEMENT
// =======================================================================

const fetchLeads = async () => {
  try {
    const response = await api.get('leads/');
    allLeads.value = response.data;
    distributeLeadsToColumns();
  } catch (error) { showToast('error', 'Gagal memuat data leads'); }
};

const distributeLeadsToColumns = () => {
  leadsGenInbound.value = []; leadsGenOutbound.value = []; leadsFollowUp.value = [];
  leadsQuotation.value = []; leadsDeals.value = []; leadsOnboarding.value = []; leadsRetention.value = [];

  allLeads.value.forEach(lead => {
    switch (lead.status_kanban) {
      case 'lead_generation':
        if (inboundSources.includes(lead.source)) leadsGenInbound.value.push(lead);
        else leadsGenOutbound.value.push(lead);
        break;
      case 'follow_up': leadsFollowUp.value.push(lead); break;
      case 'quotation': leadsQuotation.value.push(lead); break;
      case 'deals': leadsDeals.value.push(lead); break;
      case 'onboarding': leadsOnboarding.value.push(lead); break;
      case 'retention': leadsRetention.value.push(lead); break;
    }
  });
};

const deleteLead = async (pk) => {
  if (!confirm("Hapus data Lead ini permanen?")) return;
  try { 
    await api.delete(`leads/${pk}/`); 
    fetchLeads(); 
    showToast('success', 'Lead berhasil dihapus');
  } catch (error) { showToast('error', 'Gagal hapus'); }
};

// =======================================================================
// API & LOGIC: ADD/EDIT LEAD
// =======================================================================

const openModal = (item = null) => {
  if (item) { 
    isEditing.value = true; 
    formLead.value = JSON.parse(JSON.stringify(item)); 
    if (!formLead.value.pics) formLead.value.pics = [];
  } else { 
    isEditing.value = false; 
    formLead.value = { 
      property: '', source: '', type: '', 
      coordinates: '', address: '', gp_pic: '', 
      date_in: new Date().toISOString().split('T')[0],
      referral_or_affiliate_by: '', commission_amount: '',
      pics: [{ pic_name: '', phone_number: '', whatsapp: '', email: '' }] 
    }; 
  }
  showEditModal.value = true;
};

const closeModal = () => showEditModal.value = false;

const handleGenericSubmit = async () => {
  if (!isReferralOrAffiliate.value) {
      formLead.value.referral_or_affiliate_by = '';
      formLead.value.commission_amount = '';
  }

  if (isEditing.value) {
    try {
      await api.put(`leads/${formLead.value.lead_id}/`, formLead.value);
      closeModal(); fetchLeads(); showToast('success', 'Data diperbarui');
    } catch (error) { showToast('error', 'Gagal update'); }
  } else {
    try {
      await api.post('leads/', formLead.value);
      closeModal(); fetchLeads(); showToast('success', 'Lead baru tersimpan');
    } catch (error) { showToast('error', 'Gagal simpan'); }
  }
};

const addPicRowEdit = () => formLead.value.pics.push({ pic_name: '', phone_number: '', whatsapp: '', email: '' });
const removePicRowEdit = (i) => formLead.value.pics.splice(i, 1);

const openDetailModal = (lead) => { selectedLead.value = lead; showDetailModal.value = true; };
const closeDetailModal = () => showDetailModal.value = false;

// =======================================================================
// API & LOGIC: DRAG DROP & TASK
// =======================================================================

const onChangeFollowUp = (evt) => {
  if (evt.added) {
    draggedItem.value = evt.added.element;
    modalMode.value = 'drag'; 
    showFollowUpModal.value = true;
    activeDragTab.value = 'followup';
    resetFormActivity(draggedItem.value); 
    formActivity.value.stage = 'Follow Up';
  }
};

const onChangeQuotation = (evt) => {
  if (evt.added) {
    draggedItem.value = evt.added.element;
    showQuotationModal.value = true;
    formQuotationInitial.value = {
      lead: draggedItem.value.lead_id,
      pic_gp: draggedItem.value.gp_pic,
      date: new Date().toISOString().split('T')[0],
      link_quotation: '', is_send: false
    };
  }
};

const onChangeDeals = (evt) => {
  if (evt.added) {
    draggedItem.value = evt.added.element;
    showDealModal.value = true;
    formDeal.value = {
      lead: draggedItem.value.lead_id,
      deal_type: 'New Deal',
      room: 0,
      pic_lead: null,
      notes: '',
      details: [{ package: '', product: '', product_amount: 0, product_amount_by: 'Month', initiation: '', initiation_amount: 0 }]
    };
  }
};

const addDealDetailRow = () => formDeal.value.details.push({ package: '', product: '', product_amount: 0, product_amount_by: 'Month', initiation: '', initiation_amount: 0 });
const removeDealDetailRow = (i) => formDeal.value.details.splice(i, 1);

const saveDeal = async () => {
  try {
    const pk = draggedItem.value.lead_id;
    await api.patch(`leads/${pk}/`, { status_kanban: 'deals' });
    await api.post('deals/', formDeal.value);
    showToast('success', 'Deal berhasil dibuat!');
    showDealModal.value = false;
    fetchLeads();
  } catch (error) { showToast('error', 'Gagal simpan deal'); }
};

const cancelMoveDeal = () => { showDealModal.value = false; fetchLeads(); showToast('warning', 'Dibatalkan'); };

const openAddNewTaskModal = (lead, defaultTab = 'followup', stageName = 'Follow Up') => {
  draggedItem.value = lead; 
  modalMode.value = 'manual'; 
  showFollowUpModal.value = true;
  activeDragTab.value = defaultTab;
  resetFormActivity(lead);
  formActivity.value.stage = stageName;
};

const openManualQuotation = (lead) => { draggedItem.value = lead; openAddNewTaskModal(lead, 'quotation', 'Quotation'); };
const cancelMove = () => { showFollowUpModal.value = false; fetchLeads(); showToast('warning', 'Dibatalkan'); };
const cancelMoveQuotation = () => { showQuotationModal.value = false; fetchLeads(); showToast('warning', 'Dibatalkan'); };

const saveDragForm = async () => {
  if (activeDragTab.value === 'quotation' && !formActivity.value.link_quotation) { showToast('warning', 'Link Quotation wajib diisi!'); return; }
  try {
    const pk = draggedItem.value.lead_id;
    if (modalMode.value === 'drag') await api.patch(`leads/${pk}/`, { status_kanban: 'follow_up' });
    if (activeDragTab.value === 'quotation') await api.post('quotations/', { ...formActivity.value, lead: pk });
    else await api.post(activeDragTab.value === 'followup' ? 'followups/' : 'meetings/', { ...formActivity.value, lead: pk });
    showToast('success', 'Berhasil disimpan'); showFollowUpModal.value = false; fetchLeads();
  } catch (error) { showToast('error', 'Gagal proses'); }
};

const saveQuotationInitial = async () => {
  if (!formQuotationInitial.value.link_quotation) { showToast('warning', 'Link Quotation wajib diisi!'); return; }
  try {
    const pk = draggedItem.value.lead_id;
    await api.patch(`leads/${pk}/`, { status_kanban: 'quotation' });
    await api.post('quotations/', { ...formQuotationInitial.value, lead: pk });
    showToast('success', 'Quotation dibuat'); showQuotationModal.value = false; fetchLeads();
  } catch (error) { showToast('error', 'Gagal simpan'); }
};

const updateStatus = async (evt, newStatus) => {
  if (evt.added) { const item = evt.added.element; try { await api.patch(`leads/${item.lead_id}/`, { status_kanban: newStatus }); } catch (error) { showToast('error', 'Gagal update status'); } }
};

// GOOGLE MAP USE

const mapContainer = ref(null)
const mapSearchQuery = ref('')
let map = null
let marker = null

const initLeafletMap = async () => {
  await nextTick()
  
  if (!mapContainer.value) {
    console.error('❌ Map container belum siap')
    return
  }

  // Hapus map lama jika ada
  if (map) {
    map.remove()
  }

  // ✅ Parse koordinat dari formLead jika ada (saat edit)
  let initLat = -8.568317900635176
  let initLng = 115.29492229863575
  
  if (formLead.value.coordinates) {
    const coords = formLead.value.coordinates.split(',')
    if (coords.length === 2) {
      initLat = parseFloat(coords[0].trim())
      initLng = parseFloat(coords[1].trim())
    }
  }

  console.log('✅ Inisialisasi Leaflet Map...')

  // Inisialisasi peta
  map = L.map(mapContainer.value).setView([initLat, initLng], 14)

  // Tambahkan tile layer OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map)

  // Tambahkan marker yang bisa di-drag
  marker = L.marker([initLat, initLng], {
    draggable: true
  }).addTo(map)

  // ✅ Event saat marker di-drag
  marker.on('dragend', async () => {
    const pos = marker.getLatLng()
    const lat = pos.lat.toFixed(6)
    const lng = pos.lng.toFixed(6)
    
    // Simpan dalam format "lat,lng"
    formLead.value.coordinates = `${lat},${lng}`
    
    await reverseGeocode(pos.lat, pos.lng)
  })

  // ✅ Event klik map untuk pindahkan marker
  map.on('click', (e) => {
    marker.setLatLng(e.latlng)
    const lat = e.latlng.lat.toFixed(6)
    const lng = e.latlng.lng.toFixed(6)
    
    // Simpan dalam format "lat,lng"
    formLead.value.coordinates = `${lat},${lng}`
    
    reverseGeocode(e.latlng.lat, e.latlng.lng)
  })

  // Paksa resize map
  setTimeout(() => {
    map.invalidateSize()
    console.log('✅ Map ready!')
  }, 300)
}

// ✅ Search lokasi
const searchLocation = async () => {
  const query = mapSearchQuery.value.trim()
  
  console.log('🔍 Mencari:', query)
  
  if (!query) {
    showToast('warning', 'Masukkan lokasi yang ingin dicari')
    return
  }

  if (!map || !marker) {
    showToast('error', 'Map belum siap')
    return
  }

  try {
    showToast('info', 'Mencari lokasi...')
    
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1&addressdetails=1`
    )
    
    const results = await response.json()
    console.log('📦 Hasil pencarian:', results)

    if (results.length > 0) {
      const place = results[0]
      const lat = parseFloat(place.lat).toFixed(6)
      const lon = parseFloat(place.lon).toFixed(6)

      console.log('📍 Pindah ke:', lat, lon)

      // Update map dan marker
      map.setView([lat, lon], 16)
      marker.setLatLng([lat, lon])

      // ✅ Simpan dalam format "lat,lng"
      formLead.value.coordinates = `${lat},${lon}`
      formLead.value.address = place.display_name

      showToast('success', '✅ Lokasi ditemukan!')
      mapSearchQuery.value = ''
    } else {
      showToast('warning', '⚠️ Lokasi tidak ditemukan')
    }
  } catch (error) {
    console.error('❌ Error:', error)
    showToast('error', 'Gagal mencari lokasi')
  }
}

// ✅ Reverse geocode
const reverseGeocode = async (lat, lng) => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
    )
    const result = await response.json()

    if (result && result.display_name) {
      formLead.value.address = result.display_name
    }
  } catch (error) {
    console.error('❌ Reverse geocode error:', error)
  }
}

// Watch modal
watch(showEditModal, async (val) => {
  if (val) {
    await nextTick()
    setTimeout(() => {
      initLeafletMap()
    }, 100)
  } else {
    if (map) {
      map.remove()
      map = null
      marker = null
    }
  }
})

// =======================================================================
// ACTIVITY LOG
// =======================================================================
const fetchActivitiesByLead = async (leadId, type) => {
  try {
    let endpoint = 'followups/'; if (type === 'meeting') endpoint = 'meetings/'; if (type === 'quotation') endpoint = 'quotations/';
    const response = await api.get(endpoint);
    activityList.value = response.data.filter(item => item.lead === leadId).map(item => { if (type === 'quotation') return { ...item, id: item.quotation_id }; return item; });
  } catch (error) { showToast('error', 'Gagal memuat riwayat'); }
};
const openActivityModal = async (lead, defaultTab = 'followup') => { selectedActivityLead.value = lead; showActivityModal.value = true; activityTab.value = defaultTab; showPicList.value = false; await fetchActivitiesByLead(lead.lead_id, defaultTab); };
const switchActivityTab = async (tab) => { activityTab.value = tab; if(selectedActivityLead.value) await fetchActivitiesByLead(selectedActivityLead.value.lead_id, tab); };
const openInputModal = (item = null) => {
  if (item) { isEditingActivity.value = true; formActivity.value = JSON.parse(JSON.stringify(item)); } 
  else { isEditingActivity.value = false; resetFormActivity(selectedActivityLead.value); const statusMap = { 'follow_up': 'Follow Up', 'quotation': 'Quotation' }; formActivity.value.stage = statusMap[selectedActivityLead.value.status_kanban] || 'Activity Log'; }
  showInputModal.value = true;
};
const resetFormActivity = (leadObj = null) => { formActivity.value = { id: null, lead: leadObj ? leadObj.lead_id : null, pic_gp: leadObj ? leadObj.gp_pic : '', pic_lead: '', date: new Date().toISOString().split('T')[0], start_time: '', end_time: '', objective: 'Sales & Leads', stage: 'Follow Up', fu_type: 'Phone Calls/Telephone', notes: '', meeting_type: 'Visit Meeting', location: '', latitude: '', longitude: '', mom: '', link_quotation: '', is_send: false }; };
const saveActivityLog = async () => {
  if (activityTab.value === 'quotation' && !formActivity.value.link_quotation) { showToast('warning', 'Link Quotation wajib diisi!'); return; }
  try {
    let endpoint = 'followups/'; if (activityTab.value === 'meeting') endpoint = 'meetings/'; if (activityTab.value === 'quotation') endpoint = 'quotations/';
    const payload = { ...formActivity.value, lead: selectedActivityLead.value.lead_id };
    if (isEditingActivity.value) await api.put(`${endpoint}${formActivity.value.id}/`, payload); else await api.post(endpoint, payload);
    showToast('success', 'Data tersimpan'); showInputModal.value = false; fetchActivitiesByLead(selectedActivityLead.value.lead_id, activityTab.value);
  } catch (error) { showToast('error', 'Gagal simpan'); }
};
const deleteActivityItem = async (id) => { if (!confirm("Hapus aktivitas ini?")) return; try { let endpoint = 'followups/'; if (activityTab.value === 'meeting') endpoint = 'meetings/'; if (activityTab.value === 'quotation') endpoint = 'quotations/'; await api.delete(`${endpoint}${id}/`); showToast('success', 'Berhasil dihapus'); fetchActivitiesByLead(selectedActivityLead.value.lead_id, activityTab.value); } catch (error) { showToast('error', 'Gagal hapus'); } };

onMounted(() => { fetchLeads(); });

onMounted(() => {
  if (!window.google || !addressInput.value) return;

  const autocomplete = new google.maps.places.Autocomplete(
    addressInput.value,
    {
      fields: ['formatted_address', 'geometry'],
    }
  );

  autocomplete.addListener('place_changed', () => {
    const place = autocomplete.getPlace();

    if (!place.geometry) return;

    // Simpan alamat sebagai STRING (varchar)
    formLead.address = place.formatted_address;

    // Simpan koordinat (opsional tapi biasanya dibutuhkan)
    formLead.latitude = place.geometry.location.lat();
    formLead.longitude = place.geometry.location.lng();
  });
});
</script>

<template>
  <MainLayout>
    <div class="mb-6 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">Leads Pipeline</h1>
        <p class="text-gray-500">Geser kartu untuk memproses. Double klik kartu untuk detail.</p>
      </div>
    </div>

    <div class="flex gap-4 overflow-x-auto pb-8 h-[calc(100vh-150px)] items-start">
      <div class="min-w-[320px] bg-gray-100 rounded-xl p-3 flex flex-col gap-3 h-full">
        <div class="flex justify-between items-center px-2">
          <h3 class="font-bold text-gray-700">Lead Generation</h3>
          <div class="flex items-center gap-2">
            <button @click="openModal()" class="bg-white border border-gray-300 hover:bg-blue-50 text-gray-600 rounded px-2 py-0.5 shadow-sm transition flex items-center justify-center"><Plus :size="16" /></button>
            <span class="bg-gray-300 px-2 rounded-full text-xs py-1 font-bold text-gray-700">{{ leadsGenInbound.length + leadsGenOutbound.length }}</span>
          </div>
        </div>
        
        <div class="bg-blue-50/50 p-2 rounded-lg border border-blue-100 flex-1 flex flex-col">
          <div class="flex justify-between items-center mb-2"><h4 class="text-xs font-bold text-blue-600 uppercase tracking-wide">Inbound</h4><span class="text-[10px] font-bold bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">{{ leadsGenInbound.length }}</span></div>
          <draggable v-model="leadsGenInbound" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2 min-h-[50px]"><template #item="{element}"><div @dblclick="openDetailModal(element)" class="bg-white p-3 rounded shadow-sm border border-gray-200 cursor-move hover:shadow-md transition relative group select-none"><div class="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white/90 rounded p-0.5 shadow z-10"><button @click.stop="openModal(element)" class="text-blue-500 hover:bg-blue-100 p-1 rounded"><Edit :size="14" /></button><button @click.stop="deleteLead(element.lead_id)" class="text-red-500 hover:bg-red-100 p-1 rounded"><Trash2 :size="14" /></button></div><div class="font-bold text-gray-800 text-sm mb-1 pr-12">{{ element.property }}</div><div class="text-xs text-blue-500 mb-2">{{ element.source }}</div><div class="text-xs text-gray-500 flex items-center gap-1"><User :size="12"/> {{ element.gp_pic }}</div></div></template></draggable>
        </div>

        <div class="bg-orange-50/50 p-2 rounded-lg border border-orange-100 flex-1 flex flex-col mt-2">
          <div class="flex justify-between items-center mb-2"><h4 class="text-xs font-bold text-orange-600 uppercase tracking-wide">Outbound</h4><span class="text-[10px] font-bold bg-orange-100 text-orange-600 px-2 py-0.5 rounded-full">{{ leadsGenOutbound.length }}</span></div>
          <draggable v-model="leadsGenOutbound" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2 min-h-[50px]"><template #item="{element}"><div @dblclick="openDetailModal(element)" class="bg-white p-3 rounded shadow-sm border border-gray-200 cursor-move hover:shadow-md transition relative group select-none"><div class="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white/90 rounded p-0.5 shadow z-10"><button @click.stop="openModal(element)" class="text-blue-500 hover:bg-blue-100 p-1 rounded"><Edit :size="14" /></button><button @click.stop="deleteLead(element.lead_id)" class="text-red-500 hover:bg-red-100 p-1 rounded"><Trash2 :size="14" /></button></div><div class="font-bold text-gray-800 text-sm mb-1 pr-12">{{ element.property }}</div><div class="text-xs text-orange-500 mb-2">{{ element.source }}</div><div class="text-xs text-gray-500 flex items-center gap-1"><User :size="12"/> {{ element.gp_pic }}</div></div></template></draggable>
        </div>
      </div>

      <div class="min-w-[300px] bg-gray-100 rounded-xl p-3 flex flex-col h-full">
        <h3 class="font-bold text-gray-700 px-2 mb-3 flex justify-between">Follow Up <span class="bg-yellow-200 px-2 rounded-full text-xs py-1">{{ leadsFollowUp.length }}</span></h3>
        <draggable v-model="leadsFollowUp" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2 min-h-[100px]" @change="onChangeFollowUp">
          <template #item="{element}">
            <div @dblclick="openActivityModal(element, 'followup')" class="bg-white p-3 rounded shadow-sm border-l-4 border-yellow-400 cursor-move hover:shadow-md transition relative group select-none">
              <div class="font-bold text-gray-800 text-sm mb-1">{{ element.property }}</div>
              <div class="text-xs font-medium mb-2" :class="inboundSources.includes(element.source) ? 'text-blue-500' : 'text-orange-500'">{{ element.source }}</div>
              <div class="text-xs text-gray-400 flex items-center gap-1"><User :size="10"/> {{ element.gp_pic }}</div>
              
              <div class="mt-2 pt-2 border-t border-gray-100 flex justify-center">
                 <button @click.stop="openAddNewTaskModal(element, 'followup', 'Follow Up')" class="text-xs text-blue-600 font-bold hover:bg-blue-50 w-full py-1 rounded flex items-center justify-center gap-1 transition">
                    <Plus :size="12"/> Add New Task
                 </button>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <div class="min-w-[300px] bg-gray-100 rounded-xl p-3 flex flex-col h-full">
        <h3 class="font-bold text-gray-700 px-2 mb-3 flex justify-between">Quotation <span class="bg-purple-200 px-2 rounded-full text-xs py-1">{{ leadsQuotation.length }}</span></h3>
        <draggable v-model="leadsQuotation" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2 min-h-[100px]" @change="onChangeQuotation">
          <template #item="{element}">
            <div @dblclick="openActivityModal(element, 'quotation')" class="bg-white p-3 rounded shadow-sm border-l-4 border-purple-400 cursor-move hover:shadow-md transition relative group select-none">
              <div class="font-bold text-gray-800 text-sm mb-1">{{ element.property }}</div>
              <div class="text-xs font-medium mb-2" :class="inboundSources.includes(element.source) ? 'text-blue-500' : 'text-orange-500'">{{ element.source }}</div>
              <div class="text-xs text-gray-400 flex items-center gap-1"><User :size="10"/> {{ element.gp_pic }}</div>
              
              <div class="mt-2 pt-2 border-t border-gray-100 flex justify-center">
                 <button @click.stop="openManualQuotation(element)" class="text-xs text-purple-600 font-bold hover:bg-purple-50 w-full py-1 rounded flex items-center justify-center gap-1 transition">
                    <Plus :size="12"/> Add New Task
                 </button>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <div class="min-w-[300px] bg-gray-100 rounded-xl p-3 flex flex-col h-full"><h3 class="font-bold text-gray-700 px-2 mb-3 flex justify-between">Deals <span class="bg-green-200 px-2 rounded-full text-xs py-1">{{ leadsDeals.length }}</span></h3><draggable v-model="leadsDeals" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2 min-h-[100px]" @change="onChangeDeals"><template #item="{element}"><div class="bg-white p-3 rounded shadow-sm border-l-4 border-green-500 cursor-move hover:shadow-md transition relative group select-none"><div class="font-bold text-gray-800 text-sm mb-1">{{ element.property }}</div><div class="text-xs text-gray-500 mb-2">{{ element.source }}</div><div class="text-xs text-gray-400 flex items-center gap-1"><User :size="10"/> {{ element.gp_pic }}</div></div></template></draggable></div>

      <div class="min-w-[300px] bg-gray-100 rounded-xl p-3 flex flex-col h-full"><h3 class="font-bold text-gray-700 px-2 mb-3">Onboarding</h3><draggable v-model="leadsOnboarding" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2" @change="(e) => updateStatus(e, 'onboarding')"><template #item="{element}"><div class="card-kanban border-blue-400">{{ element.property }}</div></template></draggable></div>
      <div class="min-w-[300px] bg-gray-100 rounded-xl p-3 flex flex-col h-full"><h3 class="font-bold text-gray-700 px-2 mb-3">Retention</h3><draggable v-model="leadsRetention" group="leads" item-key="lead_id" class="flex-1 flex flex-col gap-2" @change="(e) => updateStatus(e, 'retention')"><template #item="{element}"><div class="card-kanban border-pink-400">{{ element.property }}</div></template></draggable></div>
    </div>

    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4 overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl my-8 relative animate-fade-in-up">
          <div class="sticky top-0 bg-white p-6 border-b z-10 flex justify-between items-center rounded-t-xl">
            <h3 class="text-xl font-bold text-gray-800">{{ isEditing ? 'Edit Data Lead' : 'Tambah Lead Baru' }}</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><X :size="24" /></button>
          </div>
          <form @submit.prevent="handleGenericSubmit" class="p-6 space-y-6">
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
              <h4 class="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">Informasi Properti</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2"><label class="label">Nama Properti</label><input v-model="formLead.property" type="text" class="input" required></div>
                
                <div>
                    <label class="label">Source</label>
                    <select v-model="formLead.source" class="input">
                        <optgroup label="Inbound">
                            <option v-for="src in inboundSources" :key="src" :value="src">{{ src }}</option>
                        </optgroup>
                        <optgroup label="Outbound">
                            <option value="Cold Calling">Cold Calling</option>
                            <option value="Canvassing">Canvassing</option>
                            <option value="Campaign">Campaign</option>
                            <option value="Free Trial">Free Trial</option>
                            <option value="Relational">Relational</option>
                        </optgroup>
                    </select>
                </div>

                <div v-if="isReferralOrAffiliate" class="md:col-span-2 bg-blue-50 border border-blue-100 p-3 rounded-lg grid grid-cols-2 gap-4 animate-fade-in">
                    <div>
                        <label class="label text-blue-600">{{ referralLabel }}</label>
                        <input v-model="formLead.referral_or_affiliate_by" type="text" class="input border-blue-300 focus:ring-blue-500" placeholder="Nama Pemberi Referensi">
                    </div>
                    <div>
                        <label class="label text-blue-600">Commission Amount</label>
                        <input v-model="formLead.commission_amount" type="text" class="input border-blue-300 focus:ring-blue-500" placeholder="e.g. 10% or 500000">
                    </div>
                </div>

                <div><label class="label">Type</label><input v-model="formLead.type" type="text" class="input"></div>
                <div>
                  <label class="label">GuestPro PIC</label>
                  <select v-model="formLead.gp_pic" class="input" required>
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div><label class="label">Date In</label><input v-model="formLead.date_in" type="date" class="input" required></div>
                
                <div class="md:col-span-2">
                    <label class="label">Coordinates (Lat, Long)</label>
                    <input v-model="formLead.coordinates" type="text" class="input" placeholder="-8.xxx, 115.xxx">
                </div>

                <div class="md:col-span-2"><label class="label">Alamat Lengkap</label><textarea v-model="formLead.address" class="input" rows="2"></textarea></div>
              </div>
            </div>
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-3 border-b border-gray-200 flex justify-between items-center"><h4 class="text-sm font-bold text-gray-700 uppercase tracking-wide">Daftar PIC</h4><button type="button" @click="addPicRowEdit" class="text-xs bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 flex items-center gap-1 transition"><Plus :size="14"/> Tambah PIC</button></div>
              <div class="p-4 space-y-3 max-h-64 overflow-y-auto bg-gray-50">
                <div v-for="(pic, index) in formLead.pics" :key="index" class="flex gap-2 items-start bg-white p-2 rounded border shadow-sm">
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-2 flex-1"><input v-model="pic.pic_name" type="text" class="input-sm" placeholder="Nama PIC" required><input v-model="pic.phone_number" type="text" class="input-sm" placeholder="No HP"><input v-model="pic.whatsapp" type="text" class="input-sm" placeholder="WhatsApp"><input v-model="pic.email" type="email" class="input-sm" placeholder="Email"></div>
                  <button type="button" @click="removePicRowEdit(index)" class="text-red-500 hover:bg-red-100 p-1.5 rounded transition mt-0.5"><Trash2 :size="16" /></button>
                </div>
              </div>
            </div>
            <div class="pt-4 flex justify-end gap-3 border-t">
              <button type="button" @click="closeModal" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 transition">Batal</button>
              <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 shadow flex items-center gap-2 transition"><Save :size="16" /> Simpan</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDetailModal && selectedLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl relative animate-fade-in-up overflow-hidden">
          <div class="bg-gray-50 px-6 py-4 border-b flex justify-between items-start">
            <div><h2 class="text-xl font-bold text-gray-800">{{ selectedLead.property }}</h2><div class="flex items-center gap-2 mt-1"><span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">{{ selectedLead.type }}</span></div></div>
            <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600 bg-white rounded-full p-1 shadow-sm"><X :size="20" /></button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[80vh]">
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div class="space-y-3"><div><label class="text-xs font-bold text-gray-400 uppercase">Source</label><p class="text-sm font-medium text-gray-700">{{ selectedLead.source }}</p></div><div><label class="text-xs font-bold text-gray-400 uppercase">Address</label><p class="text-sm font-medium text-gray-700 flex items-start gap-1"><MapPin :size="14" class="mt-0.5 text-gray-400"/> {{ selectedLead.address || '-' }}</p></div></div>
              <div class="space-y-3">
                  <div><label class="text-xs font-bold text-gray-400 uppercase">GuestPro PIC</label><p class="text-sm font-medium text-gray-700 flex items-center gap-1"><User :size="14" class="text-gray-400"/> {{ selectedLead.gp_pic }}</p></div>
                  <div><label class="text-xs font-bold text-gray-400 uppercase">Date In</label><p class="text-sm font-medium text-gray-700 flex items-center gap-1"><Calendar :size="14" class="text-gray-400"/> {{ selectedLead.date_in }}</p></div>
                  <div><label class="text-xs font-bold text-gray-400 uppercase">Koordinat</label><p class="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded inline-block">{{ selectedLead.coordinates || '-' }}</p></div>
              </div>
            </div>
            <div class="border rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 border-b text-xs font-bold text-gray-600 uppercase">Daftar Contact Person (PIC)</div>
              <table class="w-full text-sm"><tbody class="divide-y divide-gray-100"><tr v-for="pic in selectedLead.pics" :key="pic.id" class="hover:bg-gray-50"><td class="p-3 font-medium text-gray-800">{{ pic.pic_name }}</td><td class="p-3 text-gray-600">{{ pic.phone_number }}</td><td class="p-3 text-green-600">{{ pic.whatsapp }}</td><td class="p-3 text-blue-600">{{ pic.email }}</td></tr><tr v-if="!selectedLead.pics || selectedLead.pics.length === 0"><td class="p-4 text-center text-gray-400 italic">Tidak ada data PIC</td></tr></tbody></table>
            </div>
          </div>
          <div class="bg-gray-50 p-4 border-t flex justify-end"><button @click="closeDetailModal" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 transition">Tutup</button></div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDealModal" class="fixed inset-0 z-[130] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl relative animate-fade-in-up max-h-[90vh] overflow-y-auto">
          <div class="bg-green-600 p-5 border-b rounded-t-xl flex justify-between items-center sticky top-0 z-10">
            <h3 class="font-bold text-white text-lg flex items-center gap-2"><Briefcase :size="20"/> New Deal Closing</h3>
            <button @click="cancelMoveDeal" class="text-white hover:text-green-200"><X :size="24"/></button>
          </div>
          
          <div class="p-6 space-y-6">
            <div class="bg-green-50 p-4 rounded-lg border border-green-100 flex items-center gap-3">
              <div class="bg-green-100 p-2 rounded-full"><MapPin class="text-green-600"/></div>
              <div><div class="text-xs text-green-600 font-bold uppercase">Property Name</div><div class="text-lg font-bold text-gray-800">{{ draggedItem?.property }}</div></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="label">Deal Type</label>
                <select v-model="formDeal.deal_type" class="input">
                  <option v-for="dtype in dealTypes" :key="dtype">{{ dtype }}</option>
                </select>
              </div>
              <div><label class="label">Total Rooms</label><input v-model="formDeal.room" type="number" class="input"></div>
              
              <div class="md:col-span-2">
                <label class="label">PIC Lead (Invoice Recipient)</label>
                <select v-model="formDeal.pic_lead" class="input">
                  <option :value="null">-- Pilih PIC Lead --</option>
                  <option v-for="pic in draggedItem?.pics" :key="pic.id" :value="pic.id">
                    {{ pic.pic_name }} - {{ pic.phone_number }}
                  </option>
                </select>
              </div>

              <div class="md:col-span-2"><label class="label">Notes</label><textarea v-model="formDeal.notes" rows="2" class="input"></textarea></div>
            </div>

            <div class="border rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 border-b flex justify-between items-center">
                <h4 class="text-sm font-bold text-gray-700 uppercase flex items-center gap-2"><DollarSign :size="14"/> Product & Packages</h4>
                <button type="button" @click="addDealDetailRow" class="text-xs bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 flex items-center gap-1"><Plus :size="12"/> Add Product</button>
              </div>
              <div class="p-4 bg-gray-50 space-y-3">
                <div v-for="(detail, index) in formDeal.details" :key="index" class="bg-white p-3 rounded border shadow-sm relative">
                  <button type="button" @click="removeDealDetailRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">
                    <div><label class="label">Package Name</label><input v-model="detail.package" type="text" class="input-sm" placeholder="e.g. Pro Plan"></div>
                    <div><label class="label">Product(s)</label><input v-model="detail.product" type="text" class="input-sm" placeholder="e.g. PMS, CM, BE"></div>
                    <div>
                      <label class="label">Product Amount</label>
                      <div class="flex gap-2">
                        <input v-model="detail.product_amount" type="number" class="input-sm">
                        <select v-model="detail.product_amount_by" class="input-sm w-24"><option>Month</option><option>Year</option><option>One-time</option></select>
                      </div>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div><label class="label">Initiation (Setup/Training)</label><input v-model="detail.initiation" type="text" class="input-sm" placeholder="e.g. Onsite Training"></div>
                    <div><label class="label">Initiation Amount</label><input v-model="detail.initiation_amount" type="number" class="input-sm"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="p-5 border-t bg-gray-50 flex justify-end gap-3 sticky bottom-0 z-10">
            <button @click="cancelMoveDeal" class="px-5 py-2.5 rounded-lg border bg-white hover:bg-gray-100 font-medium text-gray-700">Batal</button>
            <button @click="saveDeal" class="px-5 py-2.5 rounded-lg bg-green-600 text-white hover:bg-green-700 font-bold shadow-lg flex items-center gap-2"><Save :size="18"/> Simpan Deal</button>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showFollowUpModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto relative animate-fade-in-up flex flex-col">
          <form @submit.prevent="saveDragForm" class="flex flex-col h-full">
              <div class="bg-white p-6 border-b z-10 flex justify-between items-center">
                <div>
                  <h2 class="text-xl font-bold text-gray-800">{{ modalMode === 'drag' ? 'Proses ke Follow Up' : 'Add New Task' }}</h2>
                  <p class="text-sm text-gray-500">
                    {{ modalMode === 'drag' ? `Pilih aktivitas pertama untuk ${draggedItem?.property}.` : `Tambahkan aktivitas baru untuk ${draggedItem?.property}.` }}
                  </p>
                </div>
                <button type="button" @click="cancelMove" class="text-gray-400 hover:text-gray-600"><X :size="24" /></button>
              </div>
              
              <div class="px-6 pt-4 pb-0">
                <div class="flex gap-2 bg-gray-100 p-1 rounded-lg overflow-x-auto">
                    <button type="button" @click="activeDragTab = 'followup'" class="flex-1 py-2 rounded-md text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'followup' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:bg-gray-200'">Form Follow Up</button>
                    <button type="button" @click="activeDragTab = 'meeting'" class="flex-1 py-2 rounded-md text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'meeting' ? 'bg-white text-orange-600 shadow-sm' : 'text-gray-500 hover:bg-gray-200'">Form Meeting</button>
                    <button v-if="modalMode !== 'drag'" type="button" @click="activeDragTab = 'quotation'" class="flex-1 py-2 rounded-md text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'quotation' ? 'bg-white text-purple-600 shadow-sm' : 'text-gray-500 hover:bg-gray-200'">Form Quotation</button>
                </div>
              </div>
              
              <div class="p-6 flex-1 overflow-y-auto">
                <div v-if="activeDragTab === 'followup'" class="space-y-4 animate-fade-in">
                  <div class="grid grid-cols-2 gap-4">
                    <div><label class="label">PIC GP</label><select v-model="formActivity.pic_gp" class="input"><option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option></select></div>
                    <div><label class="label">PIC Lead</label><input v-model="formActivity.pic_lead" type="text" class="input"></div>
                  </div>
                  <div class="grid grid-cols-2 gap-4"><div><label class="label">Date</label><input v-model="formActivity.date" type="date" class="input"></div><div><label class="label">Objective</label><input v-model="formActivity.objective" type="text" class="input"></div></div>
                  <div class="grid grid-cols-2 gap-4"><div><label class="label">Start Time</label><input v-model="formActivity.start_time" type="time" class="input"></div><div><label class="label">End Time</label><input v-model="formActivity.end_time" type="time" class="input"></div></div>
                  <div><label class="label">Type</label><select v-model="formActivity.fu_type" class="input"><option>Phone Calls/Telephone</option><option>Texting/Chat</option><option>Follow up leads</option></select></div>
                  <div><label class="label">Notes</label><textarea v-model="formActivity.notes" rows="3" class="input"></textarea></div>
                </div>
                
                <div v-if="activeDragTab === 'meeting'" class="space-y-4 animate-fade-in">
                  <div class="grid grid-cols-2 gap-4">
                    <div><label class="label">PIC GP</label><select v-model="formActivity.pic_gp" class="input"><option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option></select></div>
                    <div><label class="label">PIC Lead</label><input v-model="formActivity.pic_lead" type="text" class="input"></div>
                  </div>
                  <div class="grid grid-cols-2 gap-4"><div><label class="label">Date</label><input v-model="formActivity.date" type="date" class="input"></div><div><label class="label">Objective</label><input v-model="formActivity.objective" type="text" class="input"></div></div>
                  <div class="grid grid-cols-2 gap-4"><div><label class="label">Start Time</label><input v-model="formActivity.start_time" type="time" class="input"></div><div><label class="label">End Time</label><input v-model="formActivity.end_time" type="time" class="input"></div></div>
                  <div><label class="label">Meeting Type</label><select v-model="formActivity.meeting_type" class="input"><option>Visit Meeting</option><option>Online Meeting</option><option>Office Visit Meeting</option></select></div>
                  <div v-if="formActivity.meeting_type === 'Visit Meeting'" class="bg-gray-50 p-3 rounded border space-y-3">
                     <div><label class="label">Location</label><input v-model="formActivity.location" type="text" class="input" placeholder="Nama Lokasi / Alamat"></div>
                     <div class="grid grid-cols-2 gap-3"><div><label class="label">Latitude</label><input v-model="formActivity.latitude" type="text" class="input"></div><div><label class="label">Longitude</label><input v-model="formActivity.longitude" type="text" class="input"></div></div>
                  </div>
                  <div><label class="label">MOM</label><textarea v-model="formActivity.mom" rows="3" class="input"></textarea></div>
                </div>

                <div v-if="activeDragTab === 'quotation'" class="space-y-4 animate-fade-in">
                   <div><label class="label">PIC GP</label><select v-model="formActivity.pic_gp" class="input"><option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option></select></div>
                   <div><label class="label">Date</label><input v-model="formActivity.date" type="date" class="input"></div>
                   
                   <div>
                     <label class="label">Link Quotation</label>
                     <input 
                        v-model="formActivity.link_quotation" 
                        type="text" 
                        class="input" 
                        placeholder="google.com" 
                        @blur="autoFixUrl(formActivity, 'link_quotation')" 
                        required
                     >
                   </div>
                   
                   <div class="flex items-center gap-2 cursor-pointer pt-2" @click="formActivity.is_send = !formActivity.is_send"><CheckSquare :size="20" class="text-green-600" v-if="formActivity.is_send"/><Square :size="20" class="text-gray-400" v-else/><span class="text-sm font-medium text-gray-700">Sudah Terkirim?</span></div>
                </div>
              </div>
              
              <div class="p-6 border-t bg-gray-50 flex justify-end gap-3 mt-auto">
                <button type="button" @click="cancelMove" class="px-6 py-2 rounded-lg border bg-white hover:bg-gray-100 font-medium">Batal</button>
                <button type="submit" class="px-6 py-2 rounded-lg text-white font-bold flex items-center gap-2 shadow-lg transition-colors" :class="activeDragTab === 'followup' ? 'bg-blue-600 hover:bg-blue-700' : (activeDragTab === 'meeting' ? 'bg-orange-600 hover:bg-orange-700' : 'bg-purple-600 hover:bg-purple-700')">
                  <Save :size="18" /> {{ activeDragTab === 'followup' ? 'Simpan Follow Up' : (activeDragTab === 'meeting' ? 'Simpan Meeting' : 'Simpan Quotation') }}
                </button>
              </div>
          </form>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showQuotationModal" class="fixed inset-0 z-[120] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg relative animate-fade-in-up">
          <div class="bg-white p-5 border-b rounded-t-xl flex justify-between items-center">
            <h3 class="font-bold text-gray-800 text-lg flex items-center gap-2">
              <span class="w-2 h-6 bg-purple-500 rounded-full inline-block"></span> Input Quotation
            </h3>
            <button @click="cancelMoveQuotation" class="text-gray-400 hover:text-gray-600"><X :size="24"/></button>
          </div>
          <div class="p-6">
            <form @submit.prevent="saveQuotationInitial" class="space-y-4">
              <div class="bg-purple-50 p-3 rounded text-sm text-purple-700 mb-4"><strong>Property:</strong> {{ draggedItem?.property }}</div>
              <div><label class="label">PIC GP</label><select v-model="formQuotationInitial.pic_gp" class="input"><option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option></select></div>
              <div><label class="label">Date</label><input v-model="formQuotationInitial.date" type="date" class="input" required></div>
              
              <div>
                <label class="label">Link Quotation</label>
                <input 
                  v-model="formQuotationInitial.link_quotation" 
                  type="text" 
                  class="input" 
                  placeholder="google.com" 
                  @blur="autoFixUrl(formQuotationInitial, 'link_quotation')" 
                  required
                >
              </div>

              <div class="flex items-center gap-2 cursor-pointer" @click="formQuotationInitial.is_send = !formQuotationInitial.is_send"><CheckSquare :size="20" class="text-green-600" v-if="formQuotationInitial.is_send"/><Square :size="20" class="text-gray-400" v-else/><span class="text-sm font-medium text-gray-700">Sudah Terkirim?</span></div>
              <div class="pt-4 flex justify-end gap-3 border-t mt-4">
                <button type="button" @click="cancelMoveQuotation" class="px-5 py-2.5 rounded-lg border bg-white hover:bg-gray-50 font-medium text-gray-700">Batal</button>
                <button type="submit" class="px-5 py-2.5 rounded-lg bg-purple-600 text-white hover:bg-purple-700 font-bold shadow-lg flex items-center gap-2"><Save :size="18"/> Simpan</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showActivityModal && selectedActivityLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-7xl h-[85vh] flex flex-col overflow-hidden relative animate-fade-in-up">
          <div class="bg-slate-50 p-5 border-b shrink-0">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h2 class="text-2xl font-bold text-gray-800">{{ selectedActivityLead.property }}</h2>
                <div class="flex items-center gap-2 mt-2">
                  <span class="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded font-bold">{{ selectedActivityLead.source }}</span>
                  <span class="text-xs border border-gray-300 text-gray-600 px-2 py-1 rounded">{{ selectedActivityLead.type }}</span>
                </div>
              </div>
              <button @click="showActivityModal = false" class="text-gray-400 hover:text-red-500 bg-white p-1.5 rounded-full shadow-sm transition"><X :size="24"/></button>
            </div>
            <div class="grid grid-cols-4 gap-6 text-sm text-gray-600 bg-white p-4 rounded-lg border border-gray-200 shadow-sm mb-3">
              <div><span class="block font-bold text-gray-400 uppercase text-[10px] mb-1">Alamat</span><span class="flex items-start gap-1 font-medium"><MapPin :size="14" class="mt-0.5"/> {{ selectedActivityLead.address || '-' }}</span></div>
              <div><span class="block font-bold text-gray-400 uppercase text-[10px] mb-1">Koordinat</span><span class="font-mono bg-gray-100 px-2 py-0.5 rounded">{{ selectedActivityLead.latitude || '-' }}, {{ selectedActivityLead.longitude || '-' }}</span></div>
              <div><span class="block font-bold text-gray-400 uppercase text-[10px] mb-1">PIC GuestPro</span><span class="flex items-center gap-1 font-medium"><User :size="14"/> {{ selectedActivityLead.gp_pic }}</span></div>
              <div><span class="block font-bold text-gray-400 uppercase text-[10px] mb-1">Tgl Masuk</span><span class="flex items-center gap-1 font-medium"><CalendarIcon :size="14"/> {{ selectedActivityLead.date_in }}</span></div>
            </div>

            <div class="bg-blue-50 border border-blue-100 rounded-lg overflow-hidden transition-all duration-300">
                <div @click="showPicList = !showPicList" class="px-4 py-2 flex justify-between items-center cursor-pointer hover:bg-blue-100 transition select-none">
                    <span class="text-xs font-bold text-blue-700 uppercase flex items-center gap-2"><User :size="14" /> Daftar PIC Lead ({{ selectedActivityLead.pics.length }})</span>
                    <ChevronDown :size="16" class="text-blue-500 transition-transform duration-300" :class="showPicList ? 'rotate-180' : ''" />
                </div>
                <div v-if="showPicList" class="border-t border-blue-100 bg-white p-3">
                    <div v-if="selectedActivityLead.pics.length === 0" class="text-center text-xs text-gray-400 italic">Tidak ada data PIC.</div>
                    <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <div v-for="pic in selectedActivityLead.pics" :key="pic.id" class="text-xs border rounded p-2 bg-gray-50">
                            <div class="font-bold text-gray-700">{{ pic.pic_name }}</div>
                            <div class="text-gray-500 mt-1 flex flex-col gap-0.5">
                                <span v-if="pic.phone_number">📞 {{ pic.phone_number }}</span>
                                <span v-if="pic.whatsapp" class="text-green-600">💬 {{ pic.whatsapp }}</span>
                                <span v-if="pic.email" class="text-blue-500">✉️ {{ pic.email }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>

          <div class="flex-1 flex flex-col bg-white overflow-hidden">
            <div class="flex justify-between items-center px-5 py-3 border-b bg-white">
              <div class="flex bg-gray-100 p-1 rounded-lg">
                <button @click="switchActivityTab('followup')" class="px-4 py-1.5 text-sm font-bold rounded-md transition-all" :class="activityTab==='followup' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'">Follow Up</button>
                <button @click="switchActivityTab('meeting')" class="px-4 py-1.5 text-sm font-bold rounded-md transition-all" :class="activityTab==='meeting' ? 'bg-white shadow text-orange-600' : 'text-gray-500 hover:text-gray-700'">Meeting</button>
                <button v-if="['quotation', 'deals', 'onboarding', 'retention'].includes(selectedActivityLead?.status_kanban)" @click="switchActivityTab('quotation')" class="px-4 py-1.5 text-sm font-bold rounded-md transition-all" :class="activityTab==='quotation' ? 'bg-white shadow text-purple-600' : 'text-gray-500 hover:text-gray-700'">Quotation</button>
              </div>
              <button @click="openInputModal(null)" class="bg-[#65a30d] hover:bg-[#4d7c0f] text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 shadow transition"><Plus :size="16" /> Tambah {{ activityTab === 'followup' ? 'Follow Up' : (activityTab === 'meeting' ? 'Meeting' : 'Quotation') }}</button>
            </div>

            <div class="flex-1 overflow-auto p-0">
              <table class="w-full text-left text-sm border-collapse">
                <thead class="bg-gray-50 text-gray-500 font-bold uppercase text-xs sticky top-0 z-10 shadow-sm">
                  <tr>
                    <th class="p-4 border-b w-40">Tanggal & Waktu</th>
                    <th class="p-4 border-b w-32">PIC GP</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b w-32">Tipe</th>
                    <th v-if="activityTab === 'meeting'" class="p-4 border-b w-40">Lokasi</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b w-48">Objective</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b">{{ activityTab === 'followup' ? 'Notes' : 'MOM' }}</th>
                    <th v-if="activityTab === 'quotation'" class="p-4 border-b">Link Document</th>
                    <th v-if="activityTab === 'quotation'" class="p-4 border-b w-24 text-center">Status</th>
                    <th class="p-4 border-b text-center w-24">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in activityList" :key="item.id" class="hover:bg-gray-50 transition">
                    <td class="p-4 align-top">
                      <div class="font-bold text-gray-800">{{ item.date }}</div>
                      <div v-if="activityTab !== 'quotation'" class="text-xs text-gray-500 mt-1 flex items-center gap-1"><Clock :size="12"/> {{ item.start_time?.substring(0,5) }} - {{ item.end_time?.substring(0,5) }}</div>
                    </td>
                    <td class="p-4 align-top text-gray-700 font-medium">{{ item.pic_gp }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top"><span class="px-2.5 py-1 rounded border text-xs font-semibold" :class="activityTab==='followup' ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-orange-50 text-orange-700 border-orange-100'">{{ activityTab === 'followup' ? item.fu_type : item.meeting_type }}</span></td>
                    <td v-if="activityTab === 'meeting'" class="p-4 align-top text-gray-600">{{ item.location || '-' }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top font-medium text-gray-700">{{ item.objective }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top text-gray-600 whitespace-pre-line">{{ activityTab === 'followup' ? item.notes : item.mom }}</td>
                    <td v-if="activityTab === 'quotation'" class="p-4 align-top">
                        <a :href="item.link_quotation" target="_blank" class="text-blue-600 hover:underline flex items-center gap-1">
                            <LinkIcon :size="14" class="shrink-0"/> <span class="truncate max-w-[200px]">{{ item.link_quotation }}</span>
                        </a>
                    </td>
                    <td v-if="activityTab === 'quotation'" class="p-4 align-top text-center"><span class="px-2 py-1 rounded text-xs font-bold" :class="item.is_send ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">{{ item.is_send ? 'Terkirim' : 'Draft' }}</span></td>
                    <td class="p-4 align-top text-center">
                      <div class="flex justify-center gap-2">
                        <button @click="openInputModal(item)" class="text-blue-500 hover:bg-blue-100 p-1.5 rounded transition" title="Edit"><Edit :size="16"/></button>
                        <button @click="deleteActivityItem(item.id)" class="text-red-500 hover:bg-red-100 p-1.5 rounded transition" title="Hapus"><Trash2 :size="16"/></button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="activityList.length === 0"><td :colspan="activityTab === 'meeting' ? 7 : (activityTab === 'quotation' ? 5 : 6)" class="p-12 text-center text-gray-400 italic bg-gray-50/50">Belum ada riwayat aktivitas. Klik tombol "Tambah" di atas.</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showInputModal" class="fixed inset-0 z-[120] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg relative animate-fade-in-up">
          <div class="bg-white p-5 border-b rounded-t-xl flex justify-between items-center">
            <h3 class="font-bold text-gray-800 text-lg flex items-center gap-2"><span class="w-2 h-6 bg-green-500 rounded-full inline-block"></span> {{ isEditingActivity ? 'Edit Data' : 'Input Data Baru' }}</h3>
            <button @click="showInputModal = false" class="text-gray-400 hover:text-gray-600"><X :size="24"/></button>
          </div>
          <div class="p-6 max-h-[70vh] overflow-y-auto">
            <form @submit.prevent="saveActivityLog" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label">PIC GP</label>
                  <select v-model="formActivity.pic_gp" class="input">
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div v-if="activityTab !== 'quotation'"><label class="label">PIC Lead</label><input v-model="formActivity.pic_lead" type="text" class="input"></div>
              </div>
              <div class="grid grid-cols-2 gap-4"><div><label class="label">Date</label><input v-model="formActivity.date" type="date" class="input"></div><div v-if="activityTab !== 'quotation'"><label class="label">Objective</label><input v-model="formActivity.objective" type="text" class="input"></div></div>
              <div v-if="activityTab !== 'quotation'" class="grid grid-cols-2 gap-4"><div><label class="label">Start Time</label><input v-model="formActivity.start_time" type="time" class="input"></div><div><label class="label">End Time</label><input v-model="formActivity.end_time" type="time" class="input"></div></div>
              
              <div v-if="activityTab === 'followup'" class="space-y-4">
                <div><label class="label">Follow Up Type</label><select v-model="formActivity.fu_type" class="input"><option>Phone Calls/Telephone</option><option>Texting/Chat</option><option>Follow up leads</option></select></div>
                <div><label class="label">Notes</label><textarea v-model="formActivity.notes" rows="4" class="input" placeholder="Catatan hasil..."></textarea></div>
              </div>

              <div v-if="activityTab === 'meeting'" class="space-y-4">
                <div><label class="label">Meeting Type</label><select v-model="formActivity.meeting_type" class="input"><option>Visit Meeting</option><option>Online Meeting</option><option>Office Visit Meeting</option></select></div>
                <div v-if="formActivity.meeting_type === 'Visit Meeting'" class="bg-gray-50 p-3 rounded border space-y-3">
                   <div><label class="label">Location</label><input v-model="formActivity.location" type="text" class="input" placeholder="Nama Lokasi / Alamat"></div>
                   <div class="grid grid-cols-2 gap-3"><div><label class="label">Latitude</label><input v-model="formActivity.latitude" type="text" class="input"></div><div><label class="label">Longitude</label><input v-model="formActivity.longitude" type="text" class="input"></div></div>
                </div>
                <div><label class="label">MOM</label><textarea v-model="formActivity.mom" rows="4" class="input" placeholder="Minutes of Meeting..."></textarea></div>
              </div>

              <div v-if="activityTab === 'quotation'" class="space-y-4">
                 <div>
                   <label class="label">Link Quotation</label>
                   <input 
                      v-model="formActivity.link_quotation" 
                      type="text" 
                      class="input" 
                      placeholder="google.com" 
                      @blur="autoFixUrl(formActivity, 'link_quotation')" 
                      required
                   >
                 </div>
                 <div class="flex items-center gap-2 cursor-pointer pt-2" @click="formActivity.is_send = !formActivity.is_send"><CheckSquare :size="20" class="text-green-600" v-if="formActivity.is_send"/><Square :size="20" class="text-gray-400" v-else/><span class="text-sm font-medium text-gray-700">Sudah Terkirim?</span></div>
              </div>

              <div class="pt-4 flex justify-end gap-3 border-t mt-4">
                <button type="button" @click="showInputModal = false" class="px-5 py-2.5 rounded-lg border bg-white hover:bg-gray-50 font-medium text-gray-700">Batal</button>
                <button type="submit" class="px-5 py-2.5 rounded-lg bg-green-600 text-white hover:bg-green-700 font-bold shadow-lg flex items-center gap-2"><Save :size="18"/> Simpan</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4 overflow-y-auto">
       <div class="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] my-8 relative animate-fade-in-up flex flex-col">
          <div class="sticky top-0 bg-white p-6 border-b z-10 flex justify-between items-center rounded-t-xl">
            <h3 class="text-xl font-bold text-gray-800">{{ isEditing ? 'Edit Data Lead' : 'Tambah Lead Baru' }}</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><X :size="24" /></button>
          </div>
          <div class="overflow-y-auto flex-1 p-6">
            <form @submit.prevent="handleGenericSubmit" class="p-6 space-y-6">
              <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 class="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">Informasi Properti</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="md:col-span-2">
                    <label class="label">Nama Properti</label>
                    <input v-model="formLead.property" type="text" class="input" required>
                  </div>
                  
                  <div>
                    <label class="label">Source</label>
                    <select v-model="formLead.source" class="input">
                      <option v-for="src in inboundSources" :key="src" :value="src">{{ src }} (Inbound)</option>
                      <option value="Cold Calling">Cold Calling</option>
                      <option value="Canvassing">Canvassing</option>
                      <option value="Campaign">Campaign</option>
                      <option value="Free Trial">Free Trial</option>
                      <option value="Relational">Relational</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="label">Type</label>
                    <input v-model="formLead.type" type="text" class="input">
                  </div>
                  
                  <div>
                    <label class="label">GuestPro PIC</label>
                    <select v-model="formLead.gp_pic" class="input" required>
                      <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="label">Date In</label>
                    <input v-model="formLead.date_in" type="date" class="input" required>
                  </div>
                  
                  <!--  KOORDINAT JADI 1 FIELD -->
                  <div class="md:col-span-2">
                    <label class="label">Koordinat (Latitude, Longitude)</label>
                    <input 
                      v-model="formLead.coordinates" 
                      type="text" 
                      class="input font-mono text-sm" 
                      placeholder="contoh: -7.797068, 110.370529"
                      readonly
                    >
                    <p class="text-xs text-gray-500 mt-1">💡 Gunakan peta di bawah untuk memilih lokasi</p>
                  </div>
                  
                  <!-- MAP SECTION -->
                  <div class="md:col-span-2">
                    <label class="label">Alamat Lengkap</label>
                    
                    <!-- Search Box -->
                    <div class="flex gap-2 mb-2">
                      <input
                        v-model="mapSearchQuery"
                        type="text"
                        class="input flex-1"
                        placeholder="Cari lokasi ( contoh : Bandara Ngurah Rai )"
                        @keyup.enter="searchLocation"
                      />
                      <button 
                        type="button" 
                        @click="searchLocation" 
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium whitespace-nowrap"
                      >
                        Cari
                      </button>
                    </div>

                    <!-- Map Container -->
                    <div
                      ref="mapContainer"
                      class="w-full h-64 rounded-lg border border-gray-300 mb-3"
                    ></div>

                    <!-- Info Card -->
                    <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
                      <div class="flex items-start gap-3">
                        <div class="text-3xl"></div>
                        <div class="flex-1 space-y-2">
                          <div class="flex items-center gap-2">
                            <span class="text-xs font-bold text-gray-600 uppercase">Koordinat:</span>
                            <span class="font-mono text-sm text-gray-800 bg-white px-2 py-1 rounded border">
                              {{ formLead.coordinates || 'Belum dipilih' }}
                            </span>
                          </div>
                          <div class="flex items-start gap-2">
                            <span class="text-xs font-bold text-gray-600 uppercase shrink-0">Alamat:</span>
                            <span class="text-sm text-gray-700">
                              {{ formLead.address || 'Klik/drag marker atau search untuk memilih lokasi' }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Input Manual Alamat -->
                    <div class="mt-3">
                      <label class="label">Edit Alamat Manual (Opsional)</label>
                      <textarea 
                        v-model="formLead.address" 
                        rows="2" 
                        class="input text-sm" 
                        placeholder="Atau ketik/edit alamat manual di sini..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="bg-gray-100 px-4 py-3 border-b border-gray-200 flex justify-between items-center"><h4 class="text-sm font-bold text-gray-700 uppercase tracking-wide">Daftar PIC</h4><button type="button" @click="addPicRowEdit" class="text-xs bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 flex items-center gap-1 transition"><Plus :size="14"/> Tambah PIC</button></div>
                <div class="p-4 space-y-3 max-h-64 overflow-y-auto bg-gray-50">
                  <div v-for="(pic, index) in formLead.pics" :key="index" class="flex gap-2 items-start bg-white p-2 rounded border shadow-sm">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 flex-1"><input v-model="pic.pic_name" type="text" class="input-sm" placeholder="Nama PIC" required><input v-model="pic.phone_number" type="text" class="input-sm" placeholder="No HP"><input v-model="pic.whatsapp" type="text" class="input-sm" placeholder="WhatsApp"><input v-model="pic.email" type="email" class="input-sm" placeholder="Email"></div>
                    <button type="button" @click="removePicRowEdit(index)" class="text-red-500 hover:bg-red-100 p-1.5 rounded transition mt-0.5"><Trash2 :size="16" /></button>
                  </div>
                </div>
              </div>
              <div class="pt-4 flex justify-end gap-3 border-t">
                <button type="button" @click="closeModal" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 transition">Batal</button>
                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 shadow flex items-center gap-2 transition"><Save :size="16" /> Simpan</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDetailModal && selectedLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl relative animate-fade-in-up overflow-hidden">
          <div class="bg-gray-50 px-6 py-4 border-b flex justify-between items-start">
            <div><h2 class="text-xl font-bold text-gray-800">{{ selectedLead.property }}</h2><div class="flex items-center gap-2 mt-1"><span class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">{{ selectedLead.type }}</span></div></div>
            <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600 bg-white rounded-full p-1 shadow-sm"><X :size="20" /></button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[80vh]">
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div class="space-y-3"><div><label class="text-xs font-bold text-gray-400 uppercase">Source</label><p class="text-sm font-medium text-gray-700">{{ selectedLead.source }}</p></div><div><label class="text-xs font-bold text-gray-400 uppercase">Address</label><p class="text-sm font-medium text-gray-700 flex items-start gap-1"><MapPin :size="14" class="mt-0.5 text-gray-400"/> {{ selectedLead.address || '-' }}</p></div></div>
              <div class="space-y-3"><div><label class="text-xs font-bold text-gray-400 uppercase">GuestPro PIC</label><p class="text-sm font-medium text-gray-700 flex items-center gap-1"><User :size="14" class="text-gray-400"/> {{ selectedLead.gp_pic }}</p></div><div><label class="text-xs font-bold text-gray-400 uppercase">Date In</label><p class="text-sm font-medium text-gray-700 flex items-center gap-1"><Calendar :size="14" class="text-gray-400"/> {{ selectedLead.date_in }}</p></div><div><label class="text-xs font-bold text-gray-400 uppercase">Koordinat</label><p class="text-xs font-mono text-gray-500">{{ selectedLead.coordinates || '-' }}</p></div></div>
            </div>
            <div class="border rounded-lg overflow-hidden">
              <div class="bg-gray-100 px-4 py-2 border-b text-xs font-bold text-gray-600 uppercase">Daftar Contact Person (PIC)</div>
              <table class="w-full text-sm"><tbody class="divide-y divide-gray-100"><tr v-for="pic in selectedLead.pics" :key="pic.id" class="hover:bg-gray-50"><td class="p-3 font-medium text-gray-800">{{ pic.pic_name }}</td><td class="p-3 text-gray-600">{{ pic.phone_number }}</td><td class="p-3 text-green-600">{{ pic.whatsapp }}</td><td class="p-3 text-blue-600">{{ pic.email }}</td></tr><tr v-if="!selectedLead.pics || selectedLead.pics.length === 0"><td class="p-4 text-center text-gray-400 italic">Tidak ada data PIC</td></tr></tbody></table>
            </div>
          </div>
          <div class="bg-gray-50 p-4 border-t flex justify-end"><button @click="closeDetailModal" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-100 transition">Tutup</button></div>
        </div>
      </div>
    </Teleport>

  </MainLayout>
</template>

<style scoped>
.card-kanban { @apply bg-white p-3 rounded shadow-sm border-l-4 cursor-move hover:shadow-md transition text-sm font-bold text-gray-700 select-none; }
.label { @apply block text-xs font-semibold text-gray-500 mb-1; }
.input { @apply w-full border border-gray-300 rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none; }
.input-sm { @apply w-full border border-gray-300 rounded px-2 py-1.5 text-xs focus:ring-1 focus:ring-blue-500 outline-none; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in-up { animation: fadeInUp 0.3s ease-out; }
.pac-container {
  z-index: 9999 !important;
}
</style>