from datetime import date, datetime
from multiprocessing.sharedctypes import Value
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
import random
from time import sleep
from . import util
from .models import Address, Person


#########################################
############## Login ####################
#########################################
@ensure_csrf_cookie
def homepage(request):
    if request.user.is_authenticated and request.method == "GET":
        return redirect('/')
    elif request.user.is_authenticated and request.method == "POST":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    request.session.pop("register", False)
    request.session.pop("recover", False)
    
    if request.method == "GET":
        try:
            sitetitle = settings.SITE_TITLE
        except AttributeError:
            sitetitle = 'blackparis'
        
        q = dict(request.GET)
        if "next" in q:
            request.session["next"] = q["next"][0]
        
        return render(
            request,
            "authentication/login.html",
            {"sitetitle": sitetitle}
        )
    
    username = request.POST["email"]
    password = request.POST["password"]
    if not username or not password:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    username = username.strip()
    user = User.objects.filter(Q(username=username) | Q(email=username)).first()
    if user and authenticate(request, username=user.username, password=password):
        login(request, user)
        next = request.session.pop("next", '/')
        return JsonResponse({"success": True, "next": next})
    
    return JsonResponse({"success": False, "message": "Invalid Credentials"})


#########################################
############## Logout ###################
#########################################
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('authentication:homepage'))


#########################################
############## Register #################
#########################################
def register(request):
    if request.user.is_authenticated or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    username = request.POST["username"]
    email = request.POST["email"]
    password = request.POST["password"]
    confirmPassword = request.POST["confirmPassword"]
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]

    if not username or not email or not password or not confirmPassword or not first_name or not last_name:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    if password != confirmPassword:
        return JsonResponse({"success": False, "message": "Passwords Don't Match"})
    
    username = username.strip().lower()
    email = email.strip()
    first_name = first_name.strip().lower().title()
    last_name = last_name.strip().lower().title()
    
    if not settings.AUTHENTICATION_DEBUG and not util.validate_password(password):
        return JsonResponse({"success": False, "message": "Invalid Password"})
    if not util.validate_email(email):
        return JsonResponse({"success": False, "message": "Invalid Email Address"})
    if not util.validate_username(username):
        return JsonResponse({"success": False, "message": "Invalid Username"})
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username Already Exists"})
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "This email is associated with another account."})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {username} - Email: {email} - Code: {code}")
    else:
        try:
            send_mail(
                'Verification Code',
                f'Your verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except:
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["register"] = {
        "username": username,
        "email": email,
        "password": password,
        "verified": False,
        "code": code,
        "first_name": first_name,
        "last_name": last_name
    }
    request.session.modified = True
    return JsonResponse({"success": True, "email": email})


def cancelregistration(request):
    if request.session.get("register", False):
        request.session["register"].clear()
        request.session.pop("register", False)
    return JsonResponse({"success": True})


def verifyRegistrationCodeResend(request):
    if request.user.is_authenticated or not request.session.get("register", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    code = str(random.randint(100000, 999999))
    email = request.session["register"]["email"]
    username = request.session["register"]["username"]
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {username} - Email: {email} - Code: {code}")
    else:
        try:
            send_mail(
                'New Verification Code',
                f'Your new verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except:
            request.session["register"].clear()
            request.session.pop("register", False)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["register"]["code"] = code
    request.session.modified = True
    return JsonResponse({"success": True})


def verifyregistration(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("register", False):
        return JsonResponse({"success": False, "message": "Invalid Request", "restart": False})
    code = request.POST["code"]
    if not code:
        return JsonResponse({"success": False, "message": "Incomplete Form", "restart": False})
    if code != request.session["register"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code", "restart": False})
    
    if User.objects.filter(username=request.session["register"]["username"]).exists():
        request.session["register"].clear()
        request.session.pop("register", False)
        return JsonResponse({
            "success": False,
            "message": "This username already exists. Please try again with a different username.",
            "restart": True
        })
    
    if User.objects.filter(email=request.session["register"]["email"]).exists():
        request.session["register"].clear()
        request.session.pop("register", False)
        return JsonResponse({
            "success": False,
            "message": "This email is associated with another account. Please try again with a different email address.",
            "restart": True
        })
    
    try:
        user = User.objects.create_user(
            request.session["register"]["username"],
            request.session["register"]["email"],
            request.session["register"]["password"]
        )
        user.first_name = request.session["register"]["first_name"]
        user.last_name = request.session["register"]["last_name"]
        user.save()

        person = Person.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            username=user.username
        )
    except:
        request.session["register"].clear()
        request.session.pop("register", False)
        return JsonResponse({
            "success": False,
            "message": "Something went wrong. Please try again later.",
            "restart": True
        })

    
    request.session["register"].clear()
    request.session.pop("register", False)

    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Registration Successful',
                'You have successfully registered your account.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except:
            pass
    return JsonResponse({"success": True})


#########################################
############## Recover ##################
#########################################
def recover(request):
    if request.user.is_authenticated or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    username = request.POST["email"]
    if not username:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    username = username.strip()
    user = User.objects.filter(Q(username=username) | Q(email=username)).first()
    if not user or not user.is_active:
        return JsonResponse({"success": False, "message": "Invalid Credentials"})
    
    email = user.email
    code = str(random.randint(100000, 999999))

    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {user.username} - Email: {email} - Code: {code}")
    else:
        try:
            send_mail(
                'Verification Code',
                f'Your verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except:
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["recover"] = {
        "user_id": user.id,
        "email": email,
        "username": user.username,
        "verified": False,
        "code": code
    }
    request.session.modified = True

    if username == user.username:
        data = util.encryptemail(email)
    else:
        data = email

    return JsonResponse({"success": True, "data": data})


def cancelrecovery(request):
    if request.session.get("recover", False):
        request.session["recover"].clear()
        request.session.pop("recover", False)
    return JsonResponse({"success": True})


def verifyRecoverCodeResend(request):
    if request.user.is_authenticated or not request.session.get("recover", False):
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = str(random.randint(100000, 999999))
    email = request.session["recover"]["email"]
    username = request.session["recover"]["username"]
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {username} - Email: {email} - Code: {code}")
    else:
        try:
            send_mail(
                'New Verification Code',
                f'Your new verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except:
            request.session["recover"].clear()
            request.session.pop("recover", False)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["recover"]["code"] = code
    request.session.modified = True
    
    return JsonResponse({"success": True})


def verifyrecovery(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("recover", False) or request.session["recover"]["verified"]:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    
    if not code:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if code != request.session["recover"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    request.session["recover"]["verified"] = True
    request.session.modified = True
    return JsonResponse({"success": True})
    

def verifyChangePassword(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("recover", False) or not request.session["recover"]["verified"]:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    password1 = request.POST["password1"]
    password2 = request.POST["password2"]

    if not password1 or not password2:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    if password1 != password2:
        return JsonResponse({"success": False, "message": "Passwords Don't Match"})
    
    if not settings.AUTHENTICATION_DEBUG and not util.validate_password(password1):
        return JsonResponse({"success": False, "message": "Invalid Password"})
    
    try:
        user = User.objects.get(id=request.session["recover"]["user_id"])
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user.set_password(password1)
    user.save()
    request.session["recover"].clear()
    request.session.pop("recover", False)
    email = user.email
    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                'Your password was just changed.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=True,
            )
        except:
            pass
    return JsonResponse({"success": True})


#########################################
############## Account ##################
#########################################
@login_required
@ensure_csrf_cookie
def account(request):
    if request.user.is_superuser or request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    if request.method == "GET":
        try:
            sitetitle = settings.SITE_TITLE
        except AttributeError:
            sitetitle = 'blackparis'
        
        request.session.pop("editEmail", False)
        return render(
            request,
            'authentication/account.html',
            {'sitetitle': sitetitle}
        )
    
    user = User.objects.filter(username=request.user.username).first()
    if not user:
        logout(request)
        return JsonResponse({"success": False})
    
    address = user.person.address.all()
    a = []
    for addr in address:
        a.append({
            "id": addr.id,
            "primary": addr.primary,
            "first_name": addr.first_name,
            "last_name": addr.last_name,
            "email": addr.email,
            "mobile": addr.mobile,
            "homephone": addr.homephone,
            "address1": addr.address1,
            "address2": addr.address2,
            "landmark": addr.landmark,
            "pincode": addr.pincode,
            "city": addr.city,
            "state": addr.state,
            "country": addr.country,
            "user_id": user.id,
            "person_id": user.person.id
        })
    
    g = user.person.gender
    if g == 'F':
        gender = "Female"
    elif g == 'M':
        gender = "Male"
    elif g == 'N':
        gender = "Non Binary"
    else:
        gender = None
    
    u = {
        "user_id": user.id,
        "person_id": user.person.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
        "gender": gender,
        "phone": user.person.phone,
        "birth_day": None if not user.person.birth_date else date.strftime(user.person.birth_date, "%B %d, %Y"),
        "address": a
    }

    return JsonResponse({"success": True, "user": u})


#############################################
################# Edit User #################
#############################################
@login_required
def editUser(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]

    if not user_id or not person_id:
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    try:
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    try:
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    if  user != request.user or person != user.person:
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    mobile = request.POST["mobile"]
    username = request.POST["username"]
    gender = request.POST["gender"]
    birth_day = request.POST["birth_day"]

    if not first_name or not last_name or not username:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    username = username.strip().lower()
    first_name = first_name.strip().lower().title()
    last_name = last_name.strip().lower().title()
    mobile = mobile.strip()
    
    if not util.validate_username(username):
        return JsonResponse({"success": False, "message": "Invalid Username"})

    try:
        t = datetime.strptime(birth_day, "%Y-%m-%d")
    except ValueError:
        t = None

    if username != user.username and User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username Already Exists"})
    
    if username != person.username and Person.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username Already Exists"})
    
    if mobile != person.phone and Person.objects.filter(phone=mobile).exists():
        return JsonResponse({"success": False, "message": "This mobile number is associated with another account."})

    person.first_name = first_name
    person.last_name = last_name
    person.username = username
    person.gender = gender if gender in ['F', 'M', 'N'] else None
    person.phone = mobile
    person.birth_date = t
    
    person.save()
    return JsonResponse({"success": True})


#############################################
################### Get User ################
#############################################
@login_required
def getUser(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False})
    
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]

    if not user_id or not person_id:
        return JsonResponse({"success": False})
    
    try:
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False})
    
    try:
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False})
    
    if  user != request.user or person != user.person:
        return JsonResponse({"success": False})
    
    g = user.person.gender
    if g == 'F':
        gender = "Female"
    elif g == 'M':
        gender = "Male"
    elif g == 'N':
        gender = "Non Binary"
    else:
        gender = "Select"
    
    u = {
        "user_id": user.id,
        "person_id": user.person.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
        "gender": g,
        "gender_l": gender,
        "phone": user.person.phone,
        "birth_day": user.person.birth_date
    }
    return JsonResponse({"success": True, "user": u})


#############################################
################ Add Address ################
#############################################
@login_required
def addAddress(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    email = request.POST["email"]
    mobile = request.POST["mobile"]
    city = request.POST["city"]
    state = request.POST["state"]
    pincode = request.POST["pincode"]
    country = request.POST["country"]
    landmark = request.POST["landmark"]
    address2 = request.POST["address2"]
    homephone = request.POST["homephone"]
    address1 = request.POST["address1"]
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]

    if not first_name or not last_name or not address1 or not email or not mobile or not city or not state or not pincode or not country or not landmark or not user_id or not person_id:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    try:
        user_id = int(user_id)
        person_id=int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Form"})
    
    try:
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})

    if user != request.user or person != user.person:
        return JsonResponse({"success": False, "message": "Invalid Request"})

    address = Address.objects.create(
        person=user.person,
        first_name=first_name.strip().lower().title(),
        last_name=last_name.strip().lower().title(),
        email=email,
        mobile=mobile,
        homephone=None if not homephone else homephone,
        address1=address1.strip().lower().title(),
        address2=None if not address2 else address2.strip().lower().title(),
        landmark=landmark.strip().lower().title(),
        pincode=pincode.strip(),
        city=city.strip().lower().title(),
        state=state.strip().lower().title(),
        country=country.strip().lower().title()
    )
    return JsonResponse({"success": True})


#############################################
################ Get Address ################
#############################################
@login_required
def getAddress(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False})
    
    address_id = request.POST["address_id"]
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]

    if not address_id or not user_id or not person_id:
        return JsonResponse({"success": False})
    
    try:
        address_id = int(address_id)
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False})
    
    try:
        addr = Address.objects.get(id=address_id)
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False})
    
    if user != request.user or person != user.person or addr.person != user.person:
        return JsonResponse({"success": False})
    
    a = {
        "id": addr.id,
        "primary": addr.primary,
        "first_name": addr.first_name,
        "last_name": addr.last_name,
        "email": addr.email,
        "mobile": addr.mobile,
        "homephone": addr.homephone,
        "address1": addr.address1,
        "address2": addr.address2,
        "landmark": addr.landmark,
        "pincode": addr.pincode,
        "city": addr.city,
        "state": addr.state,
        "country": addr.country,
        "user_id": user_id,
        "person_id": person_id
    }

    return JsonResponse({"success": True, "address": a})
            

#############################################
################ Edit Address ###############
#############################################
@login_required
def editAddress(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    address_id = request.POST["address_id"]
    person_id = request.POST["person_id"]
    user_id = request.POST["user_id"]

    if not address_id or not user_id or not person_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        address_id = int(address_id)
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        addr = Address.objects.get(id=address_id)
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user or person != user.person or addr.person != user.person:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    email = request.POST["email"]
    mobile = request.POST["mobile"]
    city = request.POST["city"]
    state = request.POST["state"]
    pincode = request.POST["pincode"]
    country = request.POST["country"]
    landmark = request.POST["landmark"]
    address2 = request.POST["address2"]
    homephone = request.POST["homephone"]
    address1 = request.POST["address1"]

    if not first_name or not last_name or not address1 or not email or not mobile or not city or not state or not pincode or not country or not landmark:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    addr.first_name = first_name.strip().lower().title()
    addr.last_name = last_name.strip().lower().title()
    addr.email = email
    addr.mobile = mobile
    addr.homephone = None if not homephone else homephone
    addr.address1 = address1.strip().lower().title()
    addr.address2 = None if not address2 else address2.strip().lower().title()
    addr.landmark = landmark.strip().lower().title()
    addr.pincode = pincode.strip()
    addr.city = city.strip().lower().title()
    addr.state = state.strip().lower().title()
    addr.country = country.strip().lower().title()
    addr.save()
    return JsonResponse({"success": True})


#############################################
############## Delete Address ###############
#############################################
@login_required
def deleteAddress(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    address_id = request.POST["address_id"]
    person_id = request.POST["person_id"]
    user_id = request.POST["user_id"]

    if not address_id or not user_id or not person_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        address_id = int(address_id)
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        addr = Address.objects.get(id=address_id)
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user or person != user.person or addr.person != user.person:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        addr.delete()
    except:
        return JsonResponse({"success": False, "message": "Protected Table"})
    else:
        return JsonResponse({"success": True})


#############################################
################ Make Primary ###############
#############################################
@login_required
def makeAddressPrimary(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    address_id = request.POST["address_id"]
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]
    if not address_id or not user_id or not person_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        address_id = int(address_id)
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        addr = Address.objects.get(id=address_id)
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user!= request.user or person != user.person or addr.person != user.person:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    addresses = person.address.all()
    for address in addresses:
        if address == addr:
            address.primary = True
        else:
            address.primary = False
        address.save()
    
    return JsonResponse({"success": True})


#############################################
################## Edit Email ###############
#############################################
@login_required
def editEmail(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    email = request.POST["email"]
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]
    password = request.POST["password"]
    new_email = request.POST["new_email"]

    if not email or not user_id or not person_id or not password or not new_email:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user or person != user.person or email != user.email or email == new_email:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not authenticate(request, username=user.username, password=password):
        return JsonResponse({"success": False, "message": "Incorrect Password"})
    
    if not util.validate_email(new_email):
        return JsonResponse({"success": False, "message": "Invalid Email Address"})
    
    if User.objects.filter(email=new_email).exists() or Person.objects.filter(email=new_email).exists():
        return JsonResponse({"success": False, "message": "This email address is associated with another account."})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {user.username} - Current Email: {email} - New Email: {new_email} - Code: {code}")
    else:
        try:
            send_mail(
                'Verification Code',
                f'Your verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [new_email],
                fail_silently=False,
            )
        except:
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["editEmail"] = {
        "user_id": user.id,
        "person_id": person.id,
        "new_email": new_email,
        "code": code,
        "old_email": user.email
    }
    request.session.modified = True
    return JsonResponse({"success": True})


def cancelEmailChange(request):
    if request.session.get("editEmail", False):
        request.session["editEmail"].clear()
        request.session.pop("editEmail")
    return JsonResponse({"success": True})


@login_required
def editEmailResendCode(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not request.session.get("editEmail", False) or request.session["editEmail"]["user_id"] != request.user.id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]
    new_email = request.POST["new_email"]

    if not user_id or not person_id or not new_email:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if request.session["editEmail"]["user_id"] != user_id or request.session["editEmail"]["person_id"] != person_id or request.session["editEmail"]["new_email"] != new_email:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        new_email = request.session["editEmail"]["new_email"]
        current_email = request.session["editEmail"]["old_email"]
        print(f"Username: {request.user.username} - Current Email: {current_email} - New Email: {new_email} - Code: {code}")
    else:
        try:
            send_mail(
                'Verification Code',
                f'Your verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [new_email],
                fail_silently=False,
            )
        except:
            request.session["editEmail"].clear()
            request.session.pop("editEmail", False)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    request.session["editEmail"]["code"] = code
    request.session.modified = True
    return JsonResponse({"success": True})
    
    
@login_required
def editEmailVerify(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not request.session.get("editEmail", False) or request.session["editEmail"]["user_id"] != request.user.id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user_id = request.POST["user_id"]
    person_id = request.POST["person_id"]
    new_email = request.POST["new_email"]
    code = request.POST["code"]

    if not user_id or not person_id or not new_email or not code:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if code != request.session["editEmail"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    try:
        user_id = int(user_id)
        person_id = int(person_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if request.session["editEmail"]["user_id"] != user_id or request.session["editEmail"]["person_id"] != person_id or request.session["editEmail"]["new_email"] != new_email:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user = User.objects.get(id=user_id)
        person = Person.objects.get(id=person_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user or person != user.person:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if User.objects.filter(email=new_email).exists() or Person.objects.filter(email=new_email).exists():
        request.session["editEmail"].clear()
        request.session.pop("editEmail", False)
        return JsonResponse({"success": False, "message": "This email address is associated with another account."})
    
    old_email = user.email
    person.email = new_email
    try:
        person.save()
    except:
        request.session["editEmail"].clear()
        request.session.pop("editEmail", False)
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})

    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                f'Your registered email address is changed from {old_email} to {new_email}',
                settings.EMAIL_HOST_USER,
                [new_email, old_email],
                fail_silently=False,
            )
        except:
            pass
    request.session["editEmail"].clear()
    request.session.pop("editEmail", False)
    return JsonResponse({"success": True})


@login_required
def updatepassword(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    user_id = request.POST["user_id"]
    current_password = request.POST["current_password"]
    new_password = request.POST["new_password"]
    new_password1 = request.POST["new_password1"]

    if not user_id or not current_password or not new_password or not new_password1:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if new_password != new_password1:
        return JsonResponse({"success": False, "message": "Passwords Don't Match"})
    
    if not settings.AUTHENTICATION_DEBUG and not util.validate_password(new_password1):
        return JsonResponse({"success": False, "message": "Invalid Password"})
    
    try:
        user_id = int(user_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Form"})
    
    try:
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not authenticate(request, username=user.username, password=current_password):
        return JsonResponse({"success": False, "message": "Incorrect Password"})
    
    user.set_password(new_password)
    user.save()
    logout(request)
    user = User.objects.get(id=user_id)
    login(request, user)
    
    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                f'Your password was just changed.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except:
            pass
    return JsonResponse({"success": True})


@login_required
def closeAccount(request):
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_staff or request.method == "GET":
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user_id = request.POST["user_id"]
    if not user_id:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user_id = int(user_id)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user.is_active = False
    user.save()
    logout(request)
    return JsonResponse({"success": True})