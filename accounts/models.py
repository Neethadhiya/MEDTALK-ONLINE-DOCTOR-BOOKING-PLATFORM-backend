from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import date

class CustomUserManager(BaseUserManager):
    def create_user(self,  first_name,  email, role, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model( first_name= first_name , email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, email, role='Admin', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(first_name, email, role, password, **extra_fields)

class Address(models.Model):
    house_street = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    pincode = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('Patient', 'Patient'),
        ('Doctor', 'Doctor'),
        ('Admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=USER_ROLES)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email =  models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    default_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    mobile = models.CharField(max_length=12, unique=True)
    otp = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    profile_created = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile','first_name']
    def __str__(self):
        return self.first_name

class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True, related_name='doctor_profile')
    specialization = models.CharField(max_length=255)
    experience = models.IntegerField()
    qualification = models.CharField(max_length=255)
    is_doctor_verified = models.BooleanField(default=False)
    online_fees = models.IntegerField(null=True)
    chat_fees = models.IntegerField(null=True)
    profileImage = models.ImageField(upload_to='profileImage/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')))
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    status = models.CharField(max_length=30, choices=(('Approved', 'Approved'), ('Rejected', 'Rejected'), ('New Request', 'New Request')), default='New Request')
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return self.user.first_name 

class DocumentImage(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='documentImages')
    documents = models.ImageField(upload_to="Documents", null=True, blank=True)
    original_filename = models.CharField(max_length=255 ,null=True)
    
    def __str__(self):
        return self.doctor.user.first_name
    
class TimeSlot(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField() 
    month = models.CharField(max_length=255)
    day = models.CharField(max_length=255) 
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"{self.month} {self.day}, {self.date.strftime('%I:%M %p')}"

class Time(models.Model):
    timeslot = models.ForeignKey('Timeslot',on_delete = models.CASCADE, related_name = 'times')
    time = models.CharField(max_length=50)

class DoctorAppointment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointment')  
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointment')
    selected_date = models.DateField()
    time =  models.CharField(max_length=300,null=True)
    comments = models.CharField(max_length=300,null=True)
    fees = models.IntegerField(null=True)
    doctor_fees = models.FloatField(null=True)
    admin_fees = models.FloatField(null=True)
    payment_status = models.BooleanField(default=False)
    consultation_type = models.CharField(max_length=300,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    status = models.CharField(max_length=30, choices=(('Completed', 'Completed'), ('Canceled', 'Canceled'), ('New Appointment', 'New Appointment')), default='New Appointment')

    def __str__(self):
        return f"Appointment for {self.user.first_name} with doctor ID {self.doctor_id} on {self.selected_date}"

class Payment(models.Model):
    stripe_id = models.CharField(max_length=100,null=True)
    appointment = models.OneToOneField(DoctorAppointment, on_delete=models.CASCADE, related_name='payment', null=True)
    payment_method = models.CharField(max_length=100, default='Stripe Payment')

    def __str__(self):
        return f"Payment for Appointment on {self.appointment.selected_date} ({self.appointment.user.first_name})"
   
class Prescription(models.Model):
    instructions = models.TextField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    appointment = models.OneToOneField(DoctorAppointment, on_delete=models.CASCADE, related_name='prescription')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='prescription',null=True)  
    def __str__(self):
        return f"Prescription for the patient {self.appointment.user.first_name}"
   
class Medicine(models.Model):
    medicine_name = models.CharField(max_length=300,null=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines',null=True)
    def __str__(self):
        return self.medicine_name

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="wallet")
    amount = models.FloatField(default=0)

    def __str__(self):
        return f"Wallet of the {self.user.first_name}"

class DoctorFees(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='doctor_fees')
    total_doctor_fees = models.FloatField(default=0)
    total_admin_fees = models.FloatField(default=0)

    def __str__(self):
        return f"Total fees for {self.doctor.name}"






