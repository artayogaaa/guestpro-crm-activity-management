from rest_framework import serializers
from .models import Lead, LeadPIC, FollowUp, Meeting, Quotation, Deal, DealDetail

class LeadPICSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False) # Agar update bisa terima ID 

    class Meta:
        model = LeadPIC
        fields = ['id', 'pic_name', 'phone_number', 'whatsapp', 'email']

class LeadSerializer(serializers.ModelSerializer):
    pics = LeadPICSerializer(many=True)
    lead_id = serializers.CharField(read_only=True)

    class Meta:
        model = Lead
        fields = [
            'lead_id', 'property', 'source', 'type', 
            'coordinates', 'address', 'gp_pic',
            'date_in', 'status_kanban', 'pics',
            'referral_or_affiliate_by', 'commission_amount'
        ]

    def create(self, validated_data):
        pics_data = validated_data.pop('pics', [])
        lead = Lead.objects.create(**validated_data)
        
        for pic_data in pics_data:
            if 'id' in pic_data: del pic_data['id']
            LeadPIC.objects.create(lead=lead, **pic_data)
        return lead

    def update(self, instance, validated_data):
        pics_data = validated_data.pop('pics', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if pics_data is not None:
            instance.pics.all().delete()
            for pic_data in pics_data:
                if 'id' in pic_data: del pic_data['id']
                LeadPIC.objects.create(lead=instance, **pic_data)

        return instance

# ==========================================
# ACTIVITY SERIALIZERS
# ==========================================

class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = '__all__'

# ==========================================
# DEAL SERIALIZERS
# ==========================================

class DealDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealDetail
        fields = '__all__'
        read_only_fields = ['deal'] # Deal ID diisi otomatis oleh parent

class DealSerializer(serializers.ModelSerializer):
    details = DealDetailSerializer(many=True) # Enable Nested Write (bisa simpan array details)
    
    # --- Extra Fields untuk Display di Frontend (Read Only) ---
    # Mengambil data dari relasi ForeignKey 'lead' agar frontend bisa nampilin nama property
    lead_property = serializers.CharField(source='lead.property', read_only=True)
    lead_pic_gp = serializers.CharField(source='lead.gp_pic', read_only=True)
    pic_lead_name = serializers.CharField(source='pic_lead.pic_name', read_only=True)
    pic_lead_contact = serializers.CharField(source='pic_lead.phone_number', read_only=True)
    pic_lead_email = serializers.CharField(source='pic_lead.email', read_only=True)

    class Meta:
        model = Deal
        fields = '__all__'

    def create(self, validated_data):
        # 1. Ambil data details (array) dari payload
        details_data = validated_data.pop('details')
        
        # 2. Buat Header Deal
        deal = Deal.objects.create(**validated_data)
        
        # 3. Buat Detail Deal satu per satu
        for detail_data in details_data:
            DealDetail.objects.create(deal=deal, **detail_data)
            
        return deal
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        
        # 1. Update Field Utama Deal
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 2. Update Details (Hapus lama, Timpa baru - paling aman untuk nested list)
        if details_data is not None:
            instance.details.all().delete()
            for detail_data in details_data:
                DealDetail.objects.create(deal=instance, **detail_data)
        
        return instance
    
    