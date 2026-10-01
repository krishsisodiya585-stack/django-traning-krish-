from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from .models import Student


class StudentFlowTests(TestCase):
	def test_registration_saves_hashed_password_and_redirects_to_login(self):
		response = self.client.post(
			reverse("register"),
			{
				"student_id": "STU-014",
				"name": "Asha Patel",
				"password": "strong-password",
				"email": "asha@example.com",
			},
		)

		student = Student.objects.get(student_id="STU-014")
		self.assertRedirects(response, reverse("login"))
		self.assertTrue(check_password("strong-password", student.password))
		self.assertNotEqual(student.password, "strong-password")

	def test_login_requires_registered_student_and_gates_prediction(self):
		response = self.client.post(
			reverse("login"),
			{"name": "Missing Student", "password": "password"},
		)
		self.assertContains(response, "Register first")
		self.assertRedirects(self.client.get(reverse("predict")), reverse("login"))

	def test_prediction_scales_scores_in_model_feature_order(self):
		student = Student.objects.create(
			student_id="STU-015",
			name="Ravi Shah",
			password="unused",
			email="ravi@example.com",
		)
		session = self.client.session
		session["student_id"] = student.pk
		session["student_name"] = student.name
		session.save()

		class FakeScaler:
			def transform(self, values):
				self.values = values
				return values

		class FakeModel:
			def predict(self, values):
				return [1]

		scaler = FakeScaler()
		with patch("placement.views.get_prediction_artifacts", return_value=(FakeModel(), scaler)):
			response = self.client.post(
				reverse("predict"),
				{"cgpa": "8.5", "iq": "110", "profile_score": "76"},
			)

		self.assertContains(response, "Positive outlook")
		self.assertEqual(scaler.values, [[8.5, 110.0, 76.0]])
