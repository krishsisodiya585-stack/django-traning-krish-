from django.test import TestCase

from .models import Student


class StudentCrudTests(TestCase):
	def setUp(self):
		self.student_data = {
			'student_id': 'STU-1',
			'student_name': 'Asha Sharma',
			'student_branch': 'Computer Science',
		}

	def test_read_page_is_available(self):
		response = self.client.get('/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No student records found.')

	def test_create_update_and_delete_student(self):
		response = self.client.post('/create/', self.student_data)

		self.assertRedirects(response, '/')
		self.assertTrue(Student.objects.filter(pk='STU-1').exists())

		response = self.client.post('/update/STU-1/', {
			'student_name': 'Asha Singh',
			'student_branch': 'Information Technology',
		})

		self.assertRedirects(response, '/')
		student = Student.objects.get(pk='STU-1')
		self.assertEqual(student.student_name, 'Asha Singh')
		self.assertEqual(student.student_branch, 'Information Technology')

		response = self.client.post('/delete/STU-1/')

		self.assertRedirects(response, '/')
		self.assertFalse(Student.objects.filter(pk='STU-1').exists())

	def test_update_page_loads_with_student(self):
		student = Student.objects.create(**self.student_data)

		response = self.client.get(f'/update/{student.student_id}/')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, student.student_name)

	def test_create_rejects_duplicate_id_and_blank_fields(self):
		Student.objects.create(**self.student_data)

		duplicate_response = self.client.post('/create/', self.student_data)
		blank_response = self.client.post('/create/', {
			'student_id': '',
			'student_name': 'Asha Sharma',
			'student_branch': 'Computer Science',
		})

		self.assertEqual(duplicate_response.status_code, 200)
		self.assertContains(duplicate_response, 'This student ID already exists.')
		self.assertEqual(blank_response.status_code, 200)
		self.assertContains(blank_response, 'All student fields are required.')
		self.assertEqual(Student.objects.count(), 1)
