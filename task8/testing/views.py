from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import SignUpForm
from .models import Answer, Attempt, Quiz, StudentProfile


def home(request):
	if request.user.is_authenticated:
		return redirect("dashboard")
	return render(request, "testing/home.html", {"form": AuthenticationForm(request)})


def signup(request):
	if request.user.is_authenticated:
		return redirect("dashboard")
	form = SignUpForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		with transaction.atomic():
			user = form.save()
			StudentProfile.objects.create(
				user=user,
				full_name=form.cleaned_data["full_name"].strip(),
				email=form.cleaned_data["email"],
			)
		auth_login(request, user)
		return redirect("dashboard")
	return render(request, "testing/signup.html", {"form": form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect("dashboard")
	form = AuthenticationForm(request, data=request.POST or None)
	if request.method == "POST" and form.is_valid():
		auth_login(request, form.get_user())
		return redirect("dashboard")
	return render(request, "testing/login.html", {"form": form})


@require_POST
def logout_view(request):
	auth_logout(request)
	return redirect("home")


@login_required
def dashboard(request):
	quizzes = Quiz.objects.filter(is_published=True).annotate(question_total=Count("questions"))
	attempts = Attempt.objects.filter(student=request.user, status=Attempt.Status.COMPLETED)
	latest_by_quiz = {}
	for attempt in attempts.select_related("quiz"):
		latest_by_quiz.setdefault(attempt.quiz_id, attempt)
	for quiz in quizzes:
		quiz.latest_attempt = latest_by_quiz.get(quiz.pk)
	return render(
		request,
		"testing/dashboard.html",
		{"quizzes": quizzes, "latest_by_quiz": latest_by_quiz, "completed_total": attempts.count()},
	)


@login_required
def take_quiz(request, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
	questions = list(quiz.questions.prefetch_related("choices"))
	if not questions or any(len(question.choices.all()) < 2 for question in questions):
		messages.error(request, "This test is not ready yet. Please try again later.")
		return redirect("dashboard")

	if request.method == "POST":
		try:
			with transaction.atomic():
				attempt = Attempt.objects.select_for_update().filter(
					student=request.user,
					quiz=quiz,
					status=Attempt.Status.IN_PROGRESS,
				).first()
				if attempt is None:
					attempt = Attempt.objects.create(student=request.user, quiz=quiz)
				if attempt.status == Attempt.Status.COMPLETED:
					return redirect("result", attempt_id=attempt.pk)

				correct_count = 0
				earned_points = 0
				total_points = sum(question.points for question in questions)
				for question in questions:
					choice_id = request.POST.get(f"question_{question.pk}")
					selected_choice = question.choices.filter(pk=choice_id).first() if choice_id else None
					is_correct = bool(selected_choice and selected_choice.is_correct)
					points_awarded = question.points if is_correct else 0
					correct_choice = question.choices.filter(is_correct=True).first()
					Answer.objects.create(
						attempt=attempt,
						question=question,
						selected_choice=selected_choice,
						is_correct=is_correct,
						points_awarded=points_awarded,
						points_possible=question.points,
						correct_answer_text=correct_choice.text if correct_choice else "",
					)
					correct_count += int(is_correct)
					earned_points += points_awarded

				attempt.status = Attempt.Status.COMPLETED
				attempt.submitted_at = timezone.now()
				attempt.question_count = len(questions)
				attempt.correct_answers = correct_count
				attempt.total_points = total_points
				attempt.earned_points = earned_points
				attempt.save(
					update_fields=(
						"status",
						"submitted_at",
						"question_count",
						"correct_answers",
						"total_points",
						"earned_points",
					)
				)
		except IntegrityError:
			messages.error(request, "Your test could not be submitted. Please reopen it and try again.")
			return redirect("dashboard")
		return redirect("result", attempt_id=attempt.pk)

	try:
		attempt, _ = Attempt.objects.get_or_create(
			student=request.user,
			quiz=quiz,
			status=Attempt.Status.IN_PROGRESS,
		)
	except IntegrityError:
		attempt = Attempt.objects.get(
			student=request.user,
			quiz=quiz,
			status=Attempt.Status.IN_PROGRESS,
		)
	return render(request, "testing/take_quiz.html", {"quiz": quiz, "questions": questions, "attempt": attempt})


@login_required
def result(request, attempt_id):
	attempt = get_object_or_404(
		Attempt.objects.select_related("quiz", "student").prefetch_related(
			"answers__question", "answers__selected_choice"
		),
		pk=attempt_id,
		status=Attempt.Status.COMPLETED,
	)
	if attempt.student_id != request.user.pk and not request.user.is_staff:
		return HttpResponseForbidden("You do not have access to this result.")
	return render(
		request,
		"testing/result.html",
		{
			"attempt": attempt,
			"answers": attempt.answers.order_by("question__position"),
			"incorrect_count": attempt.question_count - attempt.correct_answers,
		},
	)


@login_required
def history(request):
	attempts = Attempt.objects.filter(
		student=request.user,
		status=Attempt.Status.COMPLETED,
	).select_related("quiz")
	return render(request, "testing/history.html", {"attempts": attempts})
