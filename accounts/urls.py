from django.urls import path
from . import views
from patient.views import ShowDoctorList


app_name = 'accounts'
urlpatterns = [
    path('register/',views.RegisterView.as_view(), name = 'register'),
    path('verify_otp/',views.VetifyOTP.as_view(), name = 'verify_otp'),
    path('login/',views.LoginView.as_view(), name = 'login'),
    path('forgot_password/',views.ForgotPassword.as_view(),name='forgot_password'),
    path('reset_password/',views.ResetPassword.as_view(),name='reset_password'),
    path('show_doctor_list/',ShowDoctorList.as_view(), name = 'show_doctor_list'),
]