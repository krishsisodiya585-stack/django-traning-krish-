from django.db import models


class Student(models.Model):
	student_id = models.CharField(max_length=20, primary_key=True)
	student_name = models.CharField(max_length=100)
	student_branch = models.CharField(max_length=100)

	def __str__(self):
		return f'{self.student_id} - {self.student_name}'
