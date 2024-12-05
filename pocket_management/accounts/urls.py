from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Home and dashboard
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',next_page='accounts:profile'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:home'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Profile
    
    path('change-password/', views.change_password, name='change_password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)