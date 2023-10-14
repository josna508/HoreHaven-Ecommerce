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
    # Check if the HTTP request method is POST
    if request.method == "POST":
        # Check if the 'otp' parameter is in the POST request
        get_otp = request.POST.get('otp')
        if not get_otp:
            # If 'otp' is not present in the POST data, proceed with user registration

            # Get data from the POST request
            username = request.POST.get('username')
            fname = request.POST.get('firstname')
            lname = request.POST.get('lastname')
            email = request.POST.get('email')
            pass1 = request.POST.get('password')
            pass2 = request.POST.get('confirmpassword')
            phone_no = request.POST.get('phone')

            # Check if username, first name, last name, email, and passwords are provided and not empty
            if not username.strip():
                messages.error(request, "Username is required")
                return redirect('signup')

            if not fname.strip():
                messages.error(request, "First name is required")
                return redirect('signup')

            if not lname.strip():
                messages.error(request, "Last name is required")
                return redirect('signup')

            if not email.strip():
                messages.error(request, "Email is required")
                return redirect('signup')

            if pass1 != pass2:
                messages.error(request, "Passwords do not match")
                return redirect('signup')

            # Check if the username and email are already taken
            if User.objects.filter(username=username).exists():
                messages.error(request, 'This username is already taken')
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email address is already taken')
                return redirect('signup')

            # Check if the phone number is already associated with a profile
            if Profile.objects.filter(mobile=phone_no).exists():
                messages.error(request, 'This Phone Number is already taken')
                return redirect('signup')

            # Create a new user with the provided information
            myuser = User.objects.create_user(username=username, email=email, password=pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = True
            myuser.save()

            # Generate a random OTP (One-Time Password)
            otp = int(random.randint(1000, 9999))

            # Create a new Profile for the user with the OTP
            profile = Profile(user=myuser, mobile=phone_no, otp=otp)
            profile.save()

            # Print the OTP (for debugging purposes)
            print(otp)

            # Compose and send an email with the OTP to the user
            mess = f'Hello\t{myuser.username},\nYour OTP to verify your account for HoreHaven is {otp}\nThanks!'
            send_mail(
                "Welcome to HoreHaven. Verify your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [myuser.email],
                fail_silently=False
            )

            # Render the template with OTP input field for user verification
            return render(request, 'authentication/otp_login.html', {"otp":True, 'usr':myuser})
        else:
            # If 'otp' is present in the POST data, it means the user is verifying their account

            # Get the email and user associated with the email
            get_email = request.POST.get('email')
            user = User.objects.get(email=get_email)

            # Check if the entered OTP matches the OTP stored in the user's profile
            if get_otp == Profile.objects.filter(user=user).last().otp:
                user.is_active = True
                print(user.is_active, 'useeeeeeeeeeeeeeeeeeeactive')
                user.save()
                messages.success(request, f'Account is created for {user.email}')
                # Delete the profile entry as it is no longer needed
                Profile.objects.filter(user=user).delete()
                return redirect('handlelogin')
            else:
                messages.warning(request, f'You Entered a wrong OTP')
                return render(request, 'authentication/signup.html', {'otp': True, 'usr': user})

    # Redirect the user to the homepage if they are already authenticated
    if request.user.is_authenticated:
        return redirect('/')

    # Render the initial registration form
    return render(request, 'authentication/signup.html', {'otp': False})

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
    # Check if the HTTP request method is POST
    if request.method == "POST":
        # Check if the 'otp' parameter is in the POST request
        get_otp = request.POST.get('otp')
        if not get_otp:
            # If 'otp' is not present in the POST data, proceed with OTP generation and email sending

            # Get the email address from the POST request
            email = request.POST.get('email')

            try:
                # Try to fetch the user with the given email address
                user = User.objects.get(email=email)
            except:
                # If no user with that email exists, show an error message and redirect to the same page
                messages.error(request, f"This is not a valid email id")
                return redirect(otp_login)

            if user is not None:
                # Generate a random OTP (One-Time Password)
                otp = int(random.randint(1000, 9999))

                # Create a new Profile entry for the user with the generated OTP
                profile = Profile(user=user, otp=otp)
                profile.save()

                # Compose and send an email with the OTP to the user
                mess = f'Hello\t{user.username},\nYour OTP to login to your account for  HoreHaven is {otp}\nThanks!'
                send_mail(
                    "Welcome to  HoreHaven. Verify your Email for login",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False
                )

                # Render the template with OTP input field for user login
                return render(request, 'authentication/otp_login.html', {'otp': True, 'usr': user})
        else:
            # If 'otp' is present in the POST data, it means the user is trying to log in

            # Get the email address and user associated with the email
            get_email = request.POST.get('email')
            user = User.objects.get(email=get_email)

            # Check if the entered OTP matches the OTP stored in the user's profile
            if get_otp == Profile.objects.filter(user=user).last().otp:
                # Log the user in
                login(request, user)
                messages.success(request, f'Successfully logged in as {user.email}')

                # Delete the profile entry as it is no longer needed
                Profile.objects.filter(user=user).delete()
                return redirect('index')
            else:
                # Show a warning message for an incorrect OTP
                messages.warning(request, f'You Entered a wrong OTP')
                return render(request, 'authentication/otp_login.html', {'otp': True, 'usr': user})

    # Redirect the user to the homepage if they are already authenticated
    if request.user.is_authenticated:
        return redirect('/')

    # Render the initial OTP login form
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







