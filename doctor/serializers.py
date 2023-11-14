from rest_framework import serializers
from accounts.models import (
    CustomUser,
    Doctor, 
    TimeSlot ,
    DocumentImage, 
    Time, 
    DoctorAppointment,
    Payment,
    Prescription,
    Medicine)
from adminApp.serializers import DoctorListsSerializer

class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = ['documents']  # Use the lowercase field name 'documents'
    documents = serializers.ImageField()

class DoctorProfileSerializer(serializers.ModelSerializer):
    document_images = DocumentImageSerializer(many=True, required=False, source='documents')
    class Meta:
        model = Doctor
        fields = ['experience',
                   'qualification', 
                   'gender', 
                   'specialization',
                   'location', 
                   'city', 
                   'profileImage', 
                   'document_images',
                   'online_fees',
                   'chat_fees']

    def create(self, validated_data):
        # Create the Doctor instance without saving it yet
        doctor_instance = Doctor.objects.create(**validated_data)
        doctor_instance.user = self.context['request'].user
        doctor_instance.save()

        # Extract and save document images
        document_images_data = self.context['request'].FILES.getlist("documents")
        for document_image in document_images_data:
            DocumentImage.objects.create(doctor=doctor_instance, documents=document_image)

        return doctor_instance
    
class ShowDoctorSerializer(serializers.ModelSerializer):
    doctor_data = DoctorListsSerializer(source='doctor_profile')
    class Meta:
        model = CustomUser
        fields = '__all__'

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Time
        fields = '__all__'

class TimeSlotSerializer(serializers.ModelSerializer):
    times = TimeSerializer(many=True, required=False)
    class Meta:
        model = TimeSlot
        fields = '__all__'

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.CharField(source ='doctor.user.first_name')
    user = serializers.CharField(source = 'user.first_name')
    mobile = serializers.CharField(source = 'user.mobile')
    time = serializers.CharField(source = 'time.time')
    class Meta:
        model = DoctorAppointment
        fields = '__all__'

class ViewAllDoctorAppointmentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source =  'user.first_name')
    email = serializers.CharField(source =  'user.email')
    mobile = serializers.CharField(source =  'user.mobile')
    class Meta:
        model = DoctorAppointment
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class AppoinmentDetailsDoctorSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    user =  serializers.CharField(source = 'user.first_name')
    email =  serializers.CharField(source = 'user.email')
    mobile =  serializers.CharField(source = 'user.mobile')

    class Meta:
        model = DoctorAppointment
        fields = '__all__'

# class PrescriptionSerializer(serializers.Serializer):
#     medicines = serializers.ListField()  # Assuming 'medicine_ids' is a list of medicine IDs
#     instructions = serializers.CharField()
#     comments = serializers.CharField()
#     appointment = serializers.PrimaryKeyRelatedField(queryset=DoctorAppointment.objects.all())
#     user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
#     prescription_issued_date = serializers.DateField()
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = '__all__'

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines')
        prescription = Prescription.objects.create(**validated_data)
        for medicine_data in medicines_data:
            Medicine.objects.create(prescription=prescription, **medicine_data)
        return prescription

class UserDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class ViewDoctorProfileSerializer(serializers.ModelSerializer):
    user = UserDoctorSerializer()
    class Meta:
        model = Doctor
        fields = '__all__'

class EditProfileDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

    



