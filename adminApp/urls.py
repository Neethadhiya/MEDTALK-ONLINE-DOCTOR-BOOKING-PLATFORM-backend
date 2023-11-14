from django.urls import path
from . import views

app_name = 'adminApp'
urlpatterns = [
    path('show_doctor_list/',views.ShowDoctorList.as_view(), name = 'show_doctor_list'),
    path('block_doctor/<int:id>/',views.BlockDoctor.as_view(), name = 'block_doctor'),
    path('view_doctor_details/<int:id>/',views.ViewDoctorDetails.as_view(),name='view_doctor_details'),
    path('show_patient_list/',views.ShowPatientList.as_view(),name='show_patient_list'),
    path('block_patient/<int:id>/',views.BlockPatient.as_view(), name = 'block_patient'),
    path('approve_doctor/<int:id>/',views.ApproveDoctor.as_view(), name = 'approve_doctor'),
    path('reject_doctor/<int:id>/',views.RejectDoctor.as_view(), name = 'reject_doctor'),
    path('get_admin_chart/',views.GetAdminChart.as_view(), name = 'get_admin_chart'),

]