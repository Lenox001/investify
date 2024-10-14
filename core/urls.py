from django.urls import path
from .views import index, user, contact, invest, login_view, register_view, logout_view,edit_account,basic_package, classic_package, premium_package, titanium_package,investment_overview,lipa_na_mpesa_online

urlpatterns = [
    path('', index, name='index'),
    path('user/', user, name='user'),
    path('contact/', contact, name='contact'),
    path('invest/', invest, name='invest'),
    path('login/', login_view, name='login'),  # URL for login
    path('register/', register_view, name='register'),  # URL for registration
    path('logout/', logout_view, name='logout'),  # URL for logout
     path('edit_account/', edit_account, name='edit_account'),
     path('basic-package/', basic_package, name='basic_package'),
    path('classic-package/', classic_package, name='classic_package'),
    path('premium-package/', premium_package, name='premium_package'),
    path('titanium-package/', titanium_package, name='titanium_package'),
    path('investments/', investment_overview, name='investment_overview'),
    path('lipa-na-mpesa/',lipa_na_mpesa_online, name='lipa_na_mpesa_online'),
    
     
]
