from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class StudentProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	full_name = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ("full_name",)

	def __str__(self):
		return self.full_name


class Quiz(models.Model):
	title = models.CharField(max_length=160, unique=True)
	description = models.TextField(blank=True)
	is_published = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ("title",)

	def __str__(self):
		return self.title


class Question(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
	text = models.TextField()
	explanation = models.TextField(blank=True)
	points = models.PositiveSmallIntegerField(default=1)
	position = models.PositiveSmallIntegerField(default=1)

	class Meta:
		ordering = ("position", "id")
		constraints = [
			models.UniqueConstraint(fields=("quiz", "position"), name="unique_question_position_per_quiz"),
		]

	def __str__(self):
		return f"{self.quiz}: Question {self.position}"


class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
	text = models.CharField(max_length=500)
	is_correct = models.BooleanField(default=False)
	position = models.PositiveSmallIntegerField(default=1)

	class Meta:
		ordering = ("position", "id")
		constraints = [
			models.UniqueConstraint(fields=("question", "position"), name="unique_choice_position_per_question"),
		]

	def __str__(self):
		return self.text


class Attempt(models.Model):
	class Status(models.TextChoices):
		IN_PROGRESS = "in_progress", "In progress"
		COMPLETED = "completed", "Completed"

	student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
	quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT, related_name="attempts")
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
	started_at = models.DateTimeField(auto_now_add=True)
	submitted_at = models.DateTimeField(null=True, blank=True)
	question_count = models.PositiveSmallIntegerField(default=0)
	correct_answers = models.PositiveSmallIntegerField(default=0)
	total_points = models.PositiveSmallIntegerField(default=0)
	earned_points = models.PositiveSmallIntegerField(default=0)

	class Meta:
		ordering = ("-started_at",)
		constraints = [
			models.UniqueConstraint(
				fields=("student", "quiz"),
				condition=Q(status="in_progress"),
				name="one_open_attempt_per_student_quiz",
			),
			models.CheckConstraint(
				condition=Q(earned_points__lte=F("total_points")),
				name="attempt_earned_points_within_total",
			),
			models.CheckConstraint(
				condition=Q(correct_answers__lte=F("question_count")),
				name="attempt_correct_within_question_count",
			),
		]

	def __str__(self):
		return f"{self.student} - {self.quiz} ({self.get_status_display()})"


class Answer(models.Model):
	attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
	question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
	selected_choice = models.ForeignKey(
		Choice,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="answers",
	)
	is_correct = models.BooleanField(default=False)
	points_awarded = models.PositiveSmallIntegerField(default=0)
	points_possible = models.PositiveSmallIntegerField(default=0)
	correct_answer_text = models.CharField(max_length=500, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=("attempt", "question"), name="one_answer_per_question_attempt"),
		]

	def clean(self):
		if self.attempt_id and self.question_id and self.attempt.quiz_id != self.question.quiz_id:
			raise ValidationError("The question must belong to the attempted quiz.")
		if self.selected_choice_id and self.selected_choice.question_id != self.question_id:
			raise ValidationError({"selected_choice": "Choose an option for this question."})

	def __str__(self):
		return f"{self.attempt}: {self.question}"
