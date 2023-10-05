from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .utility import send_otp  # Import your send_otp function
from datetime import datetime,timedelta
from django.db import IntegrityError
# from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from django.contrib.auth import login, authenticate
from .utility import send_otp  # Import your send_otp function

def signup(request):
    if request.method=="POST":
        get_otp = request.POST.get('otp')
        if not get_otp:
            username = request.POST.get('username')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')
            phone_no = request.POST.get('phno')

            # Check if username field is present and not empty
            username = request.POST.get('username')
            if username is None or username == '':
                messages.error(request, "Username is required")
                return redirect('signup')

            # Check if fname field is present and not empty
            fname = request.POST.get('firstname')
            if fname is None or fname == '':
                messages.error(request, "First name is required")
                return redirect('signup')
             
             # Check if lname field is present and not empty
            lname = request.POST.get('lastname')
            if lname is None or lname == '':
                messages.error(request, "Last name is required")
                return redirect('signup')

            # Check if email field is present and not empty
            email = request.POST.get('email')
            if email is None or email == '':
                messages.error(request, "Email is required")
                return redirect('signup')

            if pass1 != pass2:
                messages.error(request, "Passwords do not match")
                return redirect('signup')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken')
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email address is already taken')
                return redirect('signup')
            
            # Validate that phone_no is not empty
            if not phone_no:
                messages.error(request, "Phone number is required")
                return redirect('signup')

            # Add the code to check if phone_no is not None and not empty
            if phone_no is not None and phone_no != '':

                myuser = User.objects.create_user(username=username, email=email, password=pass1)
                myuser.first_name = fname
                myuser.last_name = lname
                myuser.is_active = False
                myuser.save()
                otp = int(random.randint(1000,9999))
                profile = Profile(user = myuser, mobile = phone_no, otp = otp)
                profile.save()
                print(otp)
                mess=f'Hello\t{myuser.username},\nYour OTP to verify your account for AVF is {otp}\nThanks!'
                send_mail(
                "welcome to HoreHaven Verify your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [myuser.email],
                fail_silently=False
                )   
                return render(request,'authentication/signup.html',{'otp':True,'usr':myuser})
            else:
                get_email = request.POST.get('email')
                user = User.objects.get(email = get_email)
                if get_otp == Profile.objects.filter(user=user).last().otp:
                    user.is_active = True
                    user.save()
                    messages.success(request,f'Account is created for {user.email}')
                    Profile.objects.filter(user=user).delete()
                    return redirect(handlelogin)
                else:
                    messages.warning(request,f'You Entered a wrong OTP')
                    return render(request,'authentication/signup.html',{'otp':True,'usr':user})       
            
        if request.user.is_authenticated:
            return redirect('/')
        
        return render(request, 'authentication/signup.html',{'otp':False})
        

def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pass1 = request.POST.get("password")

        user = authenticate(username=username, password=pass1)

        if user is not None:

            login(request, user)
            return redirect('/')

        else:
            messages.error(request, "Username or password do no match")
            return redirect("handlelogin")

    if request.user.is_authenticated:
        return redirect('/')
    
    return render(request, 'authentication/login.html')



def otp_login(request):
    if request.method == "POST":
        get_otp = request.POST.get('otp')
        if not get_otp:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "This is not a valid email id")
                return redirect('otp_login')

            # Generate a new OTP
            otp = int(random.randint(1000, 9999))
            
            # Create or update the user's profile with the new OTP
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Ensure that the OTP field is not null
            profile.otp = otp
            profile.save()

            mess = f'Hello {user.username},\nYour OTP to login to your account for HoreHaven is {otp}\nThanks!'
            
            # Send the OTP to the user's email
            send_mail(
                "Welcome to HoreHaven - Verify your Email for Login",
                mess,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )

            return render(request, 'authentication/otp_login.html', {'otp': True, 'usr': user})
        else:
            get_email = request.POST.get('email')
            user = User.objects.get(email=get_email)
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                messages.error(request, "An OTP has not been sent to this email.")
                return redirect('otp_login')
            
            if get_otp == str(profile.otp):
                login(request, user)
                # Clear the OTP after successful login
                profile.otp = None
                profile.save()
                messages.success(request, f'Successfully logged in {user.email}')
                return redirect('/')
            else:
                messages.error(request, 'You entered a wrong OTP')
                return render(request, 'authentication/otp_login.html', {'otp': True, 'usr': user})

    if request.user.is_authenticated:
        return redirect('/')

    return render(request, 'authentication/otp_login.html')

def handlelogout(request):
    logout(request)
    return HttpResponseRedirect("/")

# Function to send an OTP to the user's email
def resend_otp(user, otp):
    mess = f'Hello {user.username},\nYour OTP to reset your password for HoreHaven account is {otp}\nThanks!'
    send_mail(
        "Welcome to HoreHaven: Verify your Email for password resetting",
        mess,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False
    )

# Function to handle the forgot password process
def forgot_password(request):
    if request.method == "POST":
        get_otp = request.POST.get('otp')
        if not get_otp:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "This is not a valid email id")
                return redirect('forgot_password')

            if user is not None:
                otp = str(random.randint(1000, 9999))
                profile, created = Profile.objects.get_or_create(user=user)
                profile.otp = otp
                profile.save()

                resend_otp(user, otp)

                return render(request, 'authentication/forgotpassword.html', {'otp': True, 'usr': user})
        else:
            get_email = request.POST.get('email')
            try:
                user = User.objects.get(email=get_email)
                profile = Profile.objects.get(user=user)
            except (User.DoesNotExist, Profile.DoesNotExist):
                messages.error(request, 'User not found or OTP not generated.')
                return render(request, 'authentication/otp_login.html', {'otp': True})

            if get_otp == profile.otp:
                profile.delete()
                request.session['reset_user_id'] = user.id
                return render(request, 'authentication/resetpassword.html', {'usr': user})
            else:
                messages.warning(request, 'You Entered a wrong OTP')
                return render(request, 'authentication/otp_login.html', {'otp': True, 'usr': user})

    if request.user.is_authenticated:
        return redirect('/')
    
    return render(request, 'authentication/forgotpassword.html')

# Function to reset a user's password
def reset_password(request):
    if request.method == "POST":
        pass1 = request.POST['password']
        pass2 = request.POST["pass"]
        user_id = request.session.get('reset_user_id')

        if pass1 == pass2 and user_id:
            try:
                user = User.objects.get(id=user_id)
                user.set_password(pass1)
                user.save()
                messages.success(request, 'Password successfully changed')
                del request.session['reset_user_id']
                return redirect('handlelogin')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
        else:
            messages.error(request, 'Passwords do not match or user ID missing.')
    
    return redirect('reset_password')  # You might want to specify the correct URL pattern here

# Function to send an OTP to a user's phone number
def send_otp_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        otp = send_otp(phone_number)  # Use your send_otp function to send OTP
        # Store the OTP, OTP expiration time, and phone number in the session
        request.session["otp"] = otp 
        otp_expiration = datetime.now() + timedelta(minutes=1)
        request.session["otp_expiration"] = otp_expiration.strftime("%Y-%m-%d %H:%M:%S")
        request.session["phone_number"]=phone_number
        return redirect('otp_verification')

    return render(request, 'authentication/send_otp.html')



# Function to verify the OTP entered by the user
def otp_verification_view(request):
    if request.method == "POST":
        user_entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")
        otp_expiration_str = request.session.get("otp_expiration")

        if stored_otp and otp_expiration_str:
            current_time = datetime.now()
            otp_expiration = datetime.strptime(otp_expiration_str, "%Y-%m-%d %H:%M:%S")  # Convert to datetime object

            if user_entered_otp == stored_otp and current_time <= otp_expiration:
                # Clear the session variables after successful OTP verification
                request.session.pop("otp", None)
                request.session.pop("otp_expiration", None)

                # Perform authentication here (e.g., log the user in) and redirect to a success page
                # Example:
                # user = authenticate(request, username=username, password=password)
                # if user is not None:
                #     login(request, user)
                #     return redirect('success_page')

                # For demonstration purposes, we'll redirect to a success page without authentication
                phone_number = request.session["phone_number"]
                user = Profile.objects.get(mobile=phone_number)
                user_object = user.user
                login(request,user_object)
                return redirect('index')

            elif current_time > otp_expiration:
                messages.error(request, 'OTP has expired. Please request a new OTP.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'authentication/otp_verification.html')







