from rest_framework import serializers
from .models import CustomUser,Doctor, TimeSlot

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'email', 'mobile','password','role']
        extra_kwargs = { 
            'password' : {'write_only':True}
        }
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        user = CustomUser(**validated_data)
        user.set_password(password) 
        user.save()
        return user
    
class UserInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    mobile = serializers.CharField()
    role = serializers.CharField()
    is_doctor = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name','mobile','role', 'is_doctor' )

class LoginSerilalizer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = CustomUser
        fields = ['email','password']
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'mobile', 'role']




