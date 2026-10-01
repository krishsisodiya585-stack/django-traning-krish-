from django.db import models


class Student(models.Model):
	student_id = models.CharField(max_length=30, unique=True)
	name = models.CharField(max_length=120)
	password = models.CharField(max_length=128)
	email = models.EmailField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} ({self.student_id})"
