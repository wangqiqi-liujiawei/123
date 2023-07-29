from django.urls import path, include
from . import views
# from django.contrib.auth import views as vs
# app_name = 'account'

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    # path('login/', vs.LoginView.as_view(), name='login'),
    # path('logout/', vs.LogoutView.as_view(), name='logout'),
    # path('password_change/', vs.PasswordChangeView.as_view(), name='password_change'),
    # path('password_change/done/', vs.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # path('password_reset/', vs.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', vs.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', vs.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', vs.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', views.dashboard, name='dashboard'),
    path('', include('django.contrib.auth.urls')),
    path('registers/', views.registers, name='registers'),
    path('edit/', views.edit, name='edit'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/', views.user_list, name='user_list'),
    path('users/<username>/', views.user_detail, name='user_detail'),
    path('action_list/', views.action_list, name='action_list'),
]
