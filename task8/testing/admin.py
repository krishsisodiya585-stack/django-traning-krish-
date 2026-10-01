from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Answer, Attempt, Choice, Question, Quiz, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ("full_name", "email", "user", "joined_at")
	search_fields = ("full_name", "email", "user__username")
	readonly_fields = ("joined_at",)


class ChoiceInlineFormSet(BaseInlineFormSet):
	def clean(self):
		super().clean()
		if any(self.errors):
			return

		active_choices = [
			form.cleaned_data
			for form in self.forms
			if form.cleaned_data
			and not form.cleaned_data.get("DELETE", False)
			and (form.instance.pk or form.has_changed())
		]
		correct_count = sum(choice.get("is_correct", False) for choice in active_choices)
		if len(active_choices) < 2:
			raise ValidationError("Add at least two answer choices.")
		if correct_count != 1:
			raise ValidationError("Mark exactly one answer choice as correct.")


class ChoiceInline(admin.TabularInline):
	model = Choice
	formset = ChoiceInlineFormSet
	extra = 4


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
	list_display = ("title", "is_published", "question_total", "updated_at")
	list_filter = ("is_published",)
	search_fields = ("title", "description")
	readonly_fields = ("created_at", "updated_at")

	@admin.display(description="Questions")
	def question_total(self, quiz):
		return quiz.questions.count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("text", "quiz", "position", "points")
	list_filter = ("quiz",)
	search_fields = ("text", "quiz__title")
	inlines = (ChoiceInline,)


class AnswerInline(admin.TabularInline):
	model = Answer
	extra = 0
	can_delete = False
	readonly_fields = ("question", "selected_choice", "is_correct", "points_awarded")
	fields = readonly_fields

	def has_add_permission(self, request, obj=None):
		return False


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
	list_display = ("student", "quiz", "status", "earned_points", "total_points", "started_at", "submitted_at")
	list_filter = ("status", "quiz", "submitted_at")
	search_fields = ("student__username", "student__email", "quiz__title")
	readonly_fields = (
		"student",
		"quiz",
		"status",
		"started_at",
		"submitted_at",
		"question_count",
		"correct_answers",
		"total_points",
		"earned_points",
	)
	inlines = (AnswerInline,)

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
	list_display = ("attempt", "question", "selected_choice", "is_correct", "points_awarded")
	list_filter = ("is_correct",)
	search_fields = ("attempt__student__username", "question__text")
	readonly_fields = ("attempt", "question", "selected_choice", "is_correct", "points_awarded")

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False
