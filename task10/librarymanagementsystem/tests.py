from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .models import BookIssue


class LibraryWorkflowTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='librarian', password='safe-password-123', first_name='Aisha')

	def test_signup_creates_account_and_logs_user_in(self):
		response = self.client.post('/signup/', {
			'name': 'Ravi Kumar',
			'username': 'ravi',
			'password': 'safe-password-123',
			'confirm_password': 'safe-password-123',
		})

		self.assertRedirects(response, '/dashboard/')
		self.assertTrue(User.objects.filter(username='ravi', first_name='Ravi Kumar').exists())
		self.assertIn('_auth_user_id', self.client.session)

	@patch('librarymanagementsystem.views.mirror_issue_to_mysql')
	def test_issue_is_saved_and_shown_in_book_list(self, mirror_issue):
		self.client.force_login(self.user)
		response = self.client.post('/issue/', {
			'book_id': '1',
			'book_name': 'Python Basics',
			'book_number': 'B001',
			'student_name': 'Aisha Khan',
			'issue_date': '2026-09-10',
			'due_date': '2026-10-10',
		})

		issue = BookIssue.objects.get(book_name='Python Basics')
		self.assertEqual(issue.issued_by, self.user)
		mirror_issue.assert_called_once_with(issue)
		self.assertRedirects(response, f'/issue/{issue.pk}/success/')
		list_response = self.client.get('/books/')
		self.assertContains(list_response, 'Python Basics')
		self.assertContains(list_response, 'Aisha Khan')

	def test_due_date_before_issue_date_is_rejected(self):
		self.client.force_login(self.user)
		response = self.client.post('/issue/', {
			'book_id': '1',
			'book_name': 'Python Basics',
			'book_number': 'B001',
			'student_name': 'Aisha Khan',
			'issue_date': '2026-09-10',
			'due_date': '2026-09-09',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Due date must be on or after the issue date.')
		self.assertEqual(BookIssue.objects.count(), 0)

	def test_issue_page_requires_login(self):
		response = self.client.get('/issue/')

		self.assertRedirects(response, '/login/?next=/issue/')
