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
    if request.method == "POST":
        image = ''
        try:
            image = request.FILES['image']
            user_profile = UserProfile.objects.filter(user=request.user).first()
            user_profile.profile_picture = image
            user_profile.save()
        except:
             pass
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST["country"]
        phone = request.POST["phone"]

        if User.objects.filter(email=email).exists() and email != request.user.email:
                messages.error(request, 'This email address is already taken')
                return redirect(edit_profile)
        
        user_profile = UserProfile.objects.get(user=request.user)
        user = request.user
        user.first_name = fname
        user.last_name = lname
        user.email = email
        user.save()
        user_profile.address = address
        user_profile.city = city
        user_profile.state = state
        user_profile.country = country
        user_profile.phone_no = phone
        user_profile.save()

        messages.success(request, 'Your details updated')
        return redirect(profile)


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
    wallet = Wallet.objects.get(user=user)
    print(wallet,'hgsyuegfuyguerukhsuiefhukesgudsgfujwkgwajh')
    context = {
        'wallet':wallet
    }
    return render(request, 'wallet.html', context)