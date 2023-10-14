from django.shortcuts import redirect, render
from user_profile.models import UserAddress, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from order.models import Wallet
# Create your views here.

@login_required(login_url='handlelogin')
def add_user_address(request):
    if request.method == "POST":
       fname = request.POST['fname']
       lname = request.POST['lname']
       ph_no = request.POST['ph_no']
       house = request.POST['house']
       city = request.POST['city']
       state = request.POST['state']
       country = request.POST['country']
       user=request.user

       print('entered her===========================')
       


       UserAddress.objects.create(
            fname = fname,
            lname = lname,
            contact_number = ph_no,
            house_name = house,
            user=user,
            city = city,
            state = state,
            country = country,

       ).save()

       return redirect('placeorder')


@login_required(login_url='handlelogin')
def profile(request):
     if request.user.is_authenticated:
          user_address = None
          try:
              user_profile = UserProfile.objects.get(user=request.user)
              user_address = UserAddress.objects.filter(user=request.user)
          except:
              user_profile=UserProfile.objects.create(
                  user = request.user
              ).save()
          context = {
              'user_profile':user_profile,
              'addresses' : user_address,
          }
          return render(request, 'profile.html', context)
@login_required(login_url='handlelogin')     
def edit_profile(request):
    if request.method == 'POST':
        # Get form data from POST request
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')

        # Check if the email is already in use by another user
        if User.objects.filter(email=email).exclude(username=request.user.username).exists():
            messages.error(request, 'This email address is already taken')
            return redirect('edit_profile')

        # Update the user's information
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, 'Your details updated')
        return redirect('profile')

    # If it's not a POST request, you can display a form to edit the user's details.
    # You can retrieve the user's information and pass it to the template for editing.
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='handlelogin')
def edit_address(request, id):
    if request.method == "POST":
       name = request.POST['fname']
       ph_no = request.POST['no']
       house = request.POST['house']
       city = request.POST['city']
       state = request.POST['state']
       country = request.POST['country']


       UserAddress.objects.filter(id=id).update(
            fullname = name,
            contact_number = ph_no,
            house_name = house,
            city = city,
            state = state,
            country = country,

       )
       messages.success(request, 'saved changes')
       return redirect(edit_address, id)
    address = UserAddress.objects.get(id=id)
    context = {
        'address' : address,
    }
    return render(request, "address.html", context)

@login_required(login_url='handlelogin')
def add_address(request):
    if request.method == "POST":
       name = request.POST['name']
       ph_no = request.POST['ph_no']
       house = request.POST['house']
       city = request.POST['city']
       state = request.POST['state']
       country = request.POST['country']
       


       UserAddress.objects.create(
            fullname = name,
            contact_number = ph_no,
            house_name = house,
            city = city,
            state = state,
            country = country,
            user = request.user

       ).save()
       messages.success(request, 'Your details successfully added')
       return redirect(profile)
       
    return render(request, 'add_address.html')

def wallet(request):
    user = request.user
    print(user, 'yjgjysgfuhkesjughhukhe')
    wallet, _ = Wallet.objects.get_or_create(user=user)
    print(wallet,'hgsyuegfuyguerukhsuiefhukesgudsgfujwkgwajh')
    context = {
        'wallet':wallet
    }
    return render(request, 'wallet.html', context)