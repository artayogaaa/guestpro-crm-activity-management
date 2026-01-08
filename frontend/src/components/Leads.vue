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

const formatWhatsapp = (number) => {
  if (!number) return ''
  return number
    .replace(/\D/g, '')
    .replace(/^0/, '62')       
}

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

const trainingTypes = [
  'Implementation',
  'Maintenance', 
  'Migration'
];

const moduleOptions = [
  'Angka',
  'Buah',
  'Makan'
];

// =======================================================================
// STATE DATA
// =======================================================================
const allLeads = ref([]);

const leadsFollowUp = ref([]);
const leadsQuotation = ref([]);
const leadsDeals = ref([]);
const leadsOnboarding = ref([]);
const leadsRetention = ref([]);
const leadsGenInbound = ref([]);
const leadsGenOutbound = ref([]);
const showDealDetailModal = ref(false);
const selectedDeal = ref(null);
const dealDetails = ref(null);

// =======================================================================
// MODAL STATES
// =======================================================================

const showFollowUpModal = ref(false);
const draggedItem = ref(null); 
const activeDragTab = ref('followup'); 
const modalMode = ref('drag'); 

const showOnboardingModal = ref(false);
const selectedOnboardingLead = ref(null);
const onboardingActivityList = ref([]);
const onboardingTab = ref('followup');
const showOnboardingInputModal = ref(false);
const isEditingOnboardingActivity = ref(false);

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

const setupTypes = [
  'Setup Implementation',
  'Setup Maintenance', 
  'Setup Migration'
];

const taskOptions = [
  'Setup Master Data',
  'Reservation Transaction Import',
  'POS Transaction Import',
  'Accounting Transaction Import',
  'Mapping',
  'Others',
  'Setup Printer',
  'Setup Printed & Adapter'
];

const formOnboarding = ref({
  id: null,
  lead: null,
  deal: null,
  pic_gp: '',
  
  // Common fields
  date: new Date().toISOString().split('T')[0],
  start_time: '',
  end_time: '',
  
  // Follow Up & Meeting
  pic_lead: '',
  objective: 'Onboarding',
  stage: 'Onboarding',
  fu_type: 'Phone Calls/Telephone',
  notes: '',
  meeting_type: 'Visit Meeting',
  location: '',
  mom: '',
  
  // Setup Data Specific
  setup_type: '',
  product: '',
  task: '',
  setup_notes: '',
  status: 'On Progress',
  
  // Training Specific
  training_type: 'Implementation',
  periode: '',
  module_in_charge: '',
  training_product: '',
  training_notes: ''
});

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

const fetchOnboardingActivities = async (leadId, type) => {
  try {
    let endpoint = '';
    switch(type) {
      case 'followup': endpoint = 'followups/'; break;
      case 'meeting': endpoint = 'meetings/'; break;
      case 'setupdata': endpoint = 'setupdata/'; break;
      case 'training': endpoint = 'trainings/'; break;
    }
    const response = await api.get(endpoint);
    
    onboardingActivityList.value = response.data
      .filter(item => item.lead === leadId)
      .map(item => {
        if (type === 'setupdata') return { ...item, id: item.setup_id };
        if (type === 'training') return { ...item, id: item.training_id };
        return item;
      });
      
  } catch (error) {
    console.error('Error fetching:', error.response?.data);
    showToast('error', 'Gagal memuat riwayat onboarding');
  }
};

const openOnboardingModal = async (lead) => {
  selectedOnboardingLead.value = lead;
  showOnboardingModal.value = true;
  onboardingTab.value = 'followup';
  await fetchOnboardingActivities(lead.lead_id, 'followup');
};

const switchOnboardingTab = async (tab) => {
  onboardingTab.value = tab;
  if(selectedOnboardingLead.value) {
    await fetchOnboardingActivities(selectedOnboardingLead.value.lead_id, tab);
  }
};

const openOnboardingInputModal = (item = null) => {
  if (item) {
    isEditingOnboardingActivity.value = true;
    
    if (onboardingTab.value === 'setupdata') {
      const startDate = item.start ? new Date(item.start) : null;
      const endDate = item.end ? new Date(item.end) : null;
      
      formOnboarding.value = {
        id: item.setup_id,
        lead: item.lead,
        deal: item.deal,
        pic_gp: item.pic_gp,
        date: startDate ? startDate.toISOString().split('T')[0] : '',
        start_time: startDate ? startDate.toTimeString().slice(0,5) : '',
        end_time: endDate ? endDate.toTimeString().slice(0,5) : '',
        setup_type: item.setup_type,
        product: item.product,
        task: item.task,
        setup_notes: item.notes,
        status: item.status
      };
    } else if (onboardingTab.value === 'training') {
      formOnboarding.value = {
        id: item.training_id,
        lead: item.lead,
        deal: item.deal,
        pic_gp: item.pic_gp,
        date: item.date,
        start_time: item.start,
        end_time: item.end || '',
        training_type: item.training_type,
        periode: item.periode,
        module_in_charge: item.module_in_charge,
        training_product: item.product,
        training_notes: item.notes || ''
      };
    } else {
      formOnboarding.value = JSON.parse(JSON.stringify(item));
    }
  } else {
    isEditingOnboardingActivity.value = false;

    const dealId = selectedOnboardingLead.value.deal_id || null;

    formOnboarding.value = {
      id: null,
      lead: selectedOnboardingLead.value.lead_id,
      deal: dealId,
      pic_gp: selectedOnboardingLead.value.gp_pic,
      date: new Date().toISOString().split('T')[0],
      start_time: '',
      end_time: '',
      
      setup_type: '',
      product: '',
      task: '',
      setup_notes: '',
      status: 'On Progress',
      
      training_type: 'Implementation',
      periode: '',
      module_in_charge: '',
      training_product: '',
      training_notes: ''
    };
  }
  showOnboardingInputModal.value = true;
};

const saveOnboardingActivity = async () => {
  console.log('🔵 === START saveOnboardingActivity ===');
  console.log('📌 onboardingTab:', onboardingTab.value);
  console.log('📌 isEditing:', isEditingOnboardingActivity.value);
  console.log('📌 formOnboarding RAW:', JSON.stringify(formOnboarding.value, null, 2));
  
  try {
    let endpoint = '';
    let payload = {};
    
    switch(onboardingTab.value) {
      case 'followup': 
        endpoint = 'followups/';
        payload = {
          lead: selectedOnboardingLead.value.lead_id,
          pic_gp: formOnboarding.value.pic_gp,
          pic_lead: formOnboarding.value.pic_lead,
          date: formOnboarding.value.date,
          start_time: formOnboarding.value.start_time,
          end_time: formOnboarding.value.end_time,
          objective: formOnboarding.value.objective,
          stage: 'Onboarding',
          fu_type: formOnboarding.value.fu_type,
          notes: formOnboarding.value.notes
        };
        break;
        
      case 'meeting': 
        endpoint = 'meetings/';
        payload = {
          lead: selectedOnboardingLead.value.lead_id,
          pic_gp: formOnboarding.value.pic_gp,
          pic_lead: formOnboarding.value.pic_lead,
          date: formOnboarding.value.date,
          start_time: formOnboarding.value.start_time,
          end_time: formOnboarding.value.end_time,
          objective: formOnboarding.value.objective,
          stage: 'Onboarding',
          meeting_type: formOnboarding.value.meeting_type,
          location: formOnboarding.value.location,
          coordinates: formOnboarding.value.coordinates || '',
          mom: formOnboarding.value.mom
        };
        break;
        
      case 'setupdata': {
        endpoint = 'setupdata/';

        try {
          const response = await api.get('deals/');
          const allDeals = response.data;

          const latestDeal = allDeals
            .filter(d => d.lead === selectedOnboardingLead.value.lead_id)
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];

          if (!latestDeal) {
            showToast('error', 'Lead ini belum memiliki data Deal. Silakan buat Deal terlebih dahulu.');
            return;
          }

          const startDateTime = formOnboarding.value.date && formOnboarding.value.start_time 
            ? `${formOnboarding.value.date}T${formOnboarding.value.start_time}:00`
            : null;
          const endDateTime = formOnboarding.value.date && formOnboarding.value.end_time 
            ? `${formOnboarding.value.date}T${formOnboarding.value.end_time}:00`
            : null;

          payload = {
            lead: selectedOnboardingLead.value.lead_id,
            deal: latestDeal.deal_id,
            pic_gp: formOnboarding.value.pic_gp,
            start: startDateTime,
            end: endDateTime,
            setup_type: formOnboarding.value.setup_type,
            product: formOnboarding.value.product,
            task: formOnboarding.value.task,
            notes: formOnboarding.value.setup_notes || '',
            status: formOnboarding.value.status
          };

        } catch (error) {
          console.error('Error finding latest deal:', error);
          showToast('error', 'Gagal mengambil data Deal terbaru.');
          return;
        }
        break;
      }
        
      case 'training': {
        endpoint = 'trainings/';
        
        try {
          const response = await api.get('deals/');
          const allDeals = response.data;

          const latestDeal = allDeals
            .filter(d => d.lead === selectedOnboardingLead.value.lead_id)
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];

          if (!latestDeal) {
            showToast('error', 'Lead ini belum memiliki data Deal. Silakan buat Deal terlebih dahulu.');
            return;
          }

          payload = {
            lead: selectedOnboardingLead.value.lead_id,
            deal: latestDeal.deal_id,
            pic_gp: formOnboarding.value.pic_gp,
            date: formOnboarding.value.date,
            start: formOnboarding.value.start_time,
            end: formOnboarding.value.end_time || null,
            training_type: formOnboarding.value.training_type,
            periode: formOnboarding.value.periode,
            module_in_charge: formOnboarding.value.module_in_charge,
            product: formOnboarding.value.training_product,
            notes: formOnboarding.value.training_notes || ''
          };

        } catch (error) {
          console.error('Error finding latest deal:', error);
          showToast('error', 'Gagal mengambil data Deal terbaru.');
          return;
        }
        break;
      }
    }
    
    console.log('📤 Endpoint:', endpoint);
    console.log('📤 Payload:', JSON.stringify(payload, null, 2));
    
    let response;
    if (isEditingOnboardingActivity.value) {
      console.log('✏️ UPDATE Mode - ID:', formOnboarding.value.id);
      response = await api.put(`${endpoint}${formOnboarding.value.id}/`, payload);
      console.log('✅ UPDATE Response:', response.data);
    } else {
      console.log('➕ CREATE Mode');
      response = await api.post(endpoint, payload);
      console.log('✅ CREATE Response:', response.data);
    }
    
    showToast('success', 'Data tersimpan');
    showOnboardingInputModal.value = false;
    fetchOnboardingActivities(selectedOnboardingLead.value.lead_id, onboardingTab.value);
    
    console.log('🟢 === END saveOnboardingActivity SUCCESS ===');
    
  } catch (error) {
    console.error('🔴 === ERROR saveOnboardingActivity ===');
    console.error('❌ Error Object:', error);
    console.error('❌ Error Response:', error.response);
    console.error('❌ Error Data:', JSON.stringify(error.response?.data, null, 2));
    console.error('❌ Error Status:', error.response?.status);
    console.error('❌ Error Headers:', error.response?.headers);
    console.error('🔴 === END ERROR ===');
    
    showToast('error', `Gagal simpan: ${error.response?.data?.detail || error.message}`);
  }
};

const deleteOnboardingActivity = async (id) => {
  if (!confirm("Hapus aktivitas ini?")) return;
  try {
    let endpoint = '';
    switch(onboardingTab.value) {
      case 'followup': endpoint = 'followups/'; break;
      case 'meeting': endpoint = 'meetings/'; break;
      case 'setupdata': endpoint = 'setupdata/'; break;
      case 'training': endpoint = 'trainings/'; break;
    }
    await api.delete(`${endpoint}${id}/`);
    showToast('success', 'Berhasil dihapus');
    fetchOnboardingActivities(selectedOnboardingLead.value.lead_id, onboardingTab.value);
  } catch (error) {
    showToast('error', 'Gagal hapus');
  }
};

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

const productCatalog = {
  'PMS': ['PMS Standard', 'PMS Pro'],
  'Orderbil': ['Orderbil Standard', 'Orderbil Pro']
};

const initiationOptions = [
  'Visit Training', 
  'Online Training', 
  'Office Visit Meeting'
];

const formDeal = ref({
  lead: null,
  deal_by: '',
  deal_type: 'New Deal',
  room: 0,
  pic_lead: null,
  notes: '',
  products: [],     
  initiations: []   
});

const getAvailablePackages = (currentIndex) => {
  const selectedPackages = formDeal.value.products
    .map((item, idx) => idx !== currentIndex ? item.package : null)
    .filter(p => p !== null);
  return Object.keys(productCatalog).filter(p => !selectedPackages.includes(p));
};

const getProductsForPackage = (pkgName) => {
  return pkgName && productCatalog[pkgName] ? productCatalog[pkgName] : [];
};

const addDealProductRow = () => {
  formDeal.value.products.push({ package: '', product: '', amount: 0, cycle: 'Month' });
};
const removeDealProductRow = (i) => formDeal.value.products.splice(i, 1);

const addDealInitiationRow = () => {
  formDeal.value.initiations.push({ product: '', amount: 0 });
};
const removeDealInitiationRow = (i) => formDeal.value.initiations.splice(i, 1);

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

const fetchDealDetail = async (leadId) => {
  try {
    const response = await api.get(`deals/?lead=${leadId}`);
    if (response.data && response.data.length > 0) {
      dealDetails.value = response.data[0];
    } else {
      dealDetails.value = null;
    }
  } catch (error) {
    showToast('error', 'Gagal memuat detail deal');
    dealDetails.value = null;
  }
};

const openDealDetailModal = async (lead) => {
  selectedDeal.value = lead;
  showDealDetailModal.value = true;
  await fetchDealDetail(lead.lead_id);
};

const closeDealDetailModal = () => {
  showDealDetailModal.value = false;
  selectedDeal.value = null;
  dealDetails.value = null;
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
      coordinates: '', address: '', gp_pic: '', deal_by:'',
      date_in: new Date().toISOString().split('T')[0],
      referral_or_affiliate_by: '', commission_amount: '',
      pics: [{ pic_name: '', phone_number: '', whatsapp: '', email: '' }] 
    }; 
  }
  showEditModal.value = true;
};

const closeModal = () => showEditModal.value = false;

const handleTabChange = async (tab) => {
  activeDragTab.value = tab;
  
  if (tab === 'meeting' && formActivity.value.meeting_type === 'Visit Meeting') {
    console.log('🗺️ Tab meeting clicked, init map...');
    await nextTick();
    setTimeout(() => {
      initMeetingMap();
    }, 300);
  }
};

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
      products: [{ package: '', product: '', amount: 0, cycle: 'Month' }],
      initiations: []
    };
  }
};

const saveDeal = async () => {
  try {
    const pk = draggedItem.value.lead_id;
    const finalDetails = [];

    formDeal.value.products.forEach(p => {
        if(p.package && p.product) {
            finalDetails.push({
                package: p.package,
                
                product_initiation: p.product,
                product_initiation_amount: p.amount,
                product_initiation_amount_by: p.cycle
            });
        }
    });

    formDeal.value.initiations.forEach(i => {
        if(i.product) { 
            finalDetails.push({
                package: 'Initiation',
                product_initiation: i.product, 
                product_initiation_amount: i.amount,
                product_initiation_amount_by: 'One-time Cost' 
            });
        }
    });

    const payload = {
        ...formDeal.value,
        details: finalDetails
    };
    
    delete payload.products;
    delete payload.initiations;

    await api.patch(`leads/${pk}/`, { status_kanban: 'deals' });
    await api.post('deals/', payload);

    showToast('success', 'Deal berhasil dibuat!');
    showDealModal.value = false;
    fetchLeads();
  } catch (error) { 
    console.error("Error Details:", error.response?.data);
    showToast('error', 'Gagal simpan deal. Cek form anda.'); 
  }
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

// =======================================================================
// LEAFLET MAP
// =======================================================================

const mapContainer = ref(null)
const mapSearchQuery = ref('')
let map = null
let marker = null

const cleanAddress = (fullAddress) => {
  if (!fullAddress) return '';

  const parts = fullAddress
    .split(',')
    .map(p => p.trim());

  const streetIndex = parts.findIndex(part =>
    /^(jalan|jl\.?|street|road)\b/i.test(part)
  );

  if (streetIndex === -1) {
    return parts.slice(1).join(', ');
  }

  return parts.slice(streetIndex).join(', ');
};

const initLeafletMap = async () => {
  await nextTick()
  
  if (!mapContainer.value) {
    console.error('❌ Map container belum siap')
    return
  }

  if (map) {
    map.remove()
  }

  let initLat = -7.797068
  let initLng = 110.370529
  
  if (formLead.value.coordinates) {
    const coords = formLead.value.coordinates.split(',')
    if (coords.length === 2) {
      initLat = parseFloat(coords[0].trim())
      initLng = parseFloat(coords[1].trim())
    }
  }

  console.log('Inisialisasi Leaflet Map...')

  map = L.map(mapContainer.value).setView([initLat, initLng], 14)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map)

  marker = L.marker([initLat, initLng], {
    draggable: true
  }).addTo(map)

  marker.on('dragend', async () => {
    const pos = marker.getLatLng()
    const lat = pos.lat.toFixed(6)
    const lng = pos.lng.toFixed(6)
    
    formLead.value.coordinates = `${lat},${lng}`
    await reverseGeocode(pos.lat, pos.lng)
  })

  map.on('click', (e) => {
    marker.setLatLng(e.latlng)
    const lat = e.latlng.lat.toFixed(6)
    const lng = e.latlng.lng.toFixed(6)
    
    formLead.value.coordinates = `${lat},${lng}`
    reverseGeocode(e.latlng.lat, e.latlng.lng)
  })

  setTimeout(() => {
    map.invalidateSize()
    console.log('Map ready!')
  }, 300)
}

const searchLocation = async () => {
if (!map || !marker) {
    console.warn('⏳ Map belum siap, init dulu')
    initLeafletMap()
    return
  }

  const query = mapSearchQuery.value.trim()
  
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

    if (results.length > 0) {
      const place = results[0]
      const lat = parseFloat(place.lat).toFixed(6)
      const lon = parseFloat(place.lon).toFixed(6)

      map.setView([lat, lon], 16)
      marker.setLatLng([lat, lon])

      formLead.value.coordinates = `${lat},${lon}`
      
      const cleanedAddress = cleanAddress(place.display_name, formLead.value.property)
      formLead.value.address = cleanedAddress

      console.log('Original:', place.display_name)
      console.log(' Cleaned:', cleanedAddress)

      showToast('success', 'Lokasi ditemukan!')
      mapSearchQuery.value = ''
    } else {
      showToast('warning', '⚠️ Lokasi tidak ditemukan')
    }
  } catch (error) {
    console.error('❌ Error:', error)
    showToast('error', 'Gagal mencari lokasi')
  }
}

const reverseGeocode = async (lat, lng) => {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`
    )
    const result = await response.json()

    if (result && result.display_name) {
      const cleanedAddress = cleanAddress(result.display_name, formLead.value.property)
      formLead.value.address = cleanedAddress
      
      console.log('Original address :', result.display_name)
      console.log('Cleaned address :', cleanedAddress)
    }
  } catch (error) {
    console.error('(!) Reverse geocode error :', error)
  }
}

watch(
  [showEditModal, showInputModal, showFollowUpModal, activeDragTab, () => formActivity.value.meeting_type],
  async ([leadOpen, inputOpen, followUpOpen, activeTab, meetingType]) => {
    if (leadOpen) {
      console.log('👀 Edit modal opened')
      await nextTick()
      setTimeout(() => {
        initLeafletMap()
      }, 400)
    }
    
    if (followUpOpen && activeTab === 'meeting' && meetingType === 'Visit Meeting') {
      console.log('🗺️ Follow Up Modal - Meeting with Visit Meeting')
      await nextTick()
      setTimeout(() => {
        initMeetingMap()
      }, 800)
    }
    
    if (inputOpen && activityTab.value === 'meeting' && meetingType === 'Visit Meeting') {
      console.log('🗺️ Input Modal - Meeting with Visit Meeting')
      await nextTick()
      setTimeout(() => {
        initMeetingMap()
      }, 800)
    }
  }
)

watch(() => formOnboarding.value.end_time, (newEndTime) => {
  if (newEndTime && newEndTime !== "") {
    formOnboarding.value.status = 'Done';
  } else {
    formOnboarding.value.status = 'On Progress';
  }
});

// =======================================================================
// MEETING MAP
// =======================================================================
const meetingMapContainer = ref(null)
const meetingSearchQuery = ref('')

let meetingMap = null
let meetingMarker = null

const initMeetingMap = async (retryCount = 0) => {
  await nextTick()

  if (!meetingMapContainer.value) {
    if (retryCount < 3) {
      console.warn(`⏳ MeetingMapContainer belum ada, retry ${retryCount + 1}/3...`)
      setTimeout(() => {
        initMeetingMap(retryCount + 1)
      }, 300)
      return
    } else {
      console.error('❌ MeetingMapContainer tidak ditemukan setelah 3x retry')
      return
    }
  }

  if (meetingMap) {
    meetingMap.remove()
    meetingMap = null
  }

  let lat = -7.797068
  let lng = 110.370529
  
  if (formActivity.value.coordinates) {
    const coords = formActivity.value.coordinates.split(',')
    if (coords.length === 2) {
      lat = parseFloat(coords[0].trim())
      lng = parseFloat(coords[1].trim())
    }
  }

  console.log('🗺️ Inisialisasi Meeting Map...', lat, lng)

  meetingMap = L.map(meetingMapContainer.value).setView([lat, lng], 14)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
  }).addTo(meetingMap)

  meetingMarker = L.marker([lat, lng], { draggable: true }).addTo(meetingMap)

  meetingMarker.on('dragend', () => {
    const pos = meetingMarker.getLatLng()
    updateMeetingLocation(pos.lat, pos.lng)
  })

  meetingMap.on('click', (e) => {
    meetingMarker.setLatLng(e.latlng)
    updateMeetingLocation(e.latlng.lat, e.latlng.lng)
  })

  setTimeout(() => {
    meetingMap.invalidateSize()
    console.log('✅ Meeting Map ready!')
  }, 300)
}

const updateMeetingLocation = async (lat, lng) => {
  formActivity.coordinates = `${lat.toFixed(6)},${lng.toFixed(6)}`

  const res = await fetch(
    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
  )
  const data = await res.json()

  if (data?.display_name) {
    formActivity.location = data.display_name
  }
}

const searchMeetingLocation = async () => {
  if (!meetingMap || !meetingMarker) return

  const q = meetingSearchQuery.value.trim()
  if (!q) return

  const res = await fetch(
    `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&limit=1`
  )
  const data = await res.json()

  if (!data.length) return

  const lat = parseFloat(data[0].lat)
  const lng = parseFloat(data[0].lon)

  meetingMap.setView([lat, lng], 16)
  meetingMarker.setLatLng([lat, lng])
  updateMeetingLocation(lat, lng)

  meetingSearchQuery.value = ''
}

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

    formLead.address = place.formatted_address;
    formLead.latitude = place.geometry.location.lat();
    formLead.longitude = place.geometry.location.lng();
  });
});

</script>

<template>
  <MainLayout>
    <div class="pipeline-container">
      <div class="pipeline-header">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Leads Pipeline</h1>
          <p class="text-sm text-gray-600 mt-1">Geser kartu untuk memproses. Double klik kartu untuk detail.</p>
        </div>
      </div>

      <div class="pipeline-board">
        <!-- Lead Generation Column -->
      <!-- Lead Generation Column -->
      <div class="min-w-[320px] bg-white rounded-2xl p-4 flex flex-col gap-3 h-full shadow-sm border border-gray-100">
        <div class="flex justify-between items-center px-2">
          <h3 class="font-bold text-gray-900 text-lg">Lead Generation</h3>
          <div class="flex items-center gap-2">
            <button @click="openModal()" class="gp-btn-primary p-2 rounded-lg shadow-sm transition-all hover:shadow-md">
              <Plus :size="18" />
            </button>
            <span class="gp-badge">{{ leadsGenInbound.length + leadsGenOutbound.length }}</span>
          </div>
        </div>
        
        <!-- Inbound Section -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 p-3 rounded-xl border border-blue-200/50 flex-1 flex flex-col">
          <div class="flex justify-between items-center mb-3">
            <h4 class="text-xs font-bold text-blue-700 uppercase tracking-wide">Inbound</h4>
            <span class="text-[10px] font-bold bg-blue-600 text-white px-2.5 py-1 rounded-full shadow-sm">{{ leadsGenInbound.length }}</span>
          </div>
          <draggable 
            v-model="leadsGenInbound" 
            :group="{ name: 'gen', pull: 'followup', put: false }"
            item-key="lead_id" 
            class="flex-1 flex flex-col gap-2.5 min-h-[50px]"
          >
            <template #item="{element}">
              <div @dblclick="openDetailModal(element)" class="gp-card group">
                <div class="gp-card-actions">
                  <button @click.stop="openModal(element)" class="text-blue-600 hover:bg-blue-50 p-1.5 rounded-lg transition-all">
                    <Edit :size="14" />
                  </button>
                  <button @click.stop="deleteLead(element.lead_id)" class="text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-all">
                    <Trash2 :size="14" />
                  </button>
                </div>
                <div class="font-bold text-gray-900 text-sm mb-1.5 pr-12 line-clamp-2">{{ element.property }}</div>
                <div class="text-xs font-semibold text-blue-600 mb-2">{{ element.source }}</div>
                <div class="text-xs text-gray-600 flex items-center gap-1.5">
                  <User :size="12" class="text-gray-400" /> 
                  <span class="font-medium">{{ element.gp_pic }}</span>
                </div>
              </div>
            </template>
          </draggable>  
        </div>

        <!-- Outbound Section -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100/50 p-3 rounded-xl border border-orange-200/50 flex-1 flex flex-col mt-2">
          <div class="flex justify-between items-center mb-3">
            <h4 class="text-xs font-bold text-orange-700 uppercase tracking-wide">Outbound</h4>
            <span class="text-[10px] font-bold bg-orange-600 text-white px-2.5 py-1 rounded-full shadow-sm">{{ leadsGenOutbound.length }}</span>
          </div>
          <draggable 
            v-model="leadsGenOutbound" 
            :group="{ name: 'gen', pull: 'followup', put: false }"
            item-key="lead_id" 
            class="flex-1 flex flex-col gap-2.5 min-h-[50px]"
          >
            <template #item="{element}">
              <div @dblclick="openDetailModal(element)" class="gp-card group">
                <div class="gp-card-actions">
                  <button @click.stop="openModal(element)" class="text-blue-600 hover:bg-blue-50 p-1.5 rounded-lg transition-all">
                    <Edit :size="14" />
                  </button>
                  <button @click.stop="deleteLead(element.lead_id)" class="text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-all">
                    <Trash2 :size="14" />
                  </button>
                </div>
                <div class="font-bold text-gray-900 text-sm mb-1.5 pr-12 line-clamp-2">{{ element.property }}</div>
                <div class="text-xs font-semibold text-orange-600 mb-2">{{ element.source }}</div>
                <div class="text-xs text-gray-600 flex items-center gap-1.5">
                  <User :size="12" class="text-gray-400" /> 
                  <span class="font-medium">{{ element.gp_pic }}</span>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- Follow Up Column -->
      <div class="min-w-[300px] bg-white rounded-2xl p-4 flex flex-col h-full shadow-sm border border-gray-100">
        <h3 class="font-bold text-gray-900 px-2 mb-3 flex justify-between items-center text-lg">
          Follow Up 
          <span class="gp-badge bg-yellow-500">{{ leadsFollowUp.length }}</span>
        </h3>
        <draggable
          v-model="leadsFollowUp"
          :group="{ name: 'followup', pull: 'quotation', put: ['gen'] }"
          item-key="lead_id"
          class="flex-1 flex flex-col gap-2.5 min-h-[100px]"
          @change="onChangeFollowUp"
        >
          <template #item="{element}">
            <div @dblclick="openActivityModal(element, 'followup')" class="gp-card border-l-4 border-yellow-400 hover:border-yellow-500">
              <div class="font-bold text-gray-900 text-sm mb-1.5 line-clamp-2">{{ element.property }}</div>
              <div class="text-xs font-semibold mb-2" :class="inboundSources.includes(element.source) ? 'text-blue-600' : 'text-orange-600'">
                {{ element.source }}
              </div>
              <div class="text-xs text-gray-600 flex items-center gap-1.5 mb-3">
                <User :size="10" class="text-gray-400" /> 
                <span class="font-medium">{{ element.gp_pic }}</span>
              </div>
              
              <div class="mt-3 pt-3 border-t border-gray-100 flex justify-center">
                <button @click.stop="openAddNewTaskModal(element, 'followup', 'Follow Up')" class="gp-btn-secondary w-full">
                  <Plus :size="12"/> Add New Task
                </button>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Quotation Column -->
      <div class="min-w-[300px] bg-white rounded-2xl p-4 flex flex-col h-full shadow-sm border border-gray-100">
        <h3 class="font-bold text-gray-900 px-2 mb-3 flex justify-between items-center text-lg">
          Quotation 
          <span class="gp-badge bg-purple-500">{{ leadsQuotation.length }}</span>
        </h3>
        <draggable
          v-model="leadsQuotation"
          :group="{ name: 'quotation', pull: 'deals', put: ['followup'] }"
          item-key="lead_id"
          class="flex-1 flex flex-col gap-2.5 min-h-[100px]"
          @change="onChangeQuotation"
        >
          <template #item="{element}">
            <div @dblclick="openActivityModal(element, 'quotation')" class="gp-card border-l-4 border-purple-400 hover:border-purple-500">
              <div class="font-bold text-gray-900 text-sm mb-1.5 line-clamp-2">{{ element.property }}</div>
              <div class="text-xs font-semibold mb-2" :class="inboundSources.includes(element.source) ? 'text-blue-600' : 'text-orange-600'">
                {{ element.source }}
              </div>
              <div class="text-xs text-gray-600 flex items-center gap-1.5 mb-3">
                <User :size="10" class="text-gray-400" /> 
                <span class="font-medium">{{ element.gp_pic }}</span>
              </div>
              
              <div class="mt-3 pt-3 border-t border-gray-100 flex justify-center">
                <button @click.stop="openManualQuotation(element)" class="gp-btn-secondary w-full text-purple-600 hover:bg-purple-50">
                  <Plus :size="12"/> Add New Task
                </button>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Deals Column -->
      <div class="min-w-[300px] bg-white rounded-2xl p-4 flex flex-col h-full shadow-sm border border-gray-100">
        <h3 class="font-bold text-gray-900 px-2 mb-3 flex justify-between items-center text-lg">
          Deals 
          <span class="gp-badge bg-green-500">{{ leadsDeals.length }}</span>
        </h3>
        <draggable
          v-model="leadsDeals"
          :group="{ name: 'deals', pull: 'onboarding', put: ['quotation'] }"
          item-key="lead_id"
          class="flex-1 flex flex-col gap-2.5 min-h-[100px]"
          @change="onChangeDeals"
        >
          <template #item="{element}">
            <div @dblclick="openDealDetailModal(element)" class="gp-card border-l-4 border-green-500 hover:border-green-600 group">
              <div class="gp-card-actions">
                <button @click.stop="openDealDetailModal(element)" class="text-green-600 hover:bg-green-50 p-1.5 rounded-lg transition-all">
                  <Edit :size="14" />
                </button>
              </div>
              <div class="font-bold text-gray-900 text-sm mb-1.5 pr-12 line-clamp-2">{{ element.property }}</div>
              <div class="text-xs text-gray-600 mb-2 font-medium">{{ element.source }}</div>
              <div class="text-xs text-gray-600 flex items-center gap-1.5">
                <User :size="10" class="text-gray-400" /> 
                <span class="font-medium">{{ element.gp_pic }}</span>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Onboarding Column -->
      <div class="min-w-[300px] bg-white rounded-2xl p-4 flex flex-col h-full shadow-sm border border-gray-100">
        <h3 class="font-bold text-gray-900 px-2 mb-3 flex justify-between items-center text-lg">
          Onboarding
          <span class="gp-badge bg-blue-500">{{ leadsOnboarding.length }}</span>
        </h3>
        <draggable
          v-model="leadsOnboarding"
          :group="{ name: 'onboarding', pull: 'retention', put: ['deals'] }"
          item-key="lead_id"
          class="flex-1 flex flex-col gap-2.5 overflow-y-auto pr-1"
          @change="(e) => updateStatus(e, 'onboarding')"
        >
          <template #item="{element}">
            <div @dblclick="openOnboardingModal(element)" class="gp-card border-l-4 border-blue-400 hover:border-blue-500 cursor-pointer">
              <div class="font-bold text-gray-900 text-sm mb-2 line-clamp-2">{{ element.property }}</div>
              
              <div class="space-y-2">
                <!-- Source Badge -->
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-semibold px-2 py-0.5 rounded-md" :class="inboundSources.includes(element.source) ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'">
                    {{ element.source }}
                  </span>
                </div>
                
                <!-- PIC Info -->
                <div class="text-xs text-gray-600 flex items-center gap-1.5">
                  <User :size="11" class="text-gray-400" /> 
                  <span class="font-medium">{{ element.gp_pic }}</span>
                </div>
                
                <!-- Date Info -->
                <div class="text-xs text-gray-500 flex items-center gap-1.5">
                  <Calendar :size="11" class="text-gray-400" /> 
                  <span>{{ element.date_in }}</span>
                </div>
                
                <!-- Status Indicator -->
                <div class="pt-2 mt-2 border-t border-gray-100">
                  <div class="flex items-center justify-between">
                    <span class="text-[10px] font-bold text-blue-600 uppercase tracking-wide">In Progress</span>
                    <div class="flex gap-1">
                      <div class="w-1.5 h-1.5 rounded-full bg-blue-400"></div>
                      <div class="w-1.5 h-1.5 rounded-full bg-blue-400"></div>
                      <div class="w-1.5 h-1.5 rounded-full bg-gray-300"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </draggable>
      </div>

      <!-- Retention Column -->
      <div class="min-w-[300px] bg-white rounded-2xl p-4 flex flex-col h-full shadow-sm border border-gray-100">
        <h3 class="font-bold text-gray-900 px-2 mb-3 text-lg">Retention</h3>
        <draggable
          v-model="leadsRetention"
          :group="{ name: 'retention', pull: false, put: ['onboarding'] }"
          item-key="lead_id"
          class="flex-1 flex flex-col gap-2.5"
          @change="(e) => updateStatus(e, 'retention')"
        >
          <template #item="{element}">
            <div class="gp-card border-l-4 border-pink-400">
              <div class="font-bold text-gray-900 text-sm">{{ element.property }}</div>
            </div>
          </template>
        </draggable>
      </div>
      </div>
    </div>

    <!-- All Modals remain exactly the same structure, just updating button styles -->
    <!-- Edit/Add Lead Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4 overflow-y-auto">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl my-8 relative animate-fade-in-up">
          <div class="sticky top-0 bg-white p-6 border-b z-10 flex justify-between items-center rounded-t-2xl">
            <h3 class="text-2xl font-bold text-gray-900">{{ isEditing ? 'Edit Data Lead' : 'Tambah Lead Baru' }}</h3>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
              <X :size="24" />
            </button>
          </div>
          <form @submit.prevent="handleGenericSubmit" class="p-6 space-y-6 max-h-[calc(90vh-140px)] overflow-y-auto">
            <div class="bg-gradient-to-br from-gray-50 to-gray-100/50 p-5 rounded-xl border border-gray-200">
              <h4 class="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wide">Informasi Properti</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="md:col-span-2">
                  <label class="gp-label">Nama Properti</label>
                  <input v-model="formLead.property" type="text" class="gp-input" required>
                </div>
                
                <div>
                  <label class="gp-label">Source</label>
                  <select v-model="formLead.source" class="gp-input">
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

                <div v-if="isReferralOrAffiliate" class="md:col-span-2 bg-blue-50 border border-blue-200 p-4 rounded-xl grid grid-cols-2 gap-4 animate-fade-in">
                  <div>
                    <label class="gp-label text-blue-700">{{ referralLabel }}</label>
                    <input v-model="formLead.referral_or_affiliate_by" type="text" class="gp-input border-blue-300 focus:ring-blue-500" placeholder="Nama Pemberi Referensi">
                  </div>
                  <div>
                    <label class="gp-label text-blue-700">Commission Amount</label>
                    <input v-model="formLead.commission_amount" type="text" class="gp-input border-blue-300 focus:ring-blue-500" placeholder="e.g. 10% or 500000">
                  </div>
                </div>

                <div>
                  <label class="gp-label">Type</label>
                  <input v-model="formLead.type" type="text" class="gp-input">
                </div>
                <div>
                  <label class="gp-label">GuestPro PIC</label>
                  <select v-model="formLead.gp_pic" class="gp-input" required>
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Date In</label>
                  <input v-model="formLead.date_in" type="date" class="gp-input" required>
                </div>
                
                <div class="md:col-span-2">
                  <label class="gp-label">Koordinat (Latitude, Longitude)</label>
                  <input 
                    v-model="formLead.coordinates" 
                    type="text" 
                    class="gp-input font-mono text-sm" 
                    placeholder="contoh: -7.797068, 110.370529"
                    readonly
                  >
                  <p class="text-xs text-gray-500 mt-1.5">💡 Gunakan peta di bawah untuk memilih lokasi</p>
                </div>
                
                <!-- MAP SECTION -->
                <div class="md:col-span-2">
                  <label class="gp-label">Alamat Lengkap</label>
                  
                  <div class="flex gap-2 mb-3">
                    <input
                      v-model="mapSearchQuery"
                      type="text"
                      class="gp-input flex-1"
                      placeholder="Cari lokasi (contoh: Bandara Ngurah Rai)"
                      @keyup.enter="searchLocation"
                    />
                    <button 
                      type="button" 
                      @click="searchLocation" 
                      class="gp-btn-primary px-5"
                    >
                      Cari
                    </button>
                  </div>

                  <div
                    ref="mapContainer"
                    class="w-full h-64 rounded-xl border-2 border-gray-200 mb-3 overflow-hidden shadow-inner"
                  ></div>

                  <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-200">
                    <div class="flex items-start gap-3">
                      <div class="flex-1 space-y-2">
                        <div class="flex items-center gap-2">
                          <span class="text-xs font-bold text-gray-600 uppercase">Koordinat:</span>
                          <span class="font-mono text-sm text-gray-900 bg-white px-3 py-1 rounded-lg border shadow-sm">
                            {{ formLead.coordinates || 'Belum dipilih' }}
                          </span>
                        </div>
                        <div class="flex items-start gap-2">
                          <span class="text-xs font-bold text-gray-600 uppercase shrink-0">Alamat:</span>
                          <span class="text-sm text-gray-700 font-medium">
                            {{ formLead.address || 'Klik/drag marker atau search untuk memilih lokasi' }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-3">
                    <label class="gp-label">Edit Alamat Manual (Opsional)</label>
                    <textarea 
                      v-model="formLead.address" 
                      rows="2" 
                      class="gp-input text-sm" 
                      placeholder="Atau ketik/edit alamat manual di sini..."
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>

            <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div class="bg-gradient-to-r from-gray-100 to-gray-50 px-5 py-3 border-b border-gray-200 flex justify-between items-center">
                <h4 class="text-sm font-bold text-gray-700 uppercase tracking-wide">Daftar PIC</h4>
                <button type="button" @click="addPicRowEdit" class="gp-btn-primary text-sm">
                  <Plus :size="14"/> Tambah PIC
                </button>
              </div>
              <div class="p-4 space-y-3 max-h-64 overflow-y-auto bg-gray-50">
                <div v-for="(pic, index) in formLead.pics" :key="index" class="flex gap-2 items-start bg-white p-3 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-2 flex-1">
                    <input v-model="pic.pic_name" type="text" class="gp-input-sm" placeholder="Nama PIC" required>
                    <input v-model="pic.phone_number" type="text" class="gp-input-sm" placeholder="No HP">
                    <input v-model="pic.whatsapp" type="text" class="gp-input-sm" placeholder="WhatsApp">
                    <input v-model="pic.email" type="email" class="gp-input-sm" placeholder="Email">
                  </div>
                  <button type="button" @click="removePicRowEdit(index)" class="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-all mt-0.5">
                    <Trash2 :size="16" />
                  </button>
                </div>
              </div>
            </div>
          </form>

          <div class="sticky bottom-0 pt-4 px-6 pb-6 flex justify-end gap-3 border-t bg-white rounded-b-2xl z-20">
            <button type="button" @click="closeModal" class="gp-btn-secondary">
              Batal
            </button>
            <button type="submit" @click="handleGenericSubmit" class="gp-btn-primary">
              <Save :size="16" /> Simpan
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Detail Modal -->
    <Teleport to="body">
      <div v-if="showDetailModal && selectedLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl relative animate-fade-in-up overflow-hidden">
          <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-5 border-b flex justify-between items-start">
            <div>
              <h2 class="text-2xl font-bold text-gray-900">{{ selectedLead.property }}</h2>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs bg-gray-200 text-gray-700 px-3 py-1 rounded-full font-semibold">{{ selectedLead.type }}</span>
              </div>
            </div>
            <button @click="closeDetailModal" class="text-gray-400 hover:text-gray-600 bg-white rounded-full p-2 shadow-sm transition-all hover:shadow-md">
              <X :size="20" />
            </button>
          </div>
          <div class="p-6 overflow-y-auto max-h-[80vh]">
            <div class="grid grid-cols-2 gap-6 mb-6">
              <div class="space-y-4">
                <div>
                  <label class="gp-label-detail">Source</label>
                  <p class="text-sm font-semibold text-gray-900">{{ selectedLead.source }}</p>
                </div>
                <div>
                  <label class="gp-label-detail">Address</label>
                  <p class="text-sm font-medium text-gray-700 flex items-start gap-2">
                    <MapPin :size="14" class="mt-0.5 text-gray-400" /> 
                    {{ selectedLead.address || '-' }}
                  </p>
                </div>
              </div>
              <div class="space-y-4">
                <div>
                  <label class="gp-label-detail">GuestPro PIC</label>
                  <p class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                    <User :size="14" class="text-gray-400" /> 
                    {{ selectedLead.gp_pic }}
                  </p>
                </div>
                <div>
                  <label class="gp-label-detail">Date In</label>
                  <p class="text-sm font-medium text-gray-700 flex items-center gap-2">
                    <Calendar :size="14" class="text-gray-400" /> 
                    {{ selectedLead.date_in }}
                  </p>
                </div>
                <div>
                  <label class="gp-label-detail">Koordinat</label>
                  <p class="text-xs font-mono text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg inline-block">
                    {{ selectedLead.coordinates || '-' }}
                  </p>
                </div>
              </div>
            </div>
            <div class="border border-gray-200 rounded-xl overflow-hidden shadow-sm">
              <div class="bg-gradient-to-r from-gray-100 to-gray-50 px-4 py-3 border-b text-xs font-bold text-gray-700 uppercase tracking-wide">
                Daftar Contact Person (PIC)
              </div>
              <table class="w-full text-sm">
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="pic in selectedLead.pics" :key="pic.id" class="hover:bg-gray-50 transition-colors">
                    <td class="p-4 font-semibold text-gray-900">{{ pic.pic_name }}</td>
                    <td class="p-4 text-gray-600 font-medium">{{ pic.phone_number }}</td>
                    <td class="p-4 text-green-600 font-semibold">
                      <a
                        v-if="pic.whatsapp"
                        :href="`https://wa.me/${formatWhatsapp(pic.whatsapp)}`"
                        target="_blank"
                        rel="noopener"
                        class="hover:underline"
                      >
                        {{ pic.whatsapp }}
                      </a>
                      <span v-else>-</span>
                    </td>
                    <td class="p-4 text-blue-600 font-medium">{{ pic.email }}</td>
                  </tr>
                  <tr v-if="!selectedLead.pics || selectedLead.pics.length === 0">
                    <td colspan="4" class="p-6 text-center text-gray-400 italic bg-gray-50">
                      Tidak ada data PIC
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="bg-gray-50 p-4 border-t flex justify-end">
            <button @click="closeDetailModal" class="gp-btn-secondary">
              Tutup
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Deal Modal -->
    <Teleport to="body">
      <div v-if="showDealModal" class="fixed inset-0 z-[130] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl relative animate-fade-in-up max-h-[90vh] overflow-y-auto">
          <div class="bg-gradient-to-r from-green-600 to-green-700 p-6 border-b rounded-t-2xl flex justify-between items-center sticky top-0 z-10">
            <h3 class="font-bold text-white text-xl flex items-center gap-3">
              <Briefcase :size="24"/> New Deal Closing
            </h3>
            <button @click="cancelMoveDeal" class="text-white hover:text-green-200 transition-colors">
              <X :size="24"/>
            </button>
          </div>
          
          <div class="p-6 space-y-6">
            <div class="bg-gradient-to-br from-green-50 to-green-100/50 p-5 rounded-xl border-2 border-green-200 flex items-center gap-4 shadow-sm">
              <div class="bg-green-600 p-3 rounded-xl shadow-md">
                <MapPin class="text-white" :size="24"/>
              </div>
              <div>
                <div class="text-xs text-green-700 font-bold uppercase tracking-wide">Property Name</div>
                <div class="text-xl font-bold text-gray-900 mt-1">{{ draggedItem?.property }}</div>
              </div>
            </div>

            <div>
              <label class="label">Deal By</label>
              <select v-model="formDeal.deal_by" class="gp-input">
                <option v-for="dby in picList" :key="dby">{{ dby }}</option>
              </select>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label class="gp-label">Deal Type</label>
                <select v-model="formDeal.deal_type" class="gp-input">
                  <option v-for="dtype in dealTypes" :key="dtype">{{ dtype }}</option>
                </select>
              </div>
              <div>
                <label class="gp-label">Total Rooms</label>
                <input v-model="formDeal.room" type="number" class="gp-input">
              </div>
              
              <div class="md:col-span-2">
                <label class="gp-label">PIC Lead (Invoice Recipient)</label>
                <select v-model="formDeal.pic_lead" class="gp-input">
                  <option :value="null">-- Pilih PIC Lead --</option>
                  <option v-for="pic in draggedItem?.pics" :key="pic.id" :value="pic.id">{{ pic.pic_name }} - {{ pic.phone_number }}</option>
                </select>
              </div>
              <div class="md:col-span-2"><label class="label">Notes</label><textarea v-model="formDeal.notes" rows="2" class="input"></textarea></div>
            </div>

            <div class="border rounded-lg overflow-hidden border-blue-200">
              <div class="bg-blue-50 px-4 py-2 border-b border-blue-200 flex justify-between items-center">
                <h4 class="text-sm font-bold text-blue-800 uppercase flex items-center gap-2"><Package :size="16"/> Product & Packages</h4>
                <button type="button" @click="addDealProductRow" class="text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 flex items-center gap-1"><Plus :size="12"/> Add Product</button>
              </div>
              <div class="p-4 bg-white space-y-3">
                <div v-if="formDeal.products.length === 0" class="text-center text-gray-400 italic text-sm py-2">Belum ada produk dipilih.</div>
                
                <div v-for="(detail, index) in formDeal.products" :key="'prod-'+index" class="bg-gray-50 p-3 rounded border shadow-sm relative">
                  <button type="button" @click="removeDealProductRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-2">
                    <div>
                        <label class="label">Package Name</label>
                        <select v-model="detail.package" class="gp-input-sm" @change="detail.product = ''">
                            <option value="" disabled>-- Select --</option>
                            <option v-for="pkg in getAvailablePackages(index)" :key="pkg" :value="pkg">{{ pkg }}</option>
                            <option v-if="detail.package && !getAvailablePackages(index).includes(detail.package)" :value="detail.package">{{ detail.package }}</option>
                        </select>
                    </div>
                    <div>
                        <label class="label">Product(s)</label>
                        <select v-model="detail.product" class="gp-input-sm" :disabled="!detail.package">
                            <option value="" disabled>-- Select --</option>
                            <option v-for="prod in getProductsForPackage(detail.package)" :key="prod" :value="prod">{{ prod }}</option>
                        </select>
                    </div>
                    <div>
                      <label class="gp-label">Product Amount</label>
                      <div class="flex gap-2">
                        <input v-model="detail.amount" type="number" class="gp-input-sm">
                        <select v-model="detail.cycle" class="gp-input-sm w-24"><option>Month</option><option>Year</option><option>One-time</option></select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="border rounded-lg overflow-hidden border-green-200">
              <div class="bg-green-50 px-4 py-2 border-b border-green-200 flex justify-between items-center">
                <h4 class="text-sm font-bold text-green-800 uppercase flex items-center gap-2"><Settings :size="16"/> Initiation</h4>
                <button type="button" @click="addDealInitiationRow" class="text-xs bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700 flex items-center gap-1"><Plus :size="12"/> Add Initiation</button>
              </div>
              <div class="p-4 bg-white space-y-3">
                <div v-if="formDeal.initiations.length === 0" class="text-center text-gray-400 italic text-sm py-2">Belum ada initiation dipilih.</div>

                <div v-for="(detail, index) in formDeal.initiations" :key="'init-'+index" class="bg-gray-50 p-3 rounded border shadow-sm relative">
                  <button type="button" @click="removeDealInitiationRow(index)" class="absolute top-2 right-2 text-red-400 hover:text-red-600"><Trash2 :size="16"/></button>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
                    
                    <div>
                        <label class="gp-label">Initiation (Service)</label>
                        <select v-model="detail.product" class="gp-input-sm">
                            <option value="" disabled>-- Select Service --</option>
                            <option v-for="opt in initiationOptions" :key="opt" :value="opt">{{ opt }}</option>
                        </select>
                    </div>
                    
                    <div>
                      <label class="gp-label">Initiation Amount</label>
                      <div class="relative">
                        <input v-model="detail.amount" type="number" class="gp-input-sm pr-20">
                        <span class="absolute right-3 top-2 text-[10px] font-bold text-gray-400 bg-gray-100 px-1 rounded">
                            One-time
                        </span>
                      </div>
                    </div>

                  </div>
                </div>
              </div>
            </div>

          </div>

          <div class="p-6 border-t bg-gray-50 flex justify-end gap-3 sticky bottom-0 z-10">
            <button @click="cancelMoveDeal" class="gp-btn-secondary">
              Batal
            </button>
            <button @click="saveDeal" class="gp-btn-primary bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800">
              <Save :size="18"/> Simpan Deal
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Follow Up Modal -->
    <Teleport to="body">
      <div v-if="showFollowUpModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto relative animate-fade-in-up flex flex-col">
          <form @submit.prevent="saveDragForm" class="flex flex-col h-full">
            <div class="bg-white p-6 border-b z-10 flex justify-between items-center rounded-t-2xl">
              <div>
                <h2 class="text-2xl font-bold text-gray-900">
                  {{ modalMode === 'drag' ? 'Proses ke Follow Up' : 'Add New Task' }}
                </h2>
                <p class="text-sm text-gray-600 mt-1">
                  {{ modalMode === 'drag' ? `Pilih aktivitas pertama untuk ${draggedItem?.property}.` : `Tambahkan aktivitas baru untuk ${draggedItem?.property}.` }}
                </p>
              </div>
              <button type="button" @click="cancelMove" class="text-gray-400 hover:text-gray-600 transition-colors">
                <X :size="24" />
              </button>
            </div>
            
            <div class="px-6 pt-4 pb-0">
              <div class="flex gap-2 bg-gray-100 p-1.5 rounded-xl overflow-x-auto shadow-inner">
                <button type="button" @click="activeDragTab = 'followup'" class="flex-1 py-2.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'followup' ? 'bg-white text-blue-600 shadow-md' : 'text-gray-500 hover:bg-gray-200'">
                  Form Follow Up
                </button>
                <button type="button" @click="activeDragTab = 'meeting'" class="flex-1 py-2.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'meeting' ? 'bg-white text-orange-600 shadow-md' : 'text-gray-500 hover:bg-gray-200'">
                  Form Meeting
                </button>
                <button v-if="modalMode !== 'drag'" type="button" @click="activeDragTab = 'quotation'" class="flex-1 py-2.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap" :class="activeDragTab === 'quotation' ? 'bg-white text-purple-600 shadow-md' : 'text-gray-500 hover:bg-gray-200'">
                  Form Quotation
                </button>
              </div>
            </div>
            
            <div class="p-6 flex-1 overflow-y-auto">
              <div v-if="activeDragTab === 'followup'" class="space-y-4 animate-fade-in">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">PIC GP</label>
                    <select v-model="formActivity.pic_gp" class="gp-input">
                      <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="gp-label">PIC Lead</label>
                    <input v-model="formActivity.pic_lead" type="text" class="gp-input">
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">Date</label>
                    <input v-model="formActivity.date" type="date" class="gp-input">
                  </div>
                  <div>
                    <label class="gp-label">Objective</label>
                    <input v-model="formActivity.objective" type="text" class="gp-input">
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">Start Time</label>
                    <input v-model="formActivity.start_time" type="time" class="gp-input">
                  </div>
                  <div>
                    <label class="gp-label">End Time</label>
                    <input v-model="formActivity.end_time" type="time" class="gp-input">
                  </div>
                </div>
                <div>
                  <label class="gp-label">Type</label>
                  <select v-model="formActivity.fu_type" class="gp-input">
                    <option>Phone Calls/Telephone</option>
                    <option>Texting/Chat</option>
                    <option>Follow up leads</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Notes</label>
                  <textarea v-model="formActivity.notes" rows="4" class="gp-input"></textarea>
                </div>
              </div>
              
              <div v-if="activeDragTab === 'meeting'" class="space-y-4 animate-fade-in">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">PIC GP</label>
                    <select v-model="formActivity.pic_gp" class="gp-input">
                      <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="gp-label">PIC Lead</label>
                    <input v-model="formActivity.pic_lead" type="text" class="gp-input">
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">Date</label>
                    <input v-model="formActivity.date" type="date" class="gp-input">
                  </div>
                  <div>
                    <label class="gp-label">Objective</label>
                    <input v-model="formActivity.objective" type="text" class="gp-input">
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="gp-label">Start Time</label>
                    <input v-model="formActivity.start_time" type="time" class="gp-input">
                  </div>
                  <div>
                    <label class="gp-label">End Time</label>
                    <input v-model="formActivity.end_time" type="time" class="gp-input">
                  </div>
                </div>
                <div>
                  <label class="gp-label">Meeting Type</label>
                  <select v-model="formActivity.meeting_type" class="gp-input">
                    <option>Visit Meeting</option>
                    <option>Online Meeting</option>
                    <option>Office Visit Meeting</option>
                  </select>
                </div>
                <div class="md:col-span-2">
                  <label class="gp-label">Alamat Lengkap</label>
                  
                  <div class="flex gap-2 mb-3">
                    <input
                      v-model="mapSearchQuery"
                      type="text"
                      class="gp-input flex-1"
                      placeholder="Cari lokasi (contoh: Bandara Ngurah Rai)"
                      @keyup.enter="searchLocation"
                    />
                    <button 
                      type="button" 
                      @click="searchLocation" 
                      class="gp-btn-primary px-5"
                    >
                      Cari
                    </button>
                  </div>

                  <div
                    ref="mapContainer"
                    class="w-full h-64 rounded-xl border-2 border-gray-200 mb-3 overflow-hidden shadow-inner"
                  ></div>

                  <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-xl border border-blue-200">
                    <div class="flex items-start gap-3">
                      <div class="flex-1 space-y-2">
                        <div class="flex items-center gap-2">
                          <span class="text-xs font-bold text-gray-600 uppercase">Koordinat:</span>
                          <span class="font-mono text-sm text-gray-900 bg-white px-3 py-1 rounded-lg border shadow-sm">
                            {{ formLead.coordinates || 'Belum dipilih' }}
                          </span>
                        </div>
                        <div class="flex items-start gap-2">
                          <span class="text-xs font-bold text-gray-600 uppercase shrink-0">Alamat:</span>
                          <span class="text-sm text-gray-700 font-medium">
                            {{ formLead.address || 'Klik/drag marker atau search untuk memilih lokasi' }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-3">
                    <label class="gp-label">Edit Alamat Manual (Opsional)</label>
                    <textarea 
                      v-model="formLead.address" 
                      rows="2" 
                      class="gp-input text-sm" 
                      placeholder="Atau ketik/edit alamat manual di sini..."
                    ></textarea>
                  </div>
                </div>
                <div>
                  <label class="gp-label">MOM</label>
                  <textarea v-model="formActivity.mom" rows="4" class="gp-input"></textarea>
                </div>
              </div>

              <div v-if="activeDragTab === 'quotation'" class="space-y-4 animate-fade-in">
                <div>
                  <label class="gp-label">PIC GP</label>
                  <select v-model="formActivity.pic_gp" class="gp-input">
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Date</label>
                  <input v-model="formActivity.date" type="date" class="gp-input">
                </div>
                
                <div>
                  <label class="gp-label">Link Quotation</label>
                  <input 
                    v-model="formActivity.link_quotation" 
                    type="text" 
                    class="gp-input" 
                    placeholder="https://..." 
                    @blur="autoFixUrl(formActivity, 'link_quotation')" 
                    required
                  >
                </div>
                
                <div class="flex items-center gap-3 cursor-pointer bg-green-50 p-4 rounded-xl border-2 border-green-200 hover:bg-green-100 transition-colors" @click="formActivity.is_send = !formActivity.is_send">
                  <CheckSquare :size="22" class="text-green-600" v-if="formActivity.is_send"/>
                  <Square :size="22" class="text-gray-400" v-else/>
                  <span class="text-sm font-semibold text-gray-700">Sudah Terkirim?</span>
                </div>
              </div>
            </div>
            
            <div class="p-6 border-t bg-gray-50 flex justify-end gap-3 mt-auto sticky bottom-0">
              <button type="button" @click="cancelMove" class="gp-btn-secondary">
                Batal
              </button>
              <button type="submit" class="gp-btn-primary shadow-lg" :class="{
                'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800': activeDragTab === 'followup',
                'bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800': activeDragTab === 'meeting',
                'bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800': activeDragTab === 'quotation'
              }">
                <Save :size="18" /> 
                {{ activeDragTab === 'followup' ? 'Simpan Follow Up' : (activeDragTab === 'meeting' ? 'Simpan Meeting' : 'Simpan Quotation') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Quotation Modal -->
    <Teleport to="body">
      <div v-if="showQuotationModal" class="fixed inset-0 z-[120] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg relative animate-fade-in-up">
          <div class="bg-white p-6 border-b rounded-t-2xl flex justify-between items-center">
            <h3 class="font-bold text-gray-900 text-xl flex items-center gap-3">
              <span class="w-1.5 h-8 bg-purple-500 rounded-full inline-block"></span> 
              Input Quotation
            </h3>
            <button @click="cancelMoveQuotation" class="text-gray-400 hover:text-gray-600 transition-colors">
              <X :size="24"/>
            </button>
          </div>
          <div class="p-6">
            <form @submit.prevent="saveQuotationInitial" class="space-y-5">
              <div class="bg-gradient-to-r from-purple-50 to-purple-100/50 p-4 rounded-xl text-sm text-purple-800 border-2 border-purple-200">
                <strong class="font-bold">Property:</strong> {{ draggedItem?.property }}
              </div>
              <div>
                <label class="gp-label">PIC GP</label>
                <select v-model="formQuotationInitial.pic_gp" class="gp-input">
                  <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                </select>
              </div>
              <div>
                <label class="gp-label">Date</label>
                <input v-model="formQuotationInitial.date" type="date" class="gp-input" required>
              </div>
              
              <div>
                <label class="gp-label">Link Quotation</label>
                <input 
                  v-model="formQuotationInitial.link_quotation" 
                  type="text" 
                  class="gp-input" 
                  placeholder="https://..." 
                  @blur="autoFixUrl(formQuotationInitial, 'link_quotation')" 
                  required
                >
              </div>

              <div class="flex items-center gap-3 cursor-pointer bg-green-50 p-4 rounded-xl border-2 border-green-200 hover:bg-green-100 transition-colors" @click="formQuotationInitial.is_send = !formQuotationInitial.is_send">
                <CheckSquare :size="22" class="text-green-600" v-if="formQuotationInitial.is_send"/>
                <Square :size="22" class="text-gray-400" v-else/>
                <span class="text-sm font-semibold text-gray-700">Sudah Terkirim?</span>
              </div>

              <div class="pt-4 flex justify-end gap-3 border-t mt-6">
                <button type="button" @click="cancelMoveQuotation" class="gp-btn-secondary">
                  Batal
                </button>
                <button type="submit" class="gp-btn-primary bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800">
                  <Save :size="18"/> Simpan
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Activity Modal -->
    <Teleport to="body">
      <div v-if="showActivityModal && selectedActivityLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[85vh] flex flex-col overflow-hidden relative animate-fade-in-up">
          <div class="bg-gradient-to-r from-slate-50 to-gray-100 p-6 border-b shrink-0">
            <div class="flex justify-between items-start mb-5">
              <div>
                <h2 class="text-3xl font-bold text-gray-900">{{ selectedActivityLead.property }}</h2>
                <div class="flex items-center gap-2 mt-3">
                  <span class="text-xs bg-gray-200 text-gray-800 px-3 py-1.5 rounded-full font-bold shadow-sm">{{ selectedActivityLead.source }}</span>
                  <span class="text-xs border-2 border-gray-300 text-gray-700 px-3 py-1.5 rounded-full font-semibold">{{ selectedActivityLead.type }}</span>
                </div>
              </div>
              <button @click="showActivityModal = false" class="text-gray-400 hover:text-red-500 bg-white p-2 rounded-xl shadow-md transition-all hover:shadow-lg">
                <X :size="24"/>
              </button>
            </div>

            <div class="grid grid-cols-4 gap-6 text-sm text-gray-600 bg-white p-5 rounded-xl border-2 border-gray-200 shadow-sm mb-4">
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Alamat</span>
                <span class="flex items-start gap-2 font-semibold text-gray-900">
                  <MapPin :size="14" class="mt-0.5 text-gray-500"/> 
                  {{ selectedActivityLead.address || '-' }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Koordinat</span>
                <span class="font-mono bg-gray-100 px-3 py-1 rounded-lg text-xs font-semibold">
                  {{ selectedActivityLead.coordinates || '-' }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">PIC GuestPro</span>
                <span class="flex items-center gap-2 font-semibold text-gray-900">
                  <User :size="14" class="text-gray-500"/> 
                  {{ selectedActivityLead.gp_pic }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Tgl Masuk</span>
                <span class="flex items-center gap-2 font-semibold text-gray-900">
                  <CalendarIcon :size="14" class="text-gray-500"/> 
                  {{ selectedActivityLead.date_in }}
                </span>
              </div>
            </div>

            <div class="bg-blue-50 border-2 border-blue-200 rounded-xl overflow-hidden transition-all duration-300 shadow-sm">
              <div @click="showPicList = !showPicList" class="px-5 py-3 flex justify-between items-center cursor-pointer hover:bg-blue-100 transition select-none">
                <span class="text-xs font-bold text-blue-700 uppercase flex items-center gap-2">
                  <User :size="14" /> Daftar PIC Lead ({{ selectedActivityLead.pics.length }})
                </span>
                <ChevronDown :size="16" class="text-blue-600 transition-transform duration-300" :class="showPicList ? 'rotate-180' : ''" />
              </div>
              <div v-if="showPicList" class="border-t-2 border-blue-200 bg-white p-4">
                <div v-if="selectedActivityLead.pics.length === 0" class="text-center text-xs text-gray-400 italic py-4">
                  Tidak ada data PIC.
                </div>
                <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div v-for="pic in selectedActivityLead.pics" :key="pic.id" class="text-xs border-2 border-gray-200 rounded-xl p-3 bg-gray-50 hover:shadow-md transition-shadow">
                    <div class="font-bold text-gray-900 mb-2">{{ pic.pic_name }}</div>
                    <div class="text-gray-600 space-y-1.5">
                      <span v-if="pic.phone_number" class="block">📞 {{ pic.phone_number }}</span>
                      <span v-if="pic.whatsapp" class="block text-green-600 font-semibold">💬 {{ pic.whatsapp }}</span>
                      <span v-if="pic.email" class="block text-blue-600">✉️ {{ pic.email }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex-1 flex flex-col bg-white overflow-hidden">
            <div class="flex justify-between items-center px-6 py-4 border-b-2 bg-white">
              <div class="flex bg-gray-100 p-1.5 rounded-xl shadow-inner">
                <button @click="switchActivityTab('followup')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="activityTab==='followup' ? 'bg-white shadow-md text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Follow Up
                </button>
                <button @click="switchActivityTab('meeting')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="activityTab==='meeting' ? 'bg-white shadow-md text-orange-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Meeting
                </button>
                <button v-if="['quotation', 'deals', 'onboarding', 'retention'].includes(selectedActivityLead?.status_kanban)" @click="switchActivityTab('quotation')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="activityTab==='quotation' ? 'bg-white shadow-md text-purple-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Quotation
                </button>
              </div>
              <button @click="openInputModal(null)" class="gp-btn-primary">
                <Plus :size="16" /> 
                Tambah {{ activityTab === 'followup' ? 'Follow Up' : (activityTab === 'meeting' ? 'Meeting' : 'Quotation') }}
              </button>
            </div>

            <div class="flex-1 overflow-auto p-0">
              <table class="w-full text-left text-sm border-collapse">
                <thead class="bg-gradient-to-r from-gray-100 to-gray-50 text-gray-600 font-bold uppercase text-xs sticky top-0 z-10 shadow-sm">
                  <tr>
                    <th class="p-4 border-b-2 w-40">Tanggal & Waktu</th>
                    <th class="p-4 border-b-2 w-32">PIC GP</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b-2 w-34">Tipe</th>
                    <th v-if="activityTab === 'meeting'" class="p-4 border-b-2 w-40">Lokasi</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b-2 w-48">Objective</th>
                    <th v-if="activityTab !== 'quotation'" class="p-4 border-b-2">{{ activityTab === 'followup' ? 'Notes' : 'MOM' }}</th>
                    <th v-if="activityTab === 'quotation'" class="p-4 border-b-2">Link Document</th>
                    <th v-if="activityTab === 'quotation'" class="p-4 border-b-2 w-24 text-center">Status</th>
                    <th class="p-4 border-b-2 text-center w-24">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in activityList" :key="item.id" class="hover:bg-gray-50 transition-colors">
                    <td class="p-4 align-top">
                      <div class="font-bold text-gray-900">{{ item.date }}</div>
                      <div v-if="activityTab !== 'quotation'" class="text-xs text-gray-500 mt-1 flex items-center gap-1">
                        <Clock :size="12"/> {{ item.start_time?.substring(0,5) }} - {{ item.end_time?.substring(0,5) }}
                      </div>
                    </td>
                    <td class="p-4 align-top text-gray-800 font-semibold">{{ item.pic_gp }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top">
                      <span class="px-3 py-1.5 rounded-lg border-2 text-xs font-bold shadow-sm" :class="activityTab==='followup' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-orange-50 text-orange-700 border-orange-200'">
                        {{ activityTab === 'followup' ? item.fu_type : item.meeting_type }}
                      </span>
                    </td>
                    <td v-if="activityTab === 'meeting'" class="p-4 align-top text-gray-700 font-medium">{{ item.location || '-' }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top font-semibold text-gray-800">{{ item.objective }}</td>
                    <td v-if="activityTab !== 'quotation'" class="p-4 align-top text-gray-600 whitespace-pre-line">{{ activityTab === 'followup' ? item.notes : item.mom }}</td>
                    <td v-if="activityTab === 'quotation'" class="p-4 align-top">
                      <a :href="item.link_quotation" target="_blank" class="text-blue-600 hover:underline flex items-center gap-2 font-medium">
                        <LinkIcon :size="14" class="shrink-0"/> 
                        <span class="truncate max-w-[200px]">{{ item.link_quotation }}</span>
                      </a>
                    </td>
                    <td v-if="activityTab === 'quotation'" class="p-4 align-top text-center">
                      <span class="px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm" :class="item.is_send ? 'bg-green-100 text-green-700 border-2 border-green-200' : 'bg-gray-100 text-gray-600 border-2 border-gray-200'">
                        {{ item.is_send ? 'Terkirim' : 'Draft' }}
                      </span>
                    </td>
                    <td class="p-4 align-top text-center">
                      <div class="flex justify-center gap-2">
                        <button @click="openInputModal(item)" class="text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition-all" title="Edit">
                          <Edit :size="16"/>
                        </button>
                        <button @click="deleteActivityItem(item.id)" class="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-all" title="Hapus">
                          <Trash2 :size="16"/>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="activityList.length === 0">
                    <td :colspan="activityTab === 'meeting' ? 7 : (activityTab === 'quotation' ? 5 : 6)" class="p-12 text-center text-gray-400 italic bg-gray-50/50">
                      Belum ada riwayat aktivitas. Klik tombol "Tambah" di atas.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Input Modal (Activity Detail) -->
    <Teleport to="body">
      <div v-if="showInputModal" class="fixed inset-0 z-[120] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg relative animate-fade-in-up">
          <div class="bg-white p-6 border-b rounded-t-2xl flex justify-between items-center">
            <h3 class="font-bold text-gray-900 text-xl flex items-center gap-3">
              <span class="w-1.5 h-8 bg-lime-500 rounded-full inline-block"></span> 
              {{ isEditingActivity ? 'Edit Data' : 'Input Data Baru' }}
            </h3>
            <button @click="showInputModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <X :size="24"/>
            </button>
          </div>
          <div class="p-6 max-h-[70vh] overflow-y-auto">
            <form @submit.prevent="saveActivityLog" class="space-y-5">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">PIC GP</label>
                  <select v-model="formActivity.pic_gp" class="gp-input">
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div v-if="activityTab !== 'quotation'">
                  <label class="gp-label">PIC Lead</label>
                  <input v-model="formActivity.pic_lead" type="text" class="gp-input">
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">Date</label>
                  <input v-model="formActivity.date" type="date" class="gp-input">
                </div>
                <div v-if="activityTab !== 'quotation'">
                  <label class="gp-label">Objective</label>
                  <input v-model="formActivity.objective" type="text" class="gp-input">
                </div>
              </div>
              <div v-if="activityTab !== 'quotation'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">Start Time</label>
                  <input v-model="formActivity.start_time" type="time" class="gp-input">
                </div>
                <div>
                  <label class="gp-label">End Time</label>
                  <input v-model="formActivity.end_time" type="time" class="gp-input">
                </div>
              </div>
              
              <div v-if="activityTab === 'followup'" class="space-y-4">
                <div>
                  <label class="gp-label">Follow Up Type</label>
                  <select v-model="formActivity.fu_type" class="gp-input">
                    <option>Phone Calls/Telephone</option>
                    <option>Texting/Chat</option>
                    <option>Follow up leads</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Notes</label>
                  <textarea v-model="formActivity.notes" rows="4" class="gp-input" placeholder="Catatan hasil..."></textarea>
                </div>
              </div>

              <div v-if="activityTab === 'meeting'" class="space-y-4">
                <div>
                  <label class="gp-label">Meeting Type</label>
                  <select v-model="formActivity.meeting_type" class="gp-input">
                    <option>Visit Meeting</option>
                    <option>Online Meeting</option>
                    <option>Office Visit Meeting</option>
                  </select>
                </div>

                <div v-if="formActivity.meeting_type === 'Visit Meeting'" class="space-y-4">
                  <label class="gp-label">Lokasi Meeting (Pilih di Peta)</label>

                  <div class="flex gap-2">
                    <input
                      v-model="meetingSearchQuery"
                      type="text"
                      class="gp-input flex-1"
                      placeholder="Cari lokasi"
                      @keyup.enter="searchMeetingLocation"
                    />
                    <button
                      type="button"
                      class="gp-btn-primary"
                      @click="searchMeetingLocation"
                    >
                      Cari
                    </button>
                  </div>

                  <div
                    ref="meetingMapContainer"
                    class="w-full h-64 rounded-xl border-2 border-gray-200 overflow-hidden shadow-inner"
                  ></div>

                  <div>
                    <label class="gp-label">Coordinates</label>
                    <input
                      v-model="formActivity.coordinates"
                      type="text"
                      class="gp-input font-mono text-sm"
                      readonly
                    />
                  </div>

                  <div class="text-sm text-gray-700 bg-gray-50 p-4 rounded-xl border-2 border-gray-200 font-medium">
                    {{ formActivity.location || 'Belum dipilih' }}
                  </div>
                </div>

                <div>
                  <label class="gp-label">MOM</label>
                  <textarea v-model="formActivity.mom" rows="4" class="gp-input"></textarea>
                </div>
              </div>

              <div v-if="activityTab === 'quotation'" class="space-y-4">
                <div>
                  <label class="gp-label">Link Quotation</label>
                  <input 
                    v-model="formActivity.link_quotation" 
                    type="text" 
                    class="gp-input" 
                    placeholder="https://..." 
                    @blur="autoFixUrl(formActivity, 'link_quotation')" 
                    required
                  >
                </div>
                <div class="flex items-center gap-3 cursor-pointer bg-green-50 p-4 rounded-xl border-2 border-green-200 hover:bg-green-100 transition-colors" @click="formActivity.is_send = !formActivity.is_send">
                  <CheckSquare :size="22" class="text-green-600" v-if="formActivity.is_send"/>
                  <Square :size="22" class="text-gray-400" v-else/>
                  <span class="text-sm font-semibold text-gray-700">Sudah Terkirim?</span>
                </div>
              </div>

              <div class="pt-4 flex justify-end gap-3 border-t mt-6">
                <button type="button" @click="showInputModal = false" class="gp-btn-secondary">
                  Batal
                </button>
                <button type="submit" class="gp-btn-primary">
                  <Save :size="18"/> Simpan
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="showDealDetailModal && selectedDeal" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl relative animate-fade-in-up overflow-hidden max-h-[90vh] flex flex-col">

          <div class="bg-gradient-to-r from-green-600 to-green-700 px-6 py-5 border-b flex justify-between items-start shrink-0">
            <div>
              <h2 class="text-2xl font-bold text-white flex items-center gap-3">
                <Briefcase :size="28" /> Deal Details
              </h2>
              <p class="text-green-100 text-sm mt-2 font-medium">{{ selectedDeal.property }}</p>
            </div>
            <button @click="closeDealDetailModal" class="text-white hover:text-green-200 bg-white/10 hover:bg-white/20 rounded-full p-2 shadow-sm transition-all">
              <X :size="20" />
            </button>
          </div>

          <div class="p-6 overflow-y-auto flex-1">

            <div v-if="dealDetails === null && selectedDeal" class="flex flex-col items-center justify-center py-12">
              <div class="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent mb-4"></div>
              <p class="text-gray-500 font-medium">Memuat data deal...</p>
            </div>

            <div v-else-if="!dealDetails" class="flex flex-col items-center justify-center py-12">
              <Package :size="64" class="text-gray-300 mb-4" />
              <p class="text-gray-500 font-medium">Data deal tidak ditemukan</p>
            </div>

            <div v-else class="space-y-6">

              <div class="bg-gradient-to-br from-green-50 to-green-100/50 p-5 rounded-xl border-2 border-green-200 shadow-sm">
                <h3 class="text-xs font-bold text-green-700 uppercase tracking-wide mb-4 flex items-center gap-2">
                  <MapPin :size="14" /> Informasi Properti
                </h3>

                <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <label class="gp-label-detail text-green-600">Property Name</label>
                    <p class="text-sm font-bold text-gray-900">{{ selectedDeal.property }}</p>
                  </div>

                  <div>
                    <label class="gp-label-detail text-green-600">Source</label>
                    <p class="text-sm font-semibold text-gray-900">{{ selectedDeal.source }}</p>
                  </div>

                  <div>
                    <label class="gp-label-detail text-green-600">Type</label>
                    <p class="text-sm font-semibold text-gray-900">{{ selectedDeal.type || '-' }}</p>
                  </div>

                  <div>
                    <label class="gp-label-detail text-green-600">GuestPro PIC</label>
                    <p class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                      <User :size="14" class="text-green-600" />
                      {{ selectedDeal.gp_pic }}
                    </p>
                  </div>
                  <div>
                    <label class="gp-label-detail text-green-600">Deal By</label>
                    <p class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                      <User :size="14" class="text-green-600" />
                      {{ selectedDeal.deal_by }}
                    </p>
                  </div>
                  <div>
                    <label class="gp-label-detail text-green-600">Date In</label>
                    <p class="text-sm font-semibold text-gray-900 flex items-center gap-2">
                      <Calendar :size="14" class="text-green-600" />
                      {{ selectedDeal.date_in }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-gray-50 to-gray-100/50 p-5 rounded-xl border-2 border-gray-200 shadow-sm">
                <h3 class="text-xs font-bold text-gray-700 uppercase tracking-wide mb-4 flex items-center gap-2">
                  <DollarSign :size="14" /> Informasi Deal
                </h3>

                <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label class="gp-label-detail">Deal Type</label>
                    <p class="text-sm font-bold text-gray-900">{{ dealDetails.deal_type }}</p>
                  </div>

                  <div>
                    <label class="gp-label-detail">Total Rooms</label>
                    <p class="text-sm font-bold text-gray-900">{{ dealDetails.room }} Room(s)</p>
                  </div>

                  <div>
                    <label class="gp-label-detail">PIC Lead</label>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ dealDetails.pic_lead_name || '-' }}
                    </p>
                  </div>
                </div>

                <div v-if="dealDetails.notes">
                  <label class="gp-label-detail">Notes</label>
                  <p class="text-sm text-gray-700 bg-white p-3 rounded-lg border border-gray-200 whitespace-pre-line">
                    {{ dealDetails.notes }}
                  </p>
                </div>
              </div>

              <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <div class="bg-gradient-to-r from-gray-100 to-gray-50 px-5 py-3 border-b">
                  <h3 class="text-xs font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                    <Package :size="14" /> Products & Packages
                  </h3>
                </div>

                <div class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50 text-gray-600 font-bold uppercase text-xs">
                      <tr>
                        <th class="p-4 text-left border-b-2">Package</th>
                        <th class="p-4 text-left border-b-2">Product</th>
                        <th class="p-4 text-right border-b-2">Amount</th>
                        <th class="p-4 text-right border-b-2">Amount By</th>
                      </tr>
                    </thead>

                    <tbody class="divide-y divide-gray-100">
                      <tr v-for="detail in dealDetails.details" :key="detail.id" class="hover:bg-gray-50 transition-colors">
                        <td class="p-4 font-bold text-gray-900">{{ detail.package || '-' }}</td>
                        <td class="p-4 text-gray-700 font-medium">{{ detail.product_initiation || '-' }}</td>
                        <td class="p-4 text-right font-bold text-green-600">
                          {{ detail.product_initiation_amount
                            ? new Intl.NumberFormat('id-ID', {
                                style: 'currency',
                                currency: 'IDR',
                                minimumFractionDigits: 0
                              }).format(detail.product_initiation_amount)
                            : 'Rp 0'
                          }}
                        </td>
                        <td class="p-4 text-right font-bold text-gray-900">
                          {{ detail.product_initiation_amount_by || '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="border-2 border-gray-200 rounded-xl overflow-hidden shadow-sm">
                <div class="bg-gradient-to-r from-gray-100 to-gray-50 px-5 py-3 border-b">
                  <h3 class="text-xs font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                    <Package :size="14" /> Initiation Fees
                  </h3>
                </div>

                <div class="overflow-x-auto">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50 text-gray-600 font-bold uppercase text-xs">
                      <tr>
                        <th class="p-4 text-left border-b-2">Initiation</th>
                        <th class="p-4 text-right border-b-2">Amount</th>
                      </tr>
                    </thead>

                    <tbody class="divide-y divide-gray-100">
                      <tr v-for="detail in dealDetails.details" :key="detail.id" class="hover:bg-gray-50 transition-colors">
                        <td class="p-4 text-gray-700 font-medium">{{ detail.product_initiation || '-' }}</td>
                        <td class="p-4 text-right font-bold text-green-600">
                          {{ detail.product_initiation_amount
                            ? new Intl.NumberFormat('id-ID', {
                                style: 'currency',
                                currency: 'IDR',
                                minimumFractionDigits: 0
                              }).format(detail.product_initiation_amount)
                            : 'Rp 0'
                          }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          </div>

          <div class="bg-gray-50 p-4 border-t flex justify-end shrink-0">
            <button @click="closeDealDetailModal" class="gp-btn-secondary">
              Tutup
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Onboarding Modal -->
    <Teleport to="body">
      <div v-if="showOnboardingModal && selectedOnboardingLead" class="fixed inset-0 z-[110] flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[85vh] flex flex-col overflow-hidden relative animate-fade-in-up">
          
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-50 to-blue-100 p-6 border-b shrink-0">
            <div class="flex justify-between items-start mb-5">
              <div>
                <h2 class="text-3xl font-bold text-gray-900">{{ selectedOnboardingLead.property }}</h2>
                <div class="flex items-center gap-2 mt-3">
                  <span class="text-xs bg-blue-500 text-white px-3 py-1.5 rounded-full font-bold shadow-sm">Onboarding</span>
                  <span class="text-xs bg-gray-200 text-gray-800 px-3 py-1.5 rounded-full font-bold shadow-sm">{{ selectedOnboardingLead.source }}</span>
                </div>
              </div>
              <button @click="showOnboardingModal = false" class="text-gray-400 hover:text-red-500 bg-white p-2 rounded-xl shadow-md transition-all hover:shadow-lg">
                <X :size="24"/>
              </button>
            </div>

            <!-- Info Grid -->
            <div class="grid grid-cols-4 gap-6 text-sm text-gray-600 bg-white p-5 rounded-xl border-2 border-gray-200 shadow-sm">
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Alamat</span>
                <span class="flex items-start gap-2 font-semibold text-gray-900">
                  <MapPin :size="14" class="mt-0.5 text-gray-500"/> 
                  {{ selectedOnboardingLead.address || '-' }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Koordinat</span>
                <span class="font-mono bg-gray-100 px-3 py-1 rounded-lg text-xs font-semibold">
                  {{ selectedOnboardingLead.coordinates || '-' }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">PIC GuestPro</span>
                <span class="flex items-center gap-2 font-semibold text-gray-900">
                  <User :size="14" class="text-gray-500"/> 
                  {{ selectedOnboardingLead.gp_pic }}
                </span>
              </div>
              <div>
                <span class="block font-bold text-gray-400 uppercase text-[10px] mb-2">Tgl Masuk</span>
                <span class="flex items-center gap-2 font-semibold text-gray-900">
                  <Calendar :size="14" class="text-gray-500"/> 
                  {{ selectedOnboardingLead.date_in }}
                </span>
              </div>
            </div>
          </div>

          <!-- Tabs & Content -->
          <div class="flex-1 flex flex-col bg-white overflow-hidden">
            <div class="flex justify-between items-center px-6 py-4 border-b-2 bg-white">
              <div class="flex bg-gray-100 p-1.5 rounded-xl shadow-inner">
                <button @click="switchOnboardingTab('followup')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="onboardingTab==='followup' ? 'bg-white shadow-md text-blue-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Follow Up
                </button>
                <button @click="switchOnboardingTab('meeting')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="onboardingTab==='meeting' ? 'bg-white shadow-md text-orange-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Meeting
                </button>
                <button @click="switchOnboardingTab('setupdata')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="onboardingTab==='setupdata' ? 'bg-white shadow-md text-purple-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Setup Data
                </button>
                <button @click="switchOnboardingTab('training')" class="px-5 py-2 text-sm font-bold rounded-lg transition-all" :class="onboardingTab==='training' ? 'bg-white shadow-md text-green-600' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200'">
                  Training
                </button>
              </div>
              <button @click="openOnboardingInputModal(null)" class="gp-btn-primary">
                <Plus :size="16" /> 
                Tambah {{ onboardingTab === 'followup' ? 'Follow Up' : (onboardingTab === 'meeting' ? 'Meeting' : (onboardingTab === 'setupdata' ? 'Setup Data' : 'Training')) }}
              </button>
            </div>

            <!-- Table Content -->
            <div class="flex-1 overflow-auto p-0">
              <table class="w-full text-left text-sm border-collapse">
                <thead class="bg-gradient-to-r from-gray-100 to-gray-50 text-gray-600 font-bold uppercase text-xs sticky top-0 z-10 shadow-sm">
                  <tr>
                    <th class="p-4 border-b-2 w-40">Tanggal & Waktu</th>
                    <th class="p-4 border-b-2 w-32">PIC GP</th>
                    
                    <!-- Follow Up Columns -->
                    <th v-if="onboardingTab === 'followup'" class="p-4 border-b-2 w-34">Tipe</th>
                    <th v-if="onboardingTab === 'followup'" class="p-4 border-b-2 w-48">Objective</th>
                    <th v-if="onboardingTab === 'followup'" class="p-4 border-b-2">Notes</th>
                    
                    <!-- Meeting Columns -->
                    <th v-if="onboardingTab === 'meeting'" class="p-4 border-b-2 w-34">Meeting Type</th>
                    <th v-if="onboardingTab === 'meeting'" class="p-4 border-b-2 w-40">Lokasi</th>
                    <th v-if="onboardingTab === 'meeting'" class="p-4 border-b-2 w-48">Objective</th>
                    <th v-if="onboardingTab === 'meeting'" class="p-4 border-b-2">MOM</th>
                    
                    <!-- Setup Data Columns -->
                    <th v-if="onboardingTab === 'setupdata'" class="p-4 border-b-2 w-32">Setup Type</th>
                    <th v-if="onboardingTab === 'setupdata'" class="p-4 border-b-2 w-32">Product</th>
                    <th v-if="onboardingTab === 'setupdata'" class="p-4 border-b-2 w-40">Task</th>
                    <th v-if="onboardingTab === 'setupdata'" class="p-4 border-b-2 w-34">Status</th>
                    <th v-if="onboardingTab === 'setupdata'" class="p-4 border-b-2">Notes</th>
                    
                    <!-- Training Columns -->
                    <th v-if="onboardingTab === 'training'" class="p-4 border-b-2 w-32">Training Type</th>
                    <th v-if="onboardingTab === 'training'" class="p-4 border-b-2 w-32">Periode</th>
                    <th v-if="onboardingTab === 'training'" class="p-4 border-b-2 w-40">Module</th>
                    <th v-if="onboardingTab === 'training'" class="p-4 border-b-2 w-32">Product</th>
                    <th v-if="onboardingTab === 'training'" class="p-4 border-b-2">Notes</th>
                    
                    <th class="p-4 border-b-2 text-center w-24">Aksi</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="item in onboardingActivityList" :key="item.id" class="hover:bg-gray-50 transition-colors">
                    <td class="p-4 align-top">
                      <div class="font-bold text-gray-900">{{ item.date || (item.start ? item.start.split('T')[0] : '-') }}</div>
                      <div class="text-xs text-gray-500 mt-1 flex items-center gap-1">
                        <Clock :size="12"/> 
                        {{ onboardingTab === 'setupdata' 
                          ? (item.start ? new Date(item.start).toLocaleTimeString('id-ID', {hour: '2-digit', minute: '2-digit'}) : '-')
                          : (item.start_time?.substring(0,5) || item.start?.substring(11,16) || '-') 
                        }} - 
                        {{ onboardingTab === 'setupdata' 
                          ? (item.end ? new Date(item.end).toLocaleTimeString('id-ID', {hour: '2-digit', minute: '2-digit'}) : '-')
                          : (item.end_time?.substring(0,5) || item.end?.substring(11,16) || '-') 
                        }}
                      </div>
                    </td>
                    <td class="p-4 align-top text-gray-800 font-semibold">{{ item.pic_gp }}</td>
                    
                    <!-- Follow Up Data -->
                    <template v-if="onboardingTab === 'followup'">
                      <td class="p-4 align-top">
                        <span class="px-3 py-1.5 rounded-lg border-2 text-xs font-bold shadow-sm bg-blue-50 text-blue-700 border-blue-200">
                          {{ item.fu_type }}
                        </span>
                      </td>
                      <td class="p-4 align-top font-semibold text-gray-800">{{ item.objective }}</td>
                      <td class="p-4 align-top text-gray-600 whitespace-pre-line">{{ item.notes }}</td>
                    </template>
                    
                    <!-- Meeting Data -->
                    <template v-if="onboardingTab === 'meeting'">
                      <td class="p-4 align-top">
                        <span class="px-3 py-1.5 rounded-lg border-2 text-xs font-bold shadow-sm bg-orange-50 text-orange-700 border-orange-200">
                          {{ item.meeting_type }}
                        </span>
                      </td>
                      <td class="p-4 align-top text-gray-700 font-medium">{{ item.location || '-' }}</td>
                      <td class="p-4 align-top font-semibold text-gray-800">{{ item.objective }}</td>
                      <td class="p-4 align-top text-gray-600 whitespace-pre-line">{{ item.mom }}</td>
                    </template>
                    
                    <!-- Setup Data Data -->
                    <template v-if="onboardingTab === 'setupdata'">
                      <td class="p-4 align-top font-semibold text-gray-800">{{ item.setup_type }}</td>
                      <td class="p-4 align-top text-gray-700">{{ item.product }}</td>
                      <td class="p-4 align-top text-gray-700">{{ item.task }}</td>
                      <td class="p-4 align-top">
                        <span class="px-3 py-1.5 rounded-lg border-2 text-xs font-bold shadow-sm" :class="item.status === 'Completed' ? 'bg-green-50 text-green-700 border-green-200' : (item.status === 'In Progress' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-yellow-50 text-yellow-700 border-yellow-200')">
                          {{ item.status }}
                        </span>
                      </td>
                      <td class="p-4 align-top text-gray-600 whitespace-pre-line">{{ item.notes }}</td>
                    </template>
                    
                    <!-- Training Data -->
                    <template v-if="onboardingTab === 'training'">
                      <td class="p-4 align-top">
                        <span class="px-3 py-1.5 rounded-lg border-2 text-xs font-bold shadow-sm bg-green-50 text-green-700 border-green-200">
                          {{ item.training_type }}
                        </span>
                      </td>
                      <td class="p-4 align-top font-semibold text-gray-800">{{ item.periode }}</td>
                      <td class="p-4 align-top text-gray-700">{{ item.module_in_charge }}</td>
                      <td class="p-4 align-top font-semibold text-gray-800">{{ item.product }}</td>
                      <td class="p-4 align-top text-gray-600 whitespace-pre-line">{{ item.notes }}</td>
                    </template>
                    
                    <td class="p-4 align-top text-center">
                      <div class="flex justify-center gap-2">
                        <button @click="openOnboardingInputModal(item)" class="text-blue-600 hover:bg-blue-50 p-2 rounded-lg transition-all" title="Edit">
                          <Edit :size="16"/>
                        </button>
                        <button @click="deleteOnboardingActivity(item.id)" class="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-all" title="Hapus">
                          <Trash2 :size="16"/>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="onboardingActivityList.length === 0">
                    <td :colspan="onboardingTab === 'meeting' ? 7 : (onboardingTab === 'setupdata' ? 8 : (onboardingTab === 'training' ? 8 : 6))" class="p-12 text-center text-gray-400 italic bg-gray-50/50">
                      Belum ada riwayat aktivitas. Klik tombol "Tambah" di atas.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Onboarding Input Modal -->
    <Teleport to="body">
      <div v-if="showOnboardingInputModal" class="fixed inset-0 z-[120] flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg relative animate-fade-in-up max-h-[85vh] overflow-y-auto">
          <div class="bg-white p-6 border-b rounded-t-2xl flex justify-between items-center sticky top-0 z-10">
            <h3 class="font-bold text-gray-900 text-xl flex items-center gap-3">
              <span class="w-1.5 h-8 bg-blue-500 rounded-full inline-block"></span> 
              {{ isEditingOnboardingActivity ? 'Edit Data' : 'Input Data Baru' }}
            </h3>
            <button @click="showOnboardingInputModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
              <X :size="24"/>
            </button>
          </div>
          
          <div class="p-6">
            <form @submit.prevent="saveOnboardingActivity" class="space-y-5">
              <!-- Common Fields -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">PIC GP</label>
                  <select v-model="formOnboarding.pic_gp" class="gp-input">
                    <option v-for="pic in picList" :key="pic" :value="pic">{{ pic }}</option>
                  </select>
                </div>
                <div v-if="onboardingTab === 'followup' || onboardingTab === 'meeting'">
                  <label class="gp-label">PIC Lead</label>
                  <input v-model="formOnboarding.pic_lead" type="text" class="gp-input">
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">Date</label>
                  <input v-model="formOnboarding.date" type="date" class="gp-input" required>
                </div>
                <div v-if="onboardingTab === 'followup' || onboardingTab === 'meeting'">
                  <label class="gp-label">Objective</label>
                  <input v-model="formOnboarding.objective" type="text" class="gp-input">
                </div>
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="gp-label">Start Time</label>
                  <input v-model="formOnboarding.start_time" type="time" class="gp-input" required>
                </div>
                <div>
                  <label class="gp-label">End Time</label>
                  <input 
                    v-model="formOnboarding.end_time" 
                    type="time" 
                    class="gp-input"
                  >
                </div>
              </div>

              <!-- Follow Up Specific -->
              <div v-if="onboardingTab === 'followup'" class="space-y-4">
                <div>
                  <label class="gp-label">Follow Up Type</label>
                  <select v-model="formOnboarding.fu_type" class="gp-input">
                    <option>Phone Calls/Telephone</option>
                    <option>Texting/Chat</option>
                    <option>Follow up leads</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Notes</label>
                  <textarea v-model="formOnboarding.notes" rows="4" class="gp-input"></textarea>
                </div>
              </div>

              <!-- Meeting Specific -->
              <div v-if="onboardingTab === 'meeting'" class="space-y-4">
                <div>
                  <label class="gp-label">Meeting Type</label>
                  <select v-model="formOnboarding.meeting_type" class="gp-input">
                    <option>Visit Meeting</option>
                    <option>Online Meeting</option>
                    <option>Office Visit Meeting</option>
                  </select>
                </div>
                <div>
                  <label class="gp-label">Location</label>
                  <input v-model="formOnboarding.location" type="text" class="gp-input">
                </div>
                <div>
                  <label class="gp-label">MOM</label>
                  <textarea v-model="formOnboarding.mom" rows="4" class="gp-input"></textarea>
                </div>
              </div>

              <!-- Setup Data Specific -->
              <div v-if="onboardingTab === 'setupdata'" class="space-y-4">
                <div>
                  <label class="gp-label">Setup Type</label>
                  <select v-model="formOnboarding.setup_type" class="gp-input" required>
                    <option value="" disabled>-- Pilih Setup Type --</option>
                    <option v-for="type in setupTypes" :key="type">{{ type }}</option>
                  </select>
                </div>
                
                <div>
                  <label class="gp-label">Product</label>
                  <input v-model="formOnboarding.product" type="text" class="gp-input" placeholder="e.g. PMS, Channel Manager" required>
                </div>
                
                <div>
                  <label class="gp-label">Task</label>
                  <select v-model="formOnboarding.task" class="gp-input" required>
                    <option value="" disabled>-- Pilih Task --</option>
                    <option v-for="task in taskOptions" :key="task">{{ task }}</option>
                  </select>
                </div>
                
                <div>
                  <label class="gp-label">Status</label>
                  <select v-model="formOnboarding.status" class="gp-input">
                    <option value="On Progress">On Progress</option>
                    <option value="Done">Done</option>
                    <option value="Pending">Pending</option>
                  </select>
                </div>
                
                <div>
                  <label class="gp-label">Notes</label>
                  <textarea v-model="formOnboarding.setup_notes" rows="4" class="gp-input" placeholder="Detail setup yang dilakukan..."></textarea>
                </div>
              </div>

              <!-- Training Specific Fields (di dalam showOnboardingInputModal) -->
              <div v-if="onboardingTab === 'training'" class="space-y-4">
                <div>
                  <label class="gp-label">Training Type</label>
                  <select v-model="formOnboarding.training_type" class="gp-input" required>
                    <option value="" disabled>-- Pilih Training Type --</option>
                    <option value="Implementation">Implementation</option>
                    <option value="Maintenance">Maintenance</option>
                    <option value="Migration">Migration</option>
                  </select>
                </div>
                
                <div>
                  <label class="gp-label">Periode</label>
                  <input 
                    v-model="formOnboarding.periode" 
                    type="text" 
                    class="gp-input" 
                    placeholder="e.g. Day 1, Week 1, Phase 1" 
                    required
                  >
                </div>
                
                <div>
                  <label class="gp-label">Module in Charge</label>
                  <select v-model="formOnboarding.module_in_charge" class="gp-input" required>
                    <option value="" disabled>-- Pilih Module --</option>
                    <option value="Angka">Angka</option>
                    <option value="Buah">Buah</option>
                    <option value="Makan">Makan</option>
                  </select>
                </div>
                
                <div>
                  <label class="gp-label">Product</label>
                  <input 
                    v-model="formOnboarding.training_product" 
                    type="text" 
                    class="gp-input" 
                    placeholder="e.g. PMS Pro, Channel Manager" 
                    required
                  >
                </div>
                
                <div>
                  <label class="gp-label">Training Notes</label>
                  <textarea 
                    v-model="formOnboarding.training_notes" 
                    rows="4" 
                    class="gp-input" 
                    placeholder="Catatan hasil training..."
                  ></textarea>
                </div>
              </div>

              <div class="pt-4 flex justify-end gap-3 border-t mt-6">
                <button type="button" @click="showOnboardingInputModal = false" class="gp-btn-secondary">
                  Batal
                </button>
                <button type="submit" class="gp-btn-primary">
                  <Save :size="18"/> Simpan
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>

  </MainLayout>
</template>

<style scoped>
/* Pipeline Container - Fix horizontal scroll */
.pipeline-container {
  @apply w-full;
  position: relative;
  padding-top: 1.5rem; /* Add padding to prevent text being cut */
}

.pipeline-header {
  @apply mb-6 flex justify-between items-center;
  background: white;
  padding-bottom: 1rem;
  padding-top: 2.5rem;
}

.pipeline-board {
  @apply flex gap-4 pb-8 items-start;
  height: calc(100vh - 260px); /* Adjusted for extra padding */
  overflow-x: auto;
  overflow-y: hidden;
  width: 100%;
  /* Smooth scrolling */
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

/* Custom scrollbar */
.pipeline-board::-webkit-scrollbar {
  height: 8px;
}

.pipeline-board::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}

.pipeline-board::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.pipeline-board::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* GuestPro Design System */
.gp-btn-primary {
  @apply bg-gradient-to-r from-lime-500 to-lime-600 hover:from-lime-600 hover:to-lime-700 text-white font-bold rounded-xl px-4 py-2.5 shadow-md hover:shadow-lg transition-all duration-200 flex items-center gap-2;
}

.gp-btn-secondary {
  @apply bg-white border-2 border-gray-200 hover:border-gray-300 text-gray-700 font-semibold rounded-xl px-4 py-2.5 hover:bg-gray-50 transition-all duration-200 flex items-center gap-2;
}

.gp-badge {
  @apply bg-gray-200 text-gray-800 px-3 py-1 rounded-full text-xs font-bold shadow-sm;
}

.gp-card {
  @apply bg-white p-4 rounded-xl shadow-sm border border-gray-100 cursor-move hover:shadow-lg transition-all duration-200 relative select-none;
}

.gp-card-actions {
  @apply absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white/95 rounded-lg p-1 shadow-md z-10 backdrop-blur-sm;
}

.gp-label {
  @apply block text-xs font-bold text-gray-600 mb-2 uppercase tracking-wide;
}

.gp-label-detail {
  @apply block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1;
}

.gp-input {
  @apply w-full border-2 border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-lime-500 focus:border-lime-500 outline-none transition-all;
}

.gp-input-sm {
  @apply w-full border border-gray-200 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-lime-500 focus:border-lime-500 outline-none transition-all;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-fade-in {
  animation: fadeInUp 0.3s ease-out;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pac-container {
  z-index: 9999 !important;
}

/* Fix map z-index in modal */
.leaflet-container {
  z-index: 1 !important;
}

.leaflet-pane {
  z-index: 1 !important;
}

.leaflet-top,
.leaflet-bottom {
  z-index: 2 !important;
}
</style>