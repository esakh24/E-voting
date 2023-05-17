from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.account_login, name="account_login"),
    # path('register/', views.account_register, name="account_register"),
    path('logout/', views.account_logout, name="account_logout"),
    path('viewBulletin/', views.view_bulletin, name='viewBulletin'),
    path('viewResults/', views.view_results, name='viewResults'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('forget_password/', views.forget_password, name='forget_password'),
    path('send_mail', views.send_mail, name='send_mail'),
    path('reset_password', views.otp_verify, name = 'reset_password'),
    
]
