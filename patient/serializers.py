from rest_framework import serializers
from accounts.models import (
    CustomUser, 
    Doctor, 
    TimeSlot, 
    DocumentImage, 
    Time, 
    DoctorAppointment,
    Medicine,
    Prescription,
    Payment)
from adminApp.serializers import DoctorSerializer

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    times = TimeSerializer(many=True, required=False)
    class Meta:
        model = TimeSlot
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = '__all__'

class CustomUserssSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class DoctorListsSerializer(serializers.ModelSerializer):
    user = CustomUserssSerializer() 
    time_slots = TimeSlotSerializer(many=True, required=False)  # Include TimeSlot data

    class Meta:
        model = Doctor
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source = 'user.first_name')
    email = serializers.CharField(source = 'user.email')
    mobile = serializers.CharField(source = 'user.mobile')
    doctor = serializers.CharField(source = 'doctor.user.first_name')
    class Meta:
        model = DoctorAppointment
        fields = '__all__'

class AppointmentDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DoctorAppointment

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ['id', 'medicine_name']

class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True)
    doctor_name = serializers.CharField(source='appointment.doctor.user.first_name')
    doctor_email = serializers.CharField(source='appointment.doctor.user.email')

    class Meta:
        model = Prescription
        fields = ['id', 'instructions', 'comments', 'created_at', 'medicines','doctor_name', 'doctor_email']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PatientAppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.first_name')
    doctor_email = serializers.CharField(source='doctor.user.email')
    doctor_specialization = serializers.CharField(source='doctor.specialization')
    doctor_experience = serializers.CharField(source='doctor.experience')
    doctor_qualification = serializers.CharField(source='doctor.qualification')
    doctor_online_fees = serializers.CharField(source='doctor.online_fees')
    doctor_chat_fees = serializers.CharField(source='doctor.chat_fees')
    doctor_profileImage = serializers.CharField(source='doctor.profileImage')
    doctor_status = serializers.CharField(source='doctor.status')
    payment = PaymentSerializer()

    class Meta:
        model = DoctorAppointment
        fields = '__all__' 

class PatientViewSerializer(serializers.ModelSerializer):
     class Meta:
        model = CustomUser
        fields = '__all__' 

class DoctorFindSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    time_slots = TimeSlotSerializer(many=True, required=False)  # Include TimeSlot data

    class Meta:
        model = Doctor
        fields = '__all__'


