from django import forms

from .models import BookIssue


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ('book_id', 'book_name', 'book_number', 'student_name', 'issue_date', 'due_date')
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'book_id': 'Book ID',
            'book_name': 'Book name',
            'book_number': 'Book number',
            'student_name': 'Student name',
            'issue_date': 'Issue date',
            'due_date': 'Due date',
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')
        if issue_date and due_date and due_date < issue_date:
            self.add_error('due_date', 'Due date must be on or after the issue date.')
        return cleaned_data