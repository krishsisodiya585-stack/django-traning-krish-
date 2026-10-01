from django.db import models
from django.contrib.auth.hashers import check_password, make_password

# Create your models here.
class user(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=20)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=80)
    branch = models.CharField(max_length=80)
    registered_by = models.ForeignKey(
        user,
        on_delete=models.CASCADE,
        related_name='student_registrations',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student_id} - {self.student_name}'