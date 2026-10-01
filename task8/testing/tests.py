from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Answer, Attempt, Choice, Question, Quiz, StudentProfile


User = get_user_model()


class StudentFlowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="sam", password="Harbor-Lamp-93!")
		self.quiz = Quiz.objects.create(title="Science basics", description="A short practice test.", is_published=True)
		self.first_question = Question.objects.create(quiz=self.quiz, text="Which planet is known as the Red Planet?", points=2, position=1)
		self.second_question = Question.objects.create(quiz=self.quiz, text="What gas do plants absorb?", points=3, position=2)
		self.mars = Choice.objects.create(question=self.first_question, text="Mars", is_correct=True, position=1)
		self.venus = Choice.objects.create(question=self.first_question, text="Venus", position=2)
		self.carbon_dioxide = Choice.objects.create(question=self.second_question, text="Carbon dioxide", is_correct=True, position=1)
		self.oxygen = Choice.objects.create(question=self.second_question, text="Oxygen", position=2)

	def test_dashboard_requires_login(self):
		response = self.client.get(reverse("dashboard"))
		self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

	def test_signup_creates_hashed_user_and_unique_profile(self):
		response = self.client.post(
			reverse("signup"),
			{
				"full_name": "Riya Patel",
				"username": "riya",
				"email": "riya@example.com",
				"password1": "Harbor-Lamp-93!",
				"password2": "Harbor-Lamp-93!",
				"terms": "on",
			},
		)
		self.assertRedirects(response, reverse("dashboard"))
		user = User.objects.get(username="riya")
		self.assertTrue(user.check_password("Harbor-Lamp-93!"))
		self.assertEqual(StudentProfile.objects.get(user=user).email, "riya@example.com")

	def test_submission_scores_server_side_and_saves_history(self):
		self.client.force_login(self.user)
		start_url = reverse("take_quiz", args=(self.quiz.pk,))
		self.client.get(start_url)
		response = self.client.post(
			start_url,
			{
				f"question_{self.first_question.pk}": self.mars.pk,
				f"question_{self.second_question.pk}": self.carbon_dioxide.pk,
			},
		)
		attempt = Attempt.objects.get(student=self.user, quiz=self.quiz)
		self.assertRedirects(response, reverse("result", args=(attempt.pk,)))
		self.assertEqual((attempt.correct_answers, attempt.earned_points, attempt.total_points), (2, 5, 5))
		self.assertEqual(attempt.answers.count(), 2)
		self.assertEqual(attempt.answers.get(question=self.first_question).correct_answer_text, "Mars")
		self.assertContains(self.client.get(reverse("history")), "Science basics")

	def test_choice_from_another_question_is_not_accepted(self):
		self.client.force_login(self.user)
		start_url = reverse("take_quiz", args=(self.quiz.pk,))
		self.client.get(start_url)
		self.client.post(
			start_url,
			{
				f"question_{self.first_question.pk}": self.carbon_dioxide.pk,
				f"question_{self.second_question.pk}": self.carbon_dioxide.pk,
			},
		)
		attempt = Attempt.objects.get(student=self.user, quiz=self.quiz)
		first_answer = attempt.answers.get(question=self.first_question)
		self.assertIsNone(first_answer.selected_choice)
		self.assertFalse(first_answer.is_correct)
		self.assertEqual(attempt.earned_points, 3)

	def test_result_review_uses_submission_time_snapshot(self):
		self.client.force_login(self.user)
		start_url = reverse("take_quiz", args=(self.quiz.pk,))
		self.client.get(start_url)
		self.client.post(
			start_url,
			{
				f"question_{self.first_question.pk}": self.venus.pk,
				f"question_{self.second_question.pk}": self.carbon_dioxide.pk,
			},
		)
		attempt = Attempt.objects.get(student=self.user, quiz=self.quiz)
		self.first_question.points = 9
		self.first_question.save(update_fields=("points",))
		self.mars.text = "Jupiter"
		self.mars.is_correct = False
		self.mars.save(update_fields=("text", "is_correct"))
		response = self.client.get(reverse("result", args=(attempt.pk,)))
		self.assertContains(response, "Mars")
		self.assertContains(response, "0 / 2 pts")

	def test_students_cannot_view_another_students_result(self):
		other_user = User.objects.create_user(username="alex", password="Harbor-Lamp-93!")
		attempt = Attempt.objects.create(
			student=other_user,
			quiz=self.quiz,
			status=Attempt.Status.COMPLETED,
			submitted_at=timezone.now(),
			question_count=2,
			correct_answers=1,
			total_points=5,
			earned_points=2,
		)
		self.client.force_login(self.user)
		response = self.client.get(reverse("result", args=(attempt.pk,)))
		self.assertEqual(response.status_code, 403)

	def test_unpublished_quiz_is_not_available(self):
		self.quiz.is_published = False
		self.quiz.save(update_fields=("is_published",))
		self.client.force_login(self.user)
		response = self.client.get(reverse("take_quiz", args=(self.quiz.pk,)))
		self.assertEqual(response.status_code, 404)
