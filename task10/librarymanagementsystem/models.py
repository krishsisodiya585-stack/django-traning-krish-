from django.db import models
from django.contrib.auth.models import User


class BookIssue(models.Model):
	book_id = models.CharField(max_length=30)
	book_name = models.CharField(max_length=160)
	book_number = models.CharField(max_length=30)
	student_name = models.CharField(max_length=120)
	issue_date = models.DateField()
	due_date = models.DateField()
	issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_issues')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-issue_date', '-created_at']

	def __str__(self):
		return f'{self.book_name} - {self.student_name}'
