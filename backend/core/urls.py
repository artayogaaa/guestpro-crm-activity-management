from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets
from activities.views import ActivityViewSet
from leads.views import LeadViewSet, FollowUpViewSet, MeetingViewSet, QuotationViewSet, DealViewSet, setupdata_list, setupdata_detail, SetupDataViewSet, TrainingViewSet
# Import dari Core
from core.views import RegisterView, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'activities', ActivityViewSet)
router.register(r'leads', LeadViewSet)
router.register(r'followups', FollowUpViewSet)
router.register(r'meetings', MeetingViewSet)
router.register(r'quotations', QuotationViewSet)
router.register(r'users', UserViewSet)
router.register(r'deals', DealViewSet)
router.register(r'setupdata', SetupDataViewSet, basename='setupdata')
router.register(r'trainings', TrainingViewSet, basename='training')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='auth_register'),

    # API Routes
    path('api/', include(router.urls)),
    path('setupdata/', setupdata_list, name='setupdata-list'),
    path('setupdata/<str:pk>/', setupdata_detail, name='setupdata-detail'),
]