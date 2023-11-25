from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import (    
   DoctorListsSerializer,
   TimeSlotSerializer,
   TimeSerializer,
   AppointmentSerializer,
   AppointmentDetailsSerializer,
   MedicineSerializer,
PrescriptionSerializer,
PatientAppointmentSerializer,
PatientViewSerializer,
DoctorFindSerializer
    )
from rest_framework.response import Response
from accounts.models import (
    CustomUser,
    PasswordResetToken, 
    Doctor,
    DocumentImage,
    TimeSlot,
    Time,
    DoctorAppointment,
    Payment,
    Prescription,
    Medicine,
    Wallet,
    DoctorFees,
    )
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
from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
# from stripe_webhook import construct_event
import os
from rest_framework.exceptions import NotFound
from rest_framework import generics


stripe.api_key = settings.STRIPE_SECRET_KEY

class ShowDoctorList(APIView):
    def get(self, request):
        try:
            doctors = Doctor.objects.filter(status='Approved',is_doctor_verified =True, user__is_active=True).prefetch_related('time_slots__times')
            serializer = DoctorListsSerializer(doctors, many=True)
            response_data = {
                'success': True,
                'doctors': serializer.data,
            }
            return Response(response_data, status=200)
        
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

class ShowDoctorsList(APIView):
    def get(self, request):
        try:
            doctors = Doctor.objects.filter(status='Approved',is_doctor_verified =True, user__is_active=True).prefetch_related('time_slots__times')
            serializer = DoctorListsSerializer(doctors, many=True)
            response_data = {
                'success': True,
                'doctors': serializer.data,
            }
            return Response(response_data, status=200)
        
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)
        
class BookNowShowTimeslot(APIView):
    def post(self, request, id):
        try:
            doctor = Doctor.objects.select_related('user').get(id=id)
        except Doctor.DoesNotExist:
            response_data = {
                'error': True,
                'message': 'Doctor not found',
            }
            return Response(response_data, status=400)

        time_slots = TimeSlot.objects.filter(doctor=doctor)
        if not time_slots:
            response_data = {
                'error': True,
                'message': 'No time slots found for this doctor',
            }
            return Response(response_data, status=400)

        serializer = TimeSlotSerializer(time_slots, many=True)
        doctor_data = {
            'specialization': doctor.specialization,
            'experience': doctor.experience,
            'qualification': doctor.qualification,
            'profileImage': doctor.profileImage.url if doctor.profileImage else '', 
            'location':doctor.location,
            'online_fees':doctor.online_fees,
            'chat_fees':doctor.chat_fees,
            'city':doctor.city,
            'user': {
                'username': doctor.user.username,
                'email': doctor.user.email,
                'first_name': doctor.user.first_name,
            }
        }
        response_data = {
            'success': True,
            'doctor': doctor_data,
            'time_slots': serializer.data,
        }
        return Response(response_data, status=200)

class GetTimeSlot(APIView):
    def post(self, request):
        date = request.data.get('date')
        if not date:
            response_data = {
                'error': True,
                'message': 'No date provided',
            }
            return Response(response_data, status=400)
        timeslots = TimeSlot.objects.filter(date=date)
        times_for_date = []
        for timeslot in timeslots:
            times = Time.objects.filter(timeslot = timeslot)
            time_serializer = TimeSerializer(times, many = True)
            times_for_date.append({
                'times': time_serializer.data,
            })
        response_data = {
            'success': True,
            'timeslots': times_for_date,
            'message': 'Times for the specified date retrieved successfully',
        }

        return Response(response_data, status=200)
    
class BookAppoinment(APIView):
    def post(self, request):
        if not request.data:
            response_data = {
                'error': True,
                'message': 'No date provided',
            }
            return Response(response_data, status=400)
        user = request.user
        selected_date = request.data.get('selectedDate')
        doctorId = request.data.get('doctorId')
        time_id = request.data.get('time_id')
        comments = request.data.get('comments')
        timeslot_id = request.data.get('timeslot_id')
        consultation_value = request.data.get('consultation_value')
        doctor = Doctor.objects.get(id=doctorId)
        if consultation_value=='Video':
            fee = doctor.online_fees
            consultation_mode = 'Video Call'
            admin_fees = (fee*10)/100
            doctor_fees = fee-admin_fees
        times = Time.objects.get(id=time_id)
        selected_time = times.time
        
        existing_appointment = DoctorAppointment.objects.filter(
            user = user,
            selected_date = selected_date,
            doctor = doctor,
            time = selected_time,
        ).exclude(status='Canceled')
        if existing_appointment:
            response_data = {
                'error': True,
                'message': 'An appointment with the same criteria already exists.',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        doctor_fees_instance, created = DoctorFees.objects.get_or_create(doctor=doctor)
        doctor_fees_instance.total_doctor_fees += doctor_fees
        doctor_fees_instance.total_admin_fees += admin_fees  # Adding admin fees to DoctorFees
        doctor_fees_instance.save()
        appointment = DoctorAppointment(
            user = user,
            selected_date = selected_date,
            doctor = doctor,
            time = selected_time,
            comments = comments,
            fees = fee,
            doctor_fees = doctor_fees,
            admin_fees = admin_fees,
            consultation_type = consultation_mode,
        )
        appointment.save()
        times.delete()
        time_slots_to_delete = TimeSlot.objects.filter(times__isnull = True)
        time_slots_to_delete.delete()
        appointment_id = appointment.id
        response_data = {
            'success': True,
            'appointment_id': appointment_id,
            'message': 'Appointment booked successfully',
        }
        return Response(response_data, status=200)
    
class GetAppointmentDetails(APIView):
    def post(self,request,id):
        appointment = DoctorAppointment.objects.get(id=id)
        serializer = AppointmentSerializer(appointment)
        response_data = {
            'success': True,
            'appointment_data' : serializer.data,
            'message': 'Appointment booked successfully',
        }
        return Response(response_data, status=200)

class ConfigView(APIView):
    def get(self, request):
        publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        if not publishable_key:
            return Response(
                {'error': 'Stripe publishable key not found'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({'publishableKey': publishable_key}, status=status.HTTP_200_OK)


class StripeCheckoutView(APIView):
    def post(self, request, id):
        try:
            payment = DoctorAppointment.objects.get(id=id)
            user = CustomUser.objects.get(id=request.user.id)
            email = user.email
            payment_amount = payment.fees
            intent = stripe.PaymentIntent.create(
                amount=payment_amount*100,  # Amount in cents
                currency='inr',  # Replace with 'inr'
                payment_method_types=['card'],
                 
                description="Thank you for the booking!",
                receipt_email="neethadhiya@gmail.com",
            )
            response_data = {
                'paymentAmount': payment_amount,
                'clientSecret': intent.client_secret,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.db import transaction

class PaymentSuccess(APIView):
    @transaction.atomic
    def post(self, request):
        stripe_id = request.data.get("paymentIntentId")
        appointment_id = request.data.get("appointmentId")
        try:
            appointment = DoctorAppointment.objects.get(id=appointment_id)
            appointment.payment_status = True
            appointment.save()
            Payment.objects.create(
                stripe_id=stripe_id,
                appointment=appointment
            )

            response_data = {
                'success': True,
                'message': 'Payment added successfully',
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except DoctorAppointment.DoesNotExist:
            response_data = {
                'error': True,
                'message': 'Something went wrong',
            }
            return Response(response_data, status=400)
        except Exception as e:
            response_data = {
                'error': str(e),
            }
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ViewPatientPrescriptonView(APIView):
    def get(self, request, id):
        try:
            appointment = get_object_or_404(DoctorAppointment, id=id)
            prescription = get_object_or_404(Prescription, appointment=appointment)
            medicines = Medicine.objects.filter(prescription=prescription)
            
            prescription_serializer = PrescriptionSerializer(prescription)
            response_data = {
                'success': True,
                'prescription_data': prescription_serializer.data,
            }
            return Response(response_data, status=200)
        except NotFound:
            response_data = {
                'success': False,
                'message': 'Prescription not found',
            }
            return Response(response_data, status=404)
    

class ViewPatientAppointmentView(APIView):
    def get(self, request):
        try:
            appointment = DoctorAppointment.objects.filter(user=request.user.id).order_by('-created_at')
            appointment_serializer = PatientAppointmentSerializer(appointment, many=True)
            response_data = {
                'success': True,
                'appointments': appointment_serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except DoctorAppointment.DoesNotExist:
            response_data = {
                'success': False,
                'message': 'No appointments found for the patient.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'success': False,
                'message': str(e),  
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PatientProfileView(APIView):
    def get(self, request):
        try:
            user = CustomUser.objects.get(id=request.user.id)
            serializer = PatientViewSerializer(user)
            response_data = {
                'success': True,
                'patient': serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            response_data = {
                'success': False,
                'message': 'No user profile found.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'success': False,
                'message': str(e),  
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.db.models import Q
        
class SearchDoctorsList(APIView):
    def get(self, request, format=None):
        search = request.query_params.get('search', '').strip()
        
        doctors = Doctor.objects.filter(
            Q(specialization__icontains=search) | Q(city__icontains=search),
            status='Approved',
            is_doctor_verified=True,
            user__is_active=True 
        )
        
        if not doctors.exists():
            return Response({'message': 'No search results found', 'data': []}, status=200)
        
        serializer = DoctorFindSerializer(doctors, many=True)
        return Response({'data': serializer.data})
    
class UserCancelAppointment(APIView):
    def delete(self, request):
        appointment_id = request.data.get('id')
        try:
            appointment = DoctorAppointment.objects.get(id=appointment_id)
            if appointment.status == 'Canceled':
                response_data = {
                'error': True,
                'message': 'Appointment already canceled.',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            try:
                prescription = Prescription.objects.get(appointment=appointment)
                response_data = {
                    'error': True,
                    'message': 'Appointment already completed.',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            except Prescription.DoesNotExist:
                pass 


            today_date = timezone.now().date()
            current_time = timezone.now().time()
            appointment_time_str = appointment.time
            appointment_datetime = datetime.strptime(appointment_time_str, '%I.%M %p').time()
            if appointment.selected_date < today_date:
                response_data = {
                    'error': True,
                    'message': 'Appointment has already occurred. Cannot cancel.',
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            time_difference = datetime.combine(today_date, appointment_datetime) - datetime.combine(today_date, current_time)
            print("Appointment Selected Date:", appointment.selected_date)
            print("Today's Date:", today_date)
            print("Current Time:", current_time)
            print("Appointment Time:", appointment_datetime)
            print("Time Difference:", time_difference)
            if time_difference <= timedelta(hours=1):
                response_data = {
                    'error': True,
                    'message': 'Appointment cancellation period has expired. Cannot cancel now.',
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            payment_amount = appointment.fees
            doctor_refund = (payment_amount * 90) / 100
            admin_refund = (payment_amount * 10) / 100

            # Adjust fees in the appointment
            appointment.status = 'Canceled'  # Update appointment status
            appointment.payment_status = False
            appointment.save()
            user = appointment.user
            try:
                user_wallet = Wallet.objects.get(user=user)
            except Wallet.DoesNotExist:
                user_wallet = Wallet.objects.create(user=user)
            
            user_wallet.amount += doctor_refund  # Refund 90% to user's wallet
            user_wallet.save()

            doctor = appointment.doctor

            doctor_fees_instance = DoctorFees.objects.get(doctor=doctor)
            doctor_fees_instance.total_doctor_fees -= doctor_refund
            doctor_fees_instance.total_admin_fees -= admin_refund
            doctor_fees_instance.save()

            doctor_fees_instance.total_doctor_fees += (payment_amount * 5) / 100
            doctor_fees_instance.total_admin_fees += (payment_amount * 5) / 100
            doctor_fees_instance.save()

            timeslot = TimeSlot.objects.filter(doctor=appointment.doctor, date=appointment.selected_date).first()
            if timeslot:
                with transaction.atomic():
                    # Create a new Time entry with the canceled time for the TimeSlot
                    canceled_time = appointment.time
                    Time.objects.create(timeslot=timeslot, time=canceled_time)
                       
            response_data = {
                'success': True,
                'message': 'Appointment canceled successfully.',
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except DoctorAppointment.DoesNotExist:
            response_data = {
                'error': True,
                'message': 'Appointment does not exist.',
                }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

class WalletPayment(APIView):
    def post(self, request, id):
        try:
            appointment = DoctorAppointment.objects.get(id=id)
            user = appointment.user
            fees = appointment.fees
            wallet = Wallet.objects.get(user=user)

            if fees <= wallet.amount:
                wallet.amount -= fees
                wallet.save()
                appointment.payment_status = True
                appointment.save()
                Payment.objects.create(
                payment_method = 'Wallet Payment',
                appointment=appointment
                )
                response_data = {
                    'success': True,
                    'message': 'Payment successful. Amount deducted from wallet.',
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = {
                    'error': True,
                    'message': 'Payment failed. Insufficient balance in wallet.',
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except DoctorAppointment.DoesNotExist:
            response_data = {
                    'error': True,
                    'message': 'Appointment does not exist.',
                }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Wallet.DoesNotExist:
            response_data = {
                    'error': True,
                    'message': 'Wallet not found for this user.',
                }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any other unexpected errors
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ShowWalletBalance(APIView):
    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            print(wallet.amount, 'kkkkkkkkkkkkkkkkkk')

            response_data = {
                'success': True,
                'message': 'Wallet balance retrieved successfully.',
                'balance': wallet.amount  # Include the wallet balance in the response
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Wallet.DoesNotExist:
            # Handle the case when the wallet for the user does not exist
            raise NotFound("Wallet not found for this user")

        except Exception as e:
            # Catch any other unexpected errors
            print("An error occurred:", e)
            return Response({'error': 'An error occurred while fetching the wallet.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)