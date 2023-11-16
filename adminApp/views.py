from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import (
    DoctorListSerializer,
    DoctorViewSerializer,
    PatientListSerializer,
    DoctorListsSerializer,
    CustomUserSerializer,
    )
from rest_framework.response import Response
from accounts.models import CustomUser,PasswordResetToken, Doctor, DocumentImage,DoctorAppointment
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
from accounts.send_otp_to_email import approve_doctor_send_mail, reject_doctor_send_mail
from django.db.models import Sum

class ShowDoctorList(APIView):
    def get(self, request):
        try:
            doctors =  Doctor.objects.all()
            serializer = DoctorListSerializer(doctors, many = True)
            response_data = {
                'success': True,
                'doctors': serializer.data,
            }
            return Response(response_data, status=200)

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)


class BlockDoctor(APIView):
    def patch(self, request, id):
        try:
            doctor = CustomUser.objects.get(id = id)
        except CustomUser.DoesNotExist:
            response_data = {
                    'error' : True,
                    'message' : 'Doctor not found',
                }        
            return Response(response_data,status = 400) 
        if doctor.is_active: 
            doctor.is_active = False
            doctor.save()
            # doctors =  Doctor.objects.all()
            # serializer = CustomUserSerializer(doctors, many = True)
            serializer = CustomUserSerializer(doctor)
            response_data = {
                    'error' : True,
                    'doctors': serializer.data,
                    'message' : f'Dr. {doctor.first_name} is blocked',
                }        
            return Response(response_data,status = 400)  
        else:
            doctor.is_active = True
            doctor.save()
            serializer = CustomUserSerializer(doctor)   
            # doctors =  Doctor.objects.all()
            # serializer = DoctorListSerializer(doctors, many = True)
            response_data = {
                        'success' : True,
                        'doctors': serializer.data,
                        'message' : f'Dr. {doctor.first_name} is active now',
                    }        
            return Response(response_data,status = 200)  
        
class ViewDoctorDetails(APIView):
    def post(self, request,id):
        try:
            user = CustomUser.objects.get(id=id)
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

class ShowPatientList(APIView):
    def get(self, request):
        try:
            patients = CustomUser.objects.filter(role='Patient')
            serializer = PatientListSerializer(patients, many=True)
            response_data = {
                'success': True,
                'patients': serializer.data,
            }
            return Response(response_data, status=200)
            
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)       

class BlockPatient(APIView):
    def patch(self, request, id):
        try:
            patient = CustomUser.objects.get(id = id)
        except CustomUser.DoesNotExist:
            response_data = {
                    'error' : True,
                    'message' : 'Patient not found',
                }        
            return Response(response_data,status = 400) 
        if patient.is_active: 
            patient.is_active = False
            patient.save()
            serializer = PatientListSerializer(patient)

            response_data = {
                    'error' : True,
                    'patients': serializer.data,
                    'message' : f'Patient {patient.first_name} is blocked',
                }        
            return Response(response_data,status = 400)  
        else:
            patient.is_active = True
            patient.save()
            serializer = PatientListSerializer(patient)
            response_data = {
                    'success' : True,
                    'patients': serializer.data,
                    'message' : f'Patient {patient.first_name} is active now',
                } 
            return Response(response_data,status = 200)  

class ApproveDoctor(APIView):
    def post(self,request,id):
        user = CustomUser.objects.get(id=id)
        doctor = Doctor.objects.get(user = user)
        doctor_user = doctor.user
        name = doctor_user.first_name
        if doctor.is_doctor_verified and doctor_user.is_doctor:
            response_data = {
                        'error' : True,
                        'message' : f"Dr. {name} has already been approved",
                    }        
            return Response(response_data,status = 400) 
        try:

            doctor.is_doctor_verified = True
            doctor_user.is_doctor = True
            doctor.status = 'Approved'
            doctor.save()
            doctor_user.save()
            serializer = DoctorListsSerializer(doctor)
            approve_doctor_send_mail(doctor_user.email,doctor_user.first_name)
            response_data = {
                            'success' : True,
                            'doctors' : serializer.data,
                            'message' : f"Dr. {name} has been approved, and an approval email has been sent to Dr. {name}.",
                        }        
            return Response(response_data,status = 200)  
        except:
            response_data = {
                            'error' : True,
                            'message' : 'An error occured ..Please try again',
                        }        
            return Response(response_data,status = 400) 
        
class RejectDoctor(APIView):
    def post(self,request,id):
        user = CustomUser.objects.get(id=id)
        doctor = Doctor.objects.get(user = user)
        doctor_user = doctor.user
        name = doctor_user.first_name
        # if doctor.is_doctor_verified == False and doctor_user.is_doctor == False:
        #     response_data = {
        #                 'error' : True,
        #                 'message' : f"Dr. {name} has already been rejected",
        #             }        
        #     return Response(response_data,status = 400) 
        try:
            doctor_user.is_doctor = False
            doctor.is_doctor_verified = False
            doctor.status = 'Rejected'
            doctor_user.save()
            doctor.save()
            serializer = DoctorListsSerializer(doctor)
            reject_doctor_send_mail(doctor_user.email,doctor_user.first_name)
            response_data = {
                            'success' : True,
                            'doctors' : serializer.data,
                            'message' : f"Dr. {name} has been rejected, and an rejection email has been sent to Dr. {name}.",
                        }        
            return Response(response_data,status = 200)  
        except:
            response_data = {
                            'error' : True,
                            'message' : 'An error occured ..Please try again',
                        }        
            return Response(response_data,status = 400) 
        

class GetAdminChart(APIView):
    def get(self, request):
        try:
            # Query doctor's monthly income data
            monthly_income_data = DoctorAppointment.objects.filter(
                payment_status=True
            ).values('selected_date__year', 'selected_date__month').annotate(
                monthly_income=Sum('admin_fees')
            ).order_by('selected_date__year', 'selected_date__month')
            
            # Prepare the data for the chart
            months = []
            admin_fees = []

            for entry in monthly_income_data:
                # Create a formatted month string (e.g., '2023-10')
                month_str = f"{entry['selected_date__year']}-{entry['selected_date__month']:02}"
                months.append(month_str)
                admin_fees.append(entry['monthly_income'])
            response_data = {
            'success': True,
            "months": months,
            "admin_fees": admin_fees,
            'message': 'An error occured',
        }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
      



        

