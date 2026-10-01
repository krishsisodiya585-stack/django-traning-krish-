from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import LoginForm, SignUpForm, StudentRegistrationForm
from .models import Student, user


def get_session_account(request):
   username = request.session.get('username')
   if not username:
      return None
   return user.objects.filter(username=username).first()


def home(request):
   account = get_session_account(request)
   registrations = Student.objects.filter(registered_by=account) if account else []
   return render(request, 'myuser/home.html', {
      'account': account,
      'registrations': registrations,
   })

def sign_up(request):
   if request.method == 'POST':
      form = SignUpForm(request.POST)
      if form.is_valid():
         form.save()
         messages.success(request, 'Account created. Sign in to continue.')
         return redirect('login')
   else:
      form = SignUpForm()

   return render(request, 'myuser/sign_up.html', {'form': form})


def save_user(request):
   return redirect('sign_up')


def login(request):
   account = get_session_account(request)
   if account:
      return redirect('student_register')

   if request.method == 'POST':
      form = LoginForm(request.POST)
      if form.is_valid():
         account = user.objects.filter(
            username=form.cleaned_data['username'],
         ).first()
         if account and account.check_password(form.cleaned_data['password']):
            request.session['username'] = account.username
            request.session['name'] = account.name
            messages.success(request, 'You are now signed in.')
            return redirect('student_register')
         form.add_error(None, 'Username or password is incorrect.')
   else:
      form = LoginForm()

   return render(request, 'myuser/login.html', {'form': form})


def login_vel(request):
   return redirect('login')


def student_register(request):
   account = get_session_account(request)
   if not account:
      messages.info(request, 'Sign in to open student registration.')
      return redirect('login')

   if request.method == 'POST':
      form = StudentRegistrationForm(request.POST)
      if form.is_valid():
         registration = form.save(commit=False)
         registration.registered_by = account
         registration.save()
         messages.success(request, 'Student registration saved.')
         return redirect('home')
   else:
      form = StudentRegistrationForm()

   return render(request, 'myuser/student_register.html', {
      'account': account,
      'form': form,
   })


def logout(request):
   request.session.flush()
   messages.success(request, 'You have signed out.')
   return redirect('home')
