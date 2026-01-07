import hashlib
import time
import random
import string
from django.db import models

class Lead(models.Model):
    # Primary Key berupa String Unik (L-XXXXXX)
    lead_id = models.CharField(max_length=64, primary_key=True, editable=False)
    
    property = models.CharField(max_length=200)
    source = models.CharField(max_length=100, blank=True)
    type = models.CharField(max_length=100, blank=True)
    coordinates = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True)
    gp_pic = models.CharField(max_length=100)
    date_in = models.DateField()
    
    STATUS_KANBAN_CHOICES = [
        ('lead_generation', 'Lead Generation'),
        ('follow_up', 'Follow Up'),
        ('quotation', 'Quotation'),
        ('deals', 'Deals'),
        ('onboarding', 'Onboarding'),
        ('retention', 'Retention'),
    ]
    status_kanban = models.CharField(max_length=50, choices=STATUS_KANBAN_CHOICES, default='lead_generation')
    referral_or_affiliate_by = models.CharField(max_length=150, blank=True, null=True)
    commission_amount = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lead'
    def save(self, *args, **kwargs):
        if not self.lead_id:
            raw_string = f"{time.time()}-{random.randint(1000, 9999)}"
            hash_object = hashlib.sha256(raw_string.encode())
            self.lead_id = f"L-{hash_object.hexdigest()[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property} ({self.lead_id})"

class LeadPIC(models.Model):
    lead = models.ForeignKey(Lead, related_name='pics', on_delete=models.CASCADE)
    pic_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        db_table = 'lead_pic'

class FollowUp(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    pic_gp = models.CharField(max_length=100)
    pic_lead = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    objective = models.CharField(max_length=200, default="Sales & Leads")
    stage = models.CharField(max_length=100, default="Follow Up")
    fu_type = models.CharField(max_length=50)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'follow_up'

class Meeting(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    pic_gp = models.CharField(max_length=100)
    pic_lead = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    objective = models.CharField(max_length=200, default="Sales & Leads")
    stage = models.CharField(max_length=100, default="Follow Up")
    meeting_type = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    coordinates = models.CharField(max_length=100, blank=True, null=True)
    mom = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'meeting'
    # ... (model Lead, LeadPIC, FollowUp, Meeting yang sudah ada)

class Quotation(models.Model):
    quotation_id = models.AutoField(primary_key=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    pic_gp = models.CharField(max_length=100)
    date = models.DateField()
    link_quotation = models.URLField(max_length=500, blank=True, null=True) # Link dokumen
    is_send = models.BooleanField(default=False) # Status terkirim atau belum
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quotation'

def generate_deal_id():
    return 'D-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_deal_detail_id():
    return 'DD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Deal(models.Model):
    deal_id = models.CharField(max_length=20, primary_key=True, default=generate_deal_id, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    deal_by = models.CharField(max_length=100)
    DEAL_TYPES = [
        ('New Deal', 'New Deal'), ('Migration', 'Migration'), 
        ('Update Package', 'Update Package'), ('Refreshment Training', 'Refreshment Training'), 
        ('Upselling', 'Upselling'), ('Room Update', 'Room Update')
    ]
    deal_type = models.CharField(max_length=50, choices=DEAL_TYPES)
    date = models.DateField(auto_now_add=True) # Default today
    room = models.IntegerField(default=0)
    project_manager = models.CharField(max_length=100, blank=True, null=True) # Kosong dulu
    notes = models.TextField(blank=True, null=True)
    nik_npwp = models.FileField(upload_to='docs/', blank=True, null=True) # File/Link
    management = models.CharField(max_length=100, blank=True, null=True)
    # --- FIELD DEALING PROPERTY (DIISI NANTI) ---
    link_invoice = models.CharField(max_length=255, blank=True, null=True)
    invoice_issued = models.BooleanField(default=False)
    subscribe_changed = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    bukti_payment = models.FileField(upload_to='payments/', blank=True, null=True)
    pic_penerima_bukti_bayar = models.CharField(max_length=100, blank=True, null=True)
    is_partial_payment = models.BooleanField(default=False)
    link_payment_receipt = models.CharField(max_length=255, blank=True, null=True)
    is_invoice_send_to_customer = models.BooleanField(default=False)
    pic_lead = models.ForeignKey(LeadPIC, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    account_manager = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deal'

    def __str__(self):
        return f"{self.deal_id} - {self.lead.property}"

class DealDetail(models.Model):
    deal_detail_id = models.CharField(max_length=20, primary_key=True, default=generate_deal_detail_id, editable=False)
    deal = models.ForeignKey(Deal, related_name='details', on_delete=models.CASCADE)
    
    package = models.CharField(max_length=100)
    # Product bisa pilih banyak, simpan sebagai string koma (misal: "PMS, Channel Manager")
    product_initiation = models.CharField(max_length=255) 
    product_initiation_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    product_initiation_amount_by = models.CharField(max_length=50) # Misal: Month, Year
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deal_detail'
    def __str__(self):
        return f"Quote for {self.lead}"