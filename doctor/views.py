from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import (    
    DoctorProfileSerializer,
    ShowDoctorSerializer,
    TimeSlotSerializer,
    TimeSerializer,
    DoctorAppointmentSerializer,
    ViewAllDoctorAppointmentSerializer,
    AppoinmentDetailsDoctorSerializer,
    PrescriptionSerializer,
    MedicineSerializer,
    ViewDoctorProfileSerializer,
    EditProfileDoctorSerializer
    )
from adminApp.serializers import (    
    PatientListSerializer,
    DoctorViewSerializer
    )
from rest_framework.response import Response
from accounts.models import (
    CustomUser,
    PasswordResetToken, 
    Doctor, 
    DocumentImage, 
    TimeSlot, 
    DoctorAppointment,
    Prescription,
    Medicine,
    DoctorFees)
from rest_framework.exceptions import AuthenticationFailed
import jwt,datetime
import uuid
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError   
from rest_framework.parsers import MultiPartParser, JSONParser
from datetime import datetime
from accounts.send_otp_to_email import send_videocall_link_send_email
import pdb
from django.db.models import Sum

class CreateDoctorProfileView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request):
        if not request.data:
            return Response({'error': 'No data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if Doctor.objects.filter(user=request.user).exists():
            response_data = {
                'error': True,
                'message': ' You have already created your profile',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        serializer = DoctorProfileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                doctor_instance = serializer.save(user=request.user)
                name = doctor_instance.user.first_name
                doctor_instance.user.profile_created = True
                doctor_instance.user.save()
                document_images = request.data.getlist("Documents")
                for document_image in document_images:
                    DocumentImage.objects.create(doctor=doctor_instance, documents=document_image)

                response_data = {
                    'success': True,
                    'user': serializer.data,
                    'message': 'Doctor profile created successfully'
                }
                return Response(response_data, status=201)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Validation failed', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ShowIsDoctor(APIView):
    def post(self,request,id):
        doctor = CustomUser.objects.get(id=id)
        profile_created = doctor.profile_created
        print(profile_created,'profile_created')
        serializer = ShowDoctorSerializer(doctor)
        response_data = {
                    'success': True,
                    'doctor' : serializer.data,
                    'profile_created' : profile_created,
                    'message': 'Doctor profile created successfully'
                }
        return Response(response_data, status=200)

# class TimeslotVideoConsult(APIView):
#     def post(self,request):
#         if not request.data:
#             response_data = {
#                 'error': True,
#                 'message': ' No data is provided',
#             }
#             return Response(response_data, status = status.HTTP_400_BAD_REQUEST) 
#         doctor = request.user.doctor_profile
#         date_str = request.data.get('date', '')
#         times_str = request.data.get('time', '').split(',')
#         print
#         date_obj = datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
#         month = date_obj.strftime('%B')
#         day = date_obj.strftime('%A')
#         formatted_date = date_obj.strftime('%Y-%m-%d')
#         if TimeSlot.objects.filter(date=formatted_date,doctor=doctor).exists():
#             response_data = {
#                     'error': True,
#                     'message': 'Timeslot already added for this date'
#                 }
#             return Response(response_data, status=400)
#         time_slot_data = {
#             'doctor' : doctor.id,
#             'date' : formatted_date,
#             'month' : month,
#             'day' : day,
          
#         }
#         time_slot_serializer = TimeSlotSerializer(data=time_slot_data)
#         if time_slot_serializer.is_valid():
#             time_slot = time_slot_serializer.save()
#             times_data = [{'time': time, 'timeslot': time_slot.id} for time in times_str]

#             time_serializer = TimeSerializer(data=times_data, many=True)
#             if time_serializer.is_valid():
#                 time_serializer.save()
#                 response_data = {
#                     'success': True,
#                     'timeslots': time_slot_serializer.data,
#                     'message': 'Time slots created successfully',
#                 }
#                 return Response(response_data, status=status.HTTP_201_CREATED)
#             else:
#                 response_data = {
#                     'error': True,
#                     'message': 'Error failed',
#                     'details': time_serializer.errors,
#                 }
#                 return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             response_data = {
#                 'error': True,
#                 'message': 'TimeSlot validation failed',
#                 'details': time_slot_serializer.errors,
#             }
#             return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class TimeslotVideoConsult(APIView):
    def post(self,request):
        if not request.data:
            response_data = {
                'error': True,
                'message': ' No data is provided',
            }
            return Response(response_data, status = status.HTTP_400_BAD_REQUEST) 
        doctor = request.user.doctor_profile
        date_str = request.data.get('date', '')
        times_str = request.data.get('time', '').split(',')
        date_obj = datetime.strptime(date_str, '%a %b %d %Y %H:%M:%S GMT%z (%Z)')
        month = date_obj.strftime('%B')
        day = date_obj.strftime('%A')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        if TimeSlot.objects.filter(date=formatted_date,doctor=doctor).exists():
            response_data = {
                    'error': True,
                    'message': 'Timeslot already added for this date'
                }
            return Response(response_data, status=400)
        time_slot_data = {
            'doctor' : doctor.id,
            'date' : formatted_date,
            'month' : month,
            'day' : day,
          
        }
        time_slot_serializer = TimeSlotSerializer(data=time_slot_data)
        if time_slot_serializer.is_valid():
            time_slot = time_slot_serializer.save()
            times_data = [{'time': time, 'timeslot': time_slot.id} for time in times_str]

            time_serializer = TimeSerializer(data=times_data, many=True)
            if time_serializer.is_valid():
                time_serializer.save()
                response_data = {
                    'success': True,
                    'timeslots': time_slot_serializer.data,
                    'message': 'Time slots created successfully',
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    'error': True,
                    'message': 'Error failed',
                    'details': time_serializer.errors,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {
                'error': True,
                'message': 'TimeSlot validation failed',
                'details': time_slot_serializer.errors,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class VideoViewAll(APIView):
    def get(self,request):
        doctor = Doctor.objects.get(user = request.user)      
        appointments = DoctorAppointment.objects.filter(doctor=doctor,consultation_type='Video Call').order_by('-updated_at')
        serializer = ViewAllDoctorAppointmentSerializer(appointments, many=True)
        response_data = {
                'success': True,
                'appointments' : serializer.data,
            }
        return Response(response_data, status=200)
    
class ChatViewAll(APIView):
    def get(self,request):
        doctor = Doctor.objects.get(user = request.user)      
        appointments = DoctorAppointment.objects.filter(doctor=doctor,consultation_type='Chat').order_by('-updated_at')
        serializer = ViewAllDoctorAppointmentSerializer(appointments, many=True)
        response_data = {
                'success': True,
                'appointments' : serializer.data,
            }
        return Response(response_data, status=200)
    
class ViewAllAppointments(APIView):
    def get(self,request):
        doctor = Doctor.objects.get(user = request.user)      
        appointments = DoctorAppointment.objects.filter(doctor=doctor).order_by('-updated_at')
        serializer = ViewAllDoctorAppointmentSerializer(appointments, many=True)
        response_data = {
                'success': True,
                'appointments' : serializer.data,
            }
        return Response(response_data, status=200)

class ViewAppointmentDetails(APIView):
    def get(self, request, id):
        try:
            appointment = DoctorAppointment.objects.get(id=id)
            serializer = AppoinmentDetailsDoctorSerializer(appointment)
            response_data = {
                'success': True,
                'appointment': serializer.data, 
            }
            return Response(response_data, status=200)
        except DoctorAppointment.DoesNotExist:
            response_data = {
                'error': True,
                'message': 'Appointment not found',
            }
            return Response(response_data, status=404)

class CancelAppointment(APIView):
    def patch(self, request, id):
        try:
            appointment = DoctorAppointment.objects.get(id=id)
        except DoctorAppointment.DoesNotExist:
            return Response(
                {'error': True,
                  'message': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if appointment.status == 'Canceled':
            return Response(
                {'error': True,
                  'message': 'Appointment is already canceled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = 'Canceled'
        appointment.save()

        response_data = {
            'success': True,
            'message': 'Appointment canceled successfully',
        }
        return Response(response_data, status=status.HTTP_200_OK)

class TodaysVideoConsult(APIView):
    def get(self,request):
        doctor = Doctor.objects.get(user = request.user)  
        todays_date = datetime.now()
        formatted_date = todays_date.strftime('%Y-%m-%d') 
        appointments = DoctorAppointment.objects.filter(doctor=doctor,selected_date=formatted_date,consultation_type = 'Video Call').order_by('-updated_at')
        serializer = ViewAllDoctorAppointmentSerializer(appointments, many=True)
        response_data = {
                'success': True,
                'appointments' : serializer.data,
            }
        return Response(response_data, status=200) 
    
class TodaysChatConsult(APIView):
    def get(self,request):
        doctor = Doctor.objects.get(user = request.user)  
        todays_date = datetime.now()
        formatted_date = todays_date.strftime('%Y-%m-%d') 
        appointments = DoctorAppointment.objects.filter(doctor=doctor,selected_date=formatted_date,consultation_type = 'Chat').order_by('-updated_at')
        serializer = ViewAllDoctorAppointmentSerializer(appointments, many=True)
        response_data = {
                'success': True,
                'appointments' : serializer.data,
            }
        return Response(response_data, status=200) 
    
class SendVideoCallLinkToPatient(APIView):
    def post(self, request, id):
        appointment = DoctorAppointment.objects.get(id=id)
        patient_email = appointment.user.email
        patient_mobile = "+91" + appointment.user.mobile
        doctor = appointment.doctor.user.first_name
        time = str(appointment.time)
        t, am_pm = time.split(' ')
        hour_str, minutes_str = t.split('.')
        
        if am_pm.lower() == 'pm' and hour_str != '12':
            hour_str = str(int(hour_str) + 12)
        
        hour = int(hour_str)
        minutes = int(minutes_str)
        
        video_call_link = request.data.get('link')
        send_videocall_link_send_email(video_call_link, patient_email, doctor)
        # pywhatkit.sendwhatmsg(
        #     patient_mobile,
        #     f'Join now for a video call with Dr. {doctor} at {hour_str}:{minutes_str}. MedTalk Team',
        #     hour,
        #     minutes
        # )

        response_data = {
            'success': True,
        }
        return Response(response_data, status=200)
    
class GetPatientInfo(APIView):
    def get(self,request,id):
        patient_info = DoctorAppointment.objects.get(id = id)
        name = patient_info.user.first_name
        email = patient_info.user.email
        patient = {'name':name,'email':email, 'id':id}
        # all_medicines = Medicine.objects.all()
        # medicine_serializer = MedicineSerializer(all_medicines, many=True)
        response_data = {
            'success': True,
            'patient_data' : patient,
            # 'medicines' : medicine_serializer.data,
        }
        return Response(response_data, status=200)

class AddPrescription(APIView):
    def post(self, request, id):
        try:
            appointment = DoctorAppointment.objects.get(id=id)
            data = request.data

            # Extract medicines data from the request
            medicines_data = data.get('medicines', [])
            instructions = data.get('instructions', '')
            comments = data.get('comments', '')
            prescription = Prescription.objects.create(
                instructions=instructions,
                comments=comments,
                appointment=appointment,
                user=appointment.user
            )
            # Create and associate Medicine objects with the Prescription
            for medicine_name in medicines_data:
                medicine = Medicine.objects.create(
                    medicine_name=medicine_name,
                    prescription=prescription
                )
            response_data = {
                'success': True,
                'message': "Prescription added successfully"
            }
            return Response(response_data, status=201)

        except DoctorAppointment.DoesNotExist:
            return Response({'success': False, 'error': 'Appointment not found'}, status=404)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

class CheckPaymentStatus(APIView):
    def get(self, request, id):
        appointment = DoctorAppointment.objects.get(id = id)
        if appointment.payment_status == False:
            response_data = {
                'error': True,
                'message' : 'Patient has not completed the payment'
            }
            return Response(response_data, status=400)
        else:
            response_data = {
                'success' : True,
                'message' : 'Patient has completed the payment',
            }
            return Response(response_data, status= 200)
        
class ViewDoctorProfileView(APIView):
   
   def get(self, request):
        try:
            user = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            response_data = {
                        'error' : True,
                        'message' : 'Doctor not found.',
                    }        
            return Response(response_data,status = 400) 
        
        doctor = Doctor.objects.filter(user=user).first()
        if not doctor:
            response_data = {
                        'error' : True,
                        'message' : 'Doctor not found.',
                    }        
            return Response(response_data,status = 400) 
        document_images = DocumentImage.objects.filter(doctor=doctor)
        serializer = DoctorViewSerializer(doctor, context={'document_images': document_images})
        response_data = {
            'success': True,
            'message': 'success',
            'doctor': serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
   
class EditDoctorProfileView(APIView):
    def put(self, request):
        try:
            doctor = Doctor.objects.get(user=request.user) 
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EditProfileDoctorSerializer(doctor, data=request.data, partial=True)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            for key, value in validated_data.items():
                setattr(doctor, key, value)
            doctor.save()
            response_data = {
            'success': True,
            'message': 'Your profile updated successfully',
        }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {
            'error': True,
            'message': 'An error occured',
        }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class GetDoctorChartView(APIView):
    def get(self, request):
        try:
            doctor_instance = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            appointment_count = DoctorAppointment.objects.filter(doctor=doctor_instance).count()
            # Query doctor's monthly income data
            monthly_income_data = DoctorAppointment.objects.filter(
                doctor=doctor_instance,
                payment_status=True
            ).values('selected_date__year', 'selected_date__month').annotate(
                monthly_income=Sum('doctor_fees')
            ).order_by('selected_date__year', 'selected_date__month')
            doctor_fees_instance = DoctorFees.objects.get(doctor=doctor_instance)
            total_doctor_fees = doctor_fees_instance.total_doctor_fees
            # Prepare the data for the chart
            months = []
            doctor_fees = []
            for entry in monthly_income_data:
                # Create a formatted month string (e.g., '2023-10')
                month_str = f"{entry['selected_date__year']}-{entry['selected_date__month']:02}"
                months.append(month_str)
                doctor_fees.append(entry['monthly_income'])
            response_data = {
            'success': True,
            "months": months,
            "doctor_fees": doctor_fees,
            "appointment_count": appointment_count,
            'message': 'An error occured',
            'total_doctor_fees' : total_doctor_fees,
        }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      









