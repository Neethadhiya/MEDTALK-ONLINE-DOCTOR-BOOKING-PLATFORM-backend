from django.urls import path
from . import views

app_name = 'patient'
urlpatterns = [
    path('show_doctors_list/',views.ShowDoctorsList.as_view(), name = 'show_doctors_list'),
    path('book_now_show_timeslot/<int:id>/',views.BookNowShowTimeslot.as_view(), name = 'book_now_show_timeslot'),
    path('get_timeslots/',views.GetTimeSlot.as_view(), name = 'get_timeslots'),
    path('book_appointment/',views.BookAppoinment.as_view(), name = 'book_appointment'),
    path('get_appoinment_details/<int:id>/',views.GetAppointmentDetails.as_view(), name = 'get_appoinment_details'),
    path('create-payment-intent/<int:id>/', views.StripeCheckoutView.as_view(), name='create-payment-intent'),
    path('config/', views.ConfigView.as_view(), name='config'), 
    path('payment_success/',views.PaymentSuccess.as_view(), name = 'payment_success'),
    path('view_patient_prescription/<int:id>/', views.ViewPatientPrescriptonView.as_view(), name='view_patient_prescription'),
    path('view_patient_appointment_details/', views.ViewPatientAppointmentView.as_view(), name='view_patient_appointment_details'),
    path('view_patient_profile_dashboard/', views.PatientProfileView.as_view(), name='view_patient_profile_dashboard'), 
    path('search_doctors/', views.SearchDoctorsList.as_view(), name='search_doctors'),
  ]