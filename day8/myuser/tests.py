from django.test import TestCase
from django.urls import reverse
from .models import Student, user


class SignUpTests(TestCase):
	def test_signup_page_renders(self):
		response = self.client.get(reverse('sign_up'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Create your account')
		self.assertContains(response, 'name')

	def test_signup_creates_user_with_hashed_password(self):
		response = self.client.post(reverse('sign_up'), {
			'name': 'Asha Sharma',
			'username': 'asha',
			'password': 'StrongPass!2026',
			'confirm_password': 'StrongPass!2026',
		})

		account = user.objects.get(username='asha')
		self.assertRedirects(response, reverse('login'))
		self.assertTrue(account.check_password('StrongPass!2026'))
		self.assertNotEqual(account.password, 'StrongPass!2026')
		self.assertNotIn('username', self.client.session)

	def test_signup_rejects_mismatched_passwords(self):
		response = self.client.post(reverse('sign_up'), {
			'name': 'Asha Sharma',
			'username': 'asha',
			'password': 'StrongPass!2026',
			'confirm_password': 'DifferentPass!2026',
		})

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].errors['confirm_password'])
		self.assertFalse(user.objects.filter(username='asha').exists())

	def test_login_accepts_correct_credentials(self):
		account = user.objects.create(username='asha', name='Asha Sharma')
		account.set_password('StrongPass!2026')
		account.save()

		response = self.client.post(reverse('login'), {
			'username': 'asha',
			'password': 'StrongPass!2026',
		})

		self.assertRedirects(response, reverse('student_register'))
		self.assertEqual(self.client.session['username'], 'asha')
		self.assertEqual(self.client.session['name'], 'Asha Sharma')

	def test_student_registration_requires_login(self):
		response = self.client.get(reverse('student_register'))

		self.assertRedirects(response, reverse('login'))

	def test_student_registration_is_saved_for_signed_in_account(self):
		account = user.objects.create(username='asha', name='Asha Sharma')
		session = self.client.session
		session['username'] = account.username
		session.save()

		response = self.client.post(reverse('student_register'), {
			'student_id': 'STU-101',
			'student_name': 'Asha Sharma',
			'branch': 'Computer Science',
		})

		registration = Student.objects.get(student_id='STU-101')
		self.assertRedirects(response, reverse('home'))
		self.assertEqual(registration.registered_by, account)
		home_response = self.client.get(reverse('home'))
		self.assertContains(home_response, 'STU-101')
		self.assertContains(home_response, 'href="#database">See database</a>')

	def test_login_rejects_incorrect_password(self):
		account = user.objects.create(username='asha', name='Asha Sharma')
		account.set_password('StrongPass!2026')
		account.save()

		response = self.client.post(reverse('login'), {
			'username': 'asha',
			'password': 'WrongPass!2026',
		})

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['form'].non_field_errors())
		self.assertNotIn('username', self.client.session)
