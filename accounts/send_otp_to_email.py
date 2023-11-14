from django.core.mail import send_mail
from django.conf import settings

def send_otp_to_email(email, otp):
    email = 'neethadhiya@gmail.com'
    subject = 'Verify your MEDTALK account'
    message = f'MEDTALK account verification OTP is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True


def reset_password_send_email(token,email):
    print("pppppppppppppppppppppppp")
    email = 'neethadhiya@gmail.com'
    subject = 'Reset your MEDTALK account password'
    message = f'Please click the link to reset your password http://localhost:5173/reset_password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def approve_doctor_send_mail(email, name):
    email = 'neethadhiya@gmail.com'
    subject = 'Congratulations!!!MedTalk Doctor Approval'
    message = f'Dear Dr. {name},\n\n' \
              'We are pleased to inform you that you have been officially approved as a doctor on MedTalk.\n\n' \
              'This certification allows you to provide consultations to patients on our platform. Your expertise and commitment to healthcare are greatly valued.\n\n' \
              'Here\'s what you can do as a certified MedTalk doctor:\n' \
              '1. Start offering consultations to patients immediately.\n' \
              '2. Ensure that your profile is complete and up to date.\n' \
              '3. Add your available time slots for both clinic and video consultations.\n' \
              '4. Promptly respond to patient inquiries and appointment requests.\n' \
              '5. Provide compassionate and high-quality care to all patients.\n\n' \
              'We are excited to have you as a member of the MedTalk community and look forward to your contributions. If you have any questions or need assistance, please feel free to contact our support team.\n\n' \
              'Once again, congratulations on becoming a certified MedTalk doctor. We wish you a successful and fulfilling journey with us.\n\n' \
              'Best regards,\n' \
              'The MedTalk Team'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)
    return True

def reject_doctor_send_mail(email, name):
    email = 'neethadhiya@gmail.com'
    subject = 'MedTalk Doctor Approval Notification'
    message = f'Dear Dr. {name},\n\n' \
              'We appreciate your interest in joining MedTalk as a certified doctor.\n\n' \
              'However, we regret to inform you that we were unable to approve your application at this time. Our certification process requires valid certificates to ensure the highest quality of care for our patients.\n\n' \
              'If you believe there may have been an error or if you have updated certificates, please feel free to resubmit your application, and we will review it promptly.\n\n' \
              'We value your dedication to healthcare and hope to welcome you to our platform in the future.\n\n' \
              'Thank you for considering MedTalk as a platform to connect with patients.\n\n' \
              'Best regards,\n' \
              'The MedTalk Team'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)
    return True   

def send_videocall_link_send_email(video_call_link, patient_email, doctor):
    patient_email = 'neethadhiya@gmail.com'
    subject = 'Join a MedTalk video call with Dr. ' + doctor
    message = f'Hello,\n\nYou can now join a video call with Dr. {doctor}.\n\nPlease click the link below to join the call:\n\n{video_call_link}\n\nBest regards,\nMedTalk Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [patient_email]

    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print("Error sending email:", str(e))
        return False