from django.contrib import admin
from .models import BookIssue


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
	list_display = ('book_id', 'book_name', 'student_name', 'issue_date', 'due_date', 'issued_by')
	search_fields = ('book_id', 'book_name', 'student_name')
	list_filter = ('issue_date', 'due_date')
