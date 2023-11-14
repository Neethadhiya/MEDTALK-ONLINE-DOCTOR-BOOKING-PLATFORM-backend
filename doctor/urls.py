from django.urls import path
from . import views

app_name = 'doctor'
urlpatterns = [
    path('create_doctor_profile/', views.CreateDoctorProfileView.as_view(), name = 'create_doctor_profile'),
    path('show_is_doctor/<int:id>/', views.ShowIsDoctor.as_view(), name = 'show_is_doctor'),
    path('timeslot_video_consult/', views.TimeslotVideoConsult.as_view(), name = 'timeslot_video_consult'),
    path('video_view_all/', views.VideoViewAll.as_view(), name = 'video_view_all'),
    path('todays_video_consult/', views.TodaysVideoConsult.as_view(), name = 'todays_video_consult'),
    path('todays_chat_consult/', views.TodaysChatConsult.as_view(), name = 'todays_chat_consult'),
    path('view_appointment_details/<int:id>/', views.ViewAppointmentDetails.as_view(), name = 'view_appointment_details'),
    path('cancel_appointment/<int:id>/', views.CancelAppointment.as_view(), name = 'cancel_appointment'),
    path('chat_view_all/', views.ChatViewAll.as_view(), name = 'chat_view_all'),
    path('view_all_appointments/', views.ViewAllAppointments.as_view(), name = 'view_all_appointments'),
    path('send_video_call_link_to_patient/<int:id>/', views.SendVideoCallLinkToPatient.as_view(), name = 'send_video_call_link_to_patient'),
    path('get_patient_info/<int:id>/', views.GetPatientInfo.as_view(), name = 'get_patient_info'),
    path('add_prescription/<int:id>/', views.AddPrescription.as_view(), name = 'add_prescription'),
    path('check_payment_status/<int:id>/', views.CheckPaymentStatus.as_view(), name = 'check_payment_status'),
    path('view_doctor_profile_dashboard/', views.ViewDoctorProfileView.as_view(), name = 'view_doctor_profile_dashboard'),
    path('edit_doctor_profile/', views.EditDoctorProfileView.as_view(), name = 'edit_doctor_profile'),
    path('get_doctor_chart/', views.GetDoctorChartView.as_view(), name = 'get_doctor_chart'),



]