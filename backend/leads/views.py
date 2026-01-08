from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Lead, FollowUp, Meeting, Quotation, Deal, DealDetail, SetupData
from .serializers import LeadSerializer, FollowUpSerializer, MeetingSerializer, QuotationSerializer, DealSerializer, SetupDataSerializer
from rest_framework import viewsets
from .models import SetupData, Training
from .serializers import SetupDataSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import logging

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-created_at')
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

class FollowUpViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_classes = [IsAuthenticated]

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]

class SetupDataViewSet(viewsets.ModelViewSet):
    queryset = SetupData.objects.all()
    serializer_class = SetupDataSerializer
    lookup_field = 'setup_id'

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
def setupdata_list(request):
    logger.info("🔵 === setupdata_list called ===")
    logger.info(f"📌 Method: {request.method}")
    
    if request.method == 'GET':
        data = SetupData.objects.all().order_by('-created_at')
        serializer = SetupDataSerializer(data, many=True)
        logger.info(f"✅ GET Success - {len(serializer.data)} items")
        return Response(serializer.data)
    
    elif request.method == 'POST':
        logger.info(f"📥 POST Data received: {request.data}")
        
        serializer = SetupDataSerializer(data=request.data)
        
        if serializer.is_valid():
            logger.info("✅ Serializer VALID")
            logger.info(f"📝 Validated Data: {serializer.validated_data}")
            
            instance = serializer.save()
            logger.info(f"✅ Saved with ID: {instance.setup_id}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error("❌ Serializer INVALID")
            logger.error(f"❌ Errors: {serializer.errors}")
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def setupdata_detail(request, pk):
    logger.info(f"🔵 === setupdata_detail called ===")
    logger.info(f"📌 Method: {request.method}, PK: {pk}")
    
    try:
        data = SetupData.objects.get(setup_id=pk)
        logger.info(f"✅ Found SetupData: {data.setup_id}")
    except SetupData.DoesNotExist:
        logger.error(f"❌ SetupData not found with ID: {pk}")
        return Response({'error': 'Setup Data not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SetupDataSerializer(data)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        logger.info(f"📥 PUT Data received: {request.data}")
        
        serializer = SetupDataSerializer(data, data=request.data)
        
        if serializer.is_valid():
            logger.info("✅ Serializer VALID for UPDATE")
            instance = serializer.save()
            logger.info(f"✅ Updated ID: {instance.setup_id}")
            
            return Response(serializer.data)
        else:
            logger.error("❌ Serializer INVALID for UPDATE")
            logger.error(f"❌ Errors: {serializer.errors}")
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        setup_id = data.setup_id
        data.delete()
        logger.info(f"✅ Deleted ID: {setup_id}")
        
        return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)