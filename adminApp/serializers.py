from rest_framework import serializers
from accounts.models import CustomUser,Doctor, TimeSlot , DocumentImage

class DocumentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImage
        fields = ('documents',)

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class DoctorListSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    class Meta:
        model = Doctor
        fields = '__all__'

class DoctorViewSerializer(serializers.ModelSerializer):
    user_mobile = serializers.IntegerField(source='user.mobile')
    user_first_name = serializers.CharField(source='user.first_name')
    user_email = serializers.EmailField(source='user.email')
    documentImages = DocumentImageSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        document_images = self.context.get('document_images', [])
        data['documentImages'] = DocumentImageSerializer(document_images, many=True).data
        return data

class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class DoctorListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

