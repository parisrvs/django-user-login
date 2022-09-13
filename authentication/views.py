from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from datetime import datetime, timedelta
import random
from time import sleep
from . import util


def clear_authentication_session(request):
    if request.session.get("register", False):
        request.session["register"].clear()
        request.session.pop("register", False)
        request.session.modified = True
    if request.session.get("recover", False):
        request.session["recover"].clear()
        request.session.pop("recover", False)
        request.session.modified = True
    if request.session.get("changeEmail", False):
        request.session["changeEmail"].clear()
        request.session.pop("changeEmail", False)
        request.session.modified = True
    if request.session.get("close_account", False):
        request.session["close_account"].clear()
        request.session.pop("close_account", False)
        request.session.modified = True
    return


######## Login##########
@ensure_csrf_cookie
def login_view(request):
    clear_authentication_session(request)
    if request.method == "GET":
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return HttpResponseRedirect(reverse('admin:index'))
            return redirect('/')
        
        q = dict(request.GET)
        if "next" in q:
            request.session["next"] = q["next"][0]

        return render(
            request,
            "authentication/login.html",
            {"sitetitle": settings.SITE_TITLE}
        )
    elif request.method == "POST":
        if request.user.is_authenticated:
            return JsonResponse({"success": False, "message": "Invalid Request"})
        
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


######## Logout #########
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('authentication:login'))


###### Register ######
def register(request):
    if request.user.is_authenticated or request.method == "GET":
        clear_authentication_session(request)
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
    
    if len(first_name) > 150 or len(last_name) > 150:
        return JsonResponse({"success": False, "message": "First / Last name too long."})
    if not util.validate_password(password):
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
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["register"] = {
        "username": username,
        "email": email,
        "password": password,
        "verified": False,
        "code": code,
        "first_name": first_name,
        "last_name": last_name,
        "validity": str(validity),
        "code_generated_at": str(code_generated_at)
    }
    request.session.modified = True
    return JsonResponse({"success": True, "email": email, "validity": validity})


##### Cancel Registration ######
def cancelregistration(request):
    clear_authentication_session(request)
    return JsonResponse({"success": True})


######## Resend Verification Code ########
def verifyRegistrationCodeResend(request):
    if request.user.is_authenticated or not request.session.get("register", False):
        clear_authentication_session(request)
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
            clear_authentication_session(request)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["register"]["code"] = code
    request.session["register"]["validity"] = str(validity)
    request.session["register"]["code_generated_at"] = str(code_generated_at)
    request.session.modified = True
    return JsonResponse({"success": True, "validity": validity})


##### Process registration #####
def verifyregistration(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("register", False):
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    if not code:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    if code != request.session["register"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    if not util.is_valid(request.session["register"]["code_generated_at"], settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES):
        return JsonResponse({"success": False, "message": "This verification code isn't valid anymore. Please request a new code."})

    if User.objects.filter(username=request.session["register"]["username"]).exists():
        clear_authentication_session(request)
        return JsonResponse({
            "success": False,
            "message": "This username already exists. Please try again with a different username.",
            "restart": True
        })
    
    if User.objects.filter(email=request.session["register"]["email"]).exists():
        clear_authentication_session(request)
        return JsonResponse({
            "success": False,
            "message": "This email is associated with another account. Please try again with a different email address.",
            "restart": True
        })
    
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                request.session["register"]["username"],
                request.session["register"]["email"],
                request.session["register"]["password"]
            )
            user.first_name = request.session["register"]["first_name"]
            user.last_name = request.session["register"]["last_name"]
            user.save()
    except:
        clear_authentication_session(request)
        return JsonResponse({
            "success": False,
            "message": "Something went wrong. Please try again.",
            "restart": True
        })
    
    clear_authentication_session(request)
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
    else:
        print("You have successfully registered your account.")
    return JsonResponse({"success": True})


###### recover ######
def recover(request):
    if request.user.is_authenticated or request.method == "GET":
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    response = request.POST["email"]
    if not response:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    response = response.strip()
    user = User.objects.filter(Q(username=response) | Q(email=response)).first()
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
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["recover"] = {
        "user_id": user.id,
        "email": email,
        "username": user.username,
        "verified": False,
        "code": code,
        "validity": str(validity),
        "code_generated_at": str(code_generated_at)

    }
    request.session.modified = True

    if response == user.username:
        response = util.encryptemail(email)
    return JsonResponse({"success": True, "email": response, "validity": validity})


##### Cancel Recovery ######
def cancelrecovery(request):
    clear_authentication_session(request)
    return JsonResponse({"success": True})


##### resend verification code ######
def verifyRecoverCodeResend(request):
    if request.user.is_authenticated or not request.session.get("recover", False):
        clear_authentication_session(request)
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
            clear_authentication_session(request)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["recover"]["code"] = code
    request.session["recover"]["code_generated_at"] = str(code_generated_at)
    request.session["recover"]["validity"] = str(validity)
    request.session.modified = True
    return JsonResponse({"success": True, "validity": validity})


# initiate password change #
def verifyrecovery(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("recover", False) or request.session["recover"]["verified"]:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    if not code:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if code != request.session["recover"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    if not util.is_valid(request.session["recover"]["code_generated_at"], settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES):
        return JsonResponse({"success": False, "message": "This verification code isn't valid anymore. Please request a new code."})
    
    request.session["recover"]["verified"] = True
    request.session.modified = True
    return JsonResponse({"success": True})
    

######## change password #########
def verifyChangePassword(request):
    if request.user.is_authenticated or request.method == "GET" or not request.session.get("recover", False) or not request.session["recover"]["verified"]:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    password1 = request.POST["password1"]
    password2 = request.POST["password2"]

    if not password1 or not password2:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    if password1 != password2:
        return JsonResponse({"success": False, "message": "Passwords Don't Match"})
    if not util.validate_password(password1):
        return JsonResponse({"success": False, "message": "Invalid Password"})
    
    try:
        user = User.objects.get(id=request.session["recover"]["user_id"])
    except:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user.set_password(password1)
    try:
        user.save()
    except:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})

    clear_authentication_session(request)
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
    else:
        print("Your password was just changed.")
    return JsonResponse({"success": True})


###### Account ######
@login_required
@ensure_csrf_cookie
def account(request):
    if request.user.is_active == False:
        logout(request)
        return HttpResponseRedirect(reverse('authentication:login'))
    elif request.user.is_superuser or request.user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    else:
        clear_authentication_session(request)
        return render(
            request,
            "authentication/account.html",
            {"sitetitle": settings.SITE_TITLE}
        )


###### get user #####
@login_required
def getUser(request):
    user = User.objects.filter(username=request.user.username, is_active=True).first()
    if not user or user.is_superuser or user.is_staff:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    return JsonResponse({
        "success": True,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "last_login": user.last_login,
            "date_joined": user.date_joined
        }
    })


##### Edit Details ######
@login_required
def editDetails(request):
    if request.method == "GET" or request.user.is_superuser or request.user.is_staff:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    username = request.POST["username"]
    user_id = request.POST["user_id"]
    if not first_name or not last_name or not username or not user_id:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    username = username.strip().lower()
    first_name = first_name.strip().lower().title()
    last_name = last_name.strip().lower().title()
    if not util.validate_username(username):
        return JsonResponse({"success": False, "message": "Invalid Username"})
    
    if len(first_name) > 150 or len(last_name) > 150:
        return JsonResponse({"success": False, "message": "First / Last name too long."})
    
    try:
        user_id = int(user_id)
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if username != user.username and User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already exists. Please try a different username."})
    
    user.first_name = first_name
    user.last_name = last_name
    user.username = username

    try:
        user.save()
    except:
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again."})
    else:
        return JsonResponse({"success": True})


# Initiate Edit Email #
@login_required
def editEmail(request):
    if request.method == "GET" or request.user.is_superuser or request.user.is_staff:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    password = request.POST["password"]
    user_id = request.POST["user_id"]
    new_email = request.POST["new_email"]
    if not new_email or not password or not user_id:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    try:
        user_id = int(user_id)
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    if user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})

    if new_email == user.email:
        return JsonResponse({"success": False, "message": "No Change Detected"})
    
    if not util.validate_email(new_email):
        return JsonResponse({"success": False, "message": "Invalid Email Address"})
    
    if not authenticate(request, username=user.username, password=password):
        return JsonResponse({"success": False, "message": "Incorrect Password"})
    
    if User.objects.filter(email=new_email).exists():
        return JsonResponse({"success": False, "message": "This email is associated with another account."})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {user.username} - Email: {new_email} - Code: {code}")
    else:
        try:
            send_mail(
                'Update Email Verification Code',
                f'Your verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [new_email],
                fail_silently=False,
            )
        except:
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["changeEmail"] = {
        "username": user.username,
        "id": user.id,
        "current_email": user.email,
        "new_email": new_email,
        "code": code,
        "validity": str(validity),
        "code_generated_at": str(code_generated_at)
    }
    request.session.modified = True
    context = {
        "username": user.username,
        "current_email": user.email,
        "new_email": new_email,
    }
    
    return JsonResponse({"success": True, "context": context, "validity": validity})


###### edit email ######
@login_required
def edit_email(request):
    if request.method == "GET" or not request.session.get("changeEmail", False) or request.user.is_superuser or request.user.is_staff:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    username = request.POST["username"]
    current_email = request.POST["current_email"]
    new_email = request.POST["new_email"]
    if not code or not username or not current_email or not new_email:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if request.session["changeEmail"]["username"] != username or request.session["changeEmail"]["current_email"] != current_email \
        or request.session["changeEmail"]["new_email"] != new_email:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    try:
        user = User.objects.get(username=username)
    except:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if code != request.session["changeEmail"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    if not util.is_valid(request.session["changeEmail"]["code_generated_at"], settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES):
        return JsonResponse({"success": False, "message": "This verification code isn't valid anymore. Please request a new code."})
    
    if User.objects.filter(email=new_email).exists():
        clear_authentication_session(request)
        return JsonResponse({
            "success": False,
            "message": "This email is associated with another account. Please try again with a different email address."
        })
    
    user.email = new_email
    try:
        user.save()
    except:
        clear_authentication_session(request)
        return JsonResponse({
            "success": False,
            "message": "Something went wrong. Please try again."
        })

    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                f'Your email address is change from {current_email} to {new_email}.',
                settings.EMAIL_HOST_USER,
                [new_email, current_email],
                fail_silently=False,
            )
        except:
            pass
    else:
        print(f'Your email address is change from {current_email} to {new_email}.')
    clear_authentication_session(request)
    return JsonResponse({"success": True})


#### Cancel email update ####
@login_required
def editEmailCancel(request):
    clear_authentication_session(request)
    return JsonResponse({"success": True})


### resend verification code email update ###
@login_required
def resentEditEmailVerificationCode(request):
    if request.method == "GET" or not request.session.get("changeEmail", False) or request.user.is_superuser or request.user.is_staff:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    new_email = request.POST["new_email"]
    if not new_email or new_email != request.session["changeEmail"]["new_email"]:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {request.user.username} - Email: {new_email} - Code: {code}")
    else:
        try:
            send_mail(
                'Update Email Verification Code',
                f'Your new verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [new_email],
                fail_silently=False,
            )
        except:
            clear_authentication_session(request)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["changeEmail"]["code"] = code
    request.session["changeEmail"]["validity"] = str(validity)
    request.session["changeEmail"]["code_generated_at"] = str(code_generated_at)
    request.session.modified = True
    return JsonResponse({"success": True, "validity": validity})


### change user password ###
@login_required
def changepassword(request):
    if request.method == "GET" or request.user.is_superuser or request.user.is_staff:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user_id = request.POST["user_id"]
    current_password = request.POST["current_password"]
    new_password_1 = request.POST["new_password_1"]
    new_password_2 = request.POST["new_password_2"]
    
    if not user_id or not current_password or not new_password_1 or not new_password_2:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    if new_password_1 != new_password_2:
        return JsonResponse({"success": False, "message": "New passwords don't match."})
    if not util.validate_password(new_password_2):
        return JsonResponse({"success": False, "message": "Invalid Password"})

    try:
        user_id = int(user_id)
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})

    if user != request.user:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if not authenticate(request, username=user.username, password=current_password):
        return JsonResponse({"success": False, "message": "Incorrect Password"})
    
    try:
        user.set_password(new_password_2)
        user.save()
        update_session_auth_hash(request, user)
    except:
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                'Your password was just changed.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except:
            pass
    else:
        print('Your password was just changed.')
    return JsonResponse({"success": True})


## InitiateAccountClose ##
@login_required
def closeAccount(request):
    if request.method == "GET" or request.user.is_superuser or request.user.is_staff:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    user_id = request.POST["user_id"]
    password = request.POST["password"]
    if not user_id or not password:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    
    try:
        user_id = int(user_id)
        user = User.objects.get(id=user_id)
    except:
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user and user == request.user and authenticate(request, username=user.username, password=password):
        code = str(random.randint(100000, 999999))
        if settings.AUTHENTICATION_DEBUG:
            print(f"Username: {user.username} - Email: {user.email} - Code: {code}")
        else:
            try:
                send_mail(
                    'Security check for Account Closure',
                    f'Your verification code is {code}.',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
            except:
                return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
        
        code_generated_at = datetime.now()
        validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
        request.session["close_account"] = {
            "id": user.id,
            "code": code,
            "validity": str(validity),
            "code_generated_at": str(code_generated_at)
        }
        request.session.modified = True
        return JsonResponse({"success": True, "validity": validity, "id": user.id})
    return JsonResponse({"success": False, "message": "Invalid Credentials"})


#### close user account ####
@login_required
def accountClosure(request):
    if request.session == "GET" or request.user.is_superuser or request.user.is_staff or not request.session.get("close_account", False):
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = request.POST["code"]
    user_id = request.POST["user_id"]
    if not code or not user_id:
        return JsonResponse({"success": False, "message": "Incomplete Form"})
    try:
        user_id = int(user_id)
        user = User.objects.get(id=user_id)
    except:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if user != request.user or user.id != request.session["close_account"]["id"]:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    if code != request.session["close_account"]["code"]:
        return JsonResponse({"success": False, "message": "Incorrect Code"})
    
    if not util.is_valid(request.session["close_account"]["code_generated_at"], settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES):
        return JsonResponse({"success": False, "message": "This verification code isn't valid anymore. Please request a new one."})
    
    user.is_active = False
    user.set_unusable_password()
    try:
        user.save()
    except:
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    if not settings.AUTHENTICATION_DEBUG:
        try:
            send_mail(
                'Security Information',
                'Your account is now closed.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except:
            pass
    else:
        print('Your account is now closed.')
    messages.add_message(request, messages.INFO, "Your account is now closed.")
    logout(request)
    return JsonResponse({"success": True})


##### cancel account closure #####
@login_required
def cancelAccountClosure(request):
    clear_authentication_session(request)
    return JsonResponse({"success": True})


### resend verification code account closure ###
@login_required
def resendCloseAccountVerificationCode(request):
    if request.user.is_superuser or request.user.is_staff or not request.session.get("close_account", False):
        clear_authentication_session(request)
        return JsonResponse({"success": False, "message": "Invalid Request"})
    
    code = str(random.randint(100000, 999999))
    if settings.AUTHENTICATION_DEBUG:
        print(f"Username: {request.user.username} - Email: {request.user.email} - Code: {code}")
    else:
        try:
            send_mail(
                'Security check for Account Closure',
                f'Your new verification code is {code}.',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
        except:
            clear_authentication_session(request)
            return JsonResponse({"success": False, "message": "Something went wrong. Please try again later."})
    
    code_generated_at = datetime.now()
    validity = code_generated_at + timedelta(minutes=settings.VERIFICATION_CODE_VALIDITY_IN_MINUTES)
    request.session["close_account"]["code_generated_at"] = str(code_generated_at)
    request.session["close_account"]["validity"] = str(validity)
    request.session["close_account"]["code"] = code
    request.session.modified = True
    return JsonResponse({"success": True, "validity": validity})