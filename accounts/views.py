import os
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, UserProfile
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from .forms import UserForm
from django.shortcuts import render, redirect
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .decorators import auth_user_should_not_access
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
import threading

    
    
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('accounts/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_HOST_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        EmailThread(email).start()


@auth_user_should_not_access
def signup(request):
    if request.method == "POST":
        context = {'has_error': False, 'data': request.POST}
        email = request.POST.get('email')
        username = request.POST.get('username')
        user_type = request.POST.get('user_type', None)
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'Password should be at least 6 characters')
            context['has_error'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'Password mismatch')
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Enter a valid email address')
            context['has_error'] = True

        if not username:
            messages.add_message(request, messages.ERROR,
                                 'Username is required')
            context['has_error'] = True
       
        if not user_type:
            messages.add_message(request, messages.ERROR,
                                 'Please select a user type')
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR,
                                 'Username is taken, choose another one')
            context['has_error'] = True

            return render(request, 'accounts/signup.html', context, status=409)

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR,
                                 'Email is taken, choose another one')
            context['has_error'] = True

            return render(request, 'accounts/signup.html', context, status=409)

        if context['has_error']:
            return render(request, 'accounts/signup.html', context)

        user = User.objects.create_user(username=username, email=email, user_type=user_type)
        user.set_password(password)
        user.save()

        if not context['has_error']:

            send_activation_email(user, request)

            messages.add_message(request, messages.SUCCESS,
                                 'We sent you an email to verify your account')
            return redirect('login_user')

    return render(request, 'accounts/signup.html')


@auth_user_should_not_access
def login_user(request):

    if request.method == 'POST':
        context = {'data': request.POST}
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and not user.is_email_verified:
            messages.add_message(request, messages.ERROR,
                                 'Email is not verified, please check your email inbox')
            return render(request, 'accounts/login.html', context, status=401)

        if not user:
            messages.add_message(request, messages.ERROR,
                                 'Invalid credentials, try again')
            return render(request, 'accounts/login.html', context, status=401)

        login(request, user)

        # messages.add_message(request, messages.SUCCESS,
        #                      f'Welcome {user.username}')

        return redirect(reverse('home'))

    return render(request, 'accounts/login.html')

@login_required
def profile(request,user_id):
    user = User.objects.get(id=user_id)
    profile = UserProfile.objects.get(id=user_id)
    if request.method == "POST":

        avatar = request.FILES.get("avatar", None)

        if avatar is not None:
            profile.avatar = avatar
        profile.full_name = request.POST.get('full_name')
        profile.bio = request.POST.get('bio')
        profile.save()
        messages.success(request, "profile updated Successfully")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    if (request.user.is_authenticated and request.user.id == user_id):
        return render(request, 'accounts/profile.html', {'profile':profile})

        

def logout_user(request):

    logout(request)

    messages.add_message(request, messages.SUCCESS,
                         'Successfully logged out')

    return redirect(reverse('login_user'))


def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('login_user'))

    return render(request, 'accounts/activate-failed.html', {"user": user})

def about(request):
   
    return render(request, 'accounts/about.html')


# @login_required(login_url="/accounts/signup")
# def profile(request):
 
#     user = User.objects.get(username=request.user.username)
#     profile = UserProfile.objects.get(user=user)
#     form = UserForm(instance=user)
#     print(profile.avatar.url)
#     if request.method == 'POST':
#         form = UserForm(request.POST, request.FILES,instance=user)
#         print(profile)
#         if form.is_valid():
#             form.save()

#     return render(request,'accounts/profile.html', {'form':form, 'profile': profile})

