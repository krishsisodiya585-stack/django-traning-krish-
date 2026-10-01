from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
import logging

from .forms import BookIssueForm
from .models import BookIssue
from .mysql_sync import mirror_issue_to_mysql


logger = logging.getLogger(__name__)


def home(request):
	return render(request, 'librarymanagementsystem/home.html')


def signup_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	if request.method == 'POST':
		name = request.POST.get('name', '').strip()
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '')
		confirm_password = request.POST.get('confirm_password', '')
		if not name or not username or not password:
			messages.error(request, 'Please complete every field.')
		elif password != confirm_password:
			messages.error(request, 'Passwords do not match.')
		elif User.objects.filter(username=username).exists():
			messages.error(request, 'That username is already in use.')
		else:
			user = User.objects.create_user(username=username, password=password, first_name=name)
			login(request, user)
			return redirect('dashboard')
	return render(request, 'librarymanagementsystem/signup.html')


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		messages.error(request, 'Username or password is incorrect.')
	return render(request, 'librarymanagementsystem/login.html')


@login_required
def dashboard(request):
	issues = BookIssue.objects.filter(issued_by=request.user)
	return render(request, 'librarymanagementsystem/dashboard.html', {
		'issue_count': issues.count(),
		'student_count': issues.values('student_name').distinct().count(),
		'recent_issues': issues[:5],
	})


@login_required
def issue_book(request):
	form = BookIssueForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		issue = form.save(commit=False)
		issue.issued_by = request.user
		issue.save()
		try:
			mirror_issue_to_mysql(issue)
		except Exception:
			logger.exception('Could not mirror book issue %s to MySQL.', issue.pk)
			messages.warning(request, 'Book issue saved, but MySQL sync failed. Check the database connection.')
		else:
			messages.success(request, 'Book issue saved to the flaskproject SQL database.')
		return redirect('issue_success', issue_id=issue.pk)
	return render(request, 'librarymanagementsystem/issue_book.html', {'form': form})


@login_required
def issue_success(request, issue_id):
	issue = get_object_or_404(BookIssue, pk=issue_id, issued_by=request.user)
	return render(request, 'librarymanagementsystem/success.html', {'issue': issue})


@login_required
def book_list(request):
	issues = BookIssue.objects.filter(issued_by=request.user)
	return render(request, 'librarymanagementsystem/book_list.html', {'issues': issues})


@login_required
def logout_view(request):
	if request.method == 'POST':
		logout(request)
	return redirect('home')
