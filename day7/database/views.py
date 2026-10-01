from django.shortcuts import get_object_or_404, redirect, render

from .models import Student


def student_list(request):
	students = Student.objects.all().order_by('student_id')
	return render(request, 'emp_list.html', {'students': students})


def student_create(request):
	form_data = {}
	error = None
	if request.method == 'POST':
		form_data = {
			'student_id': request.POST.get('student_id', '').strip(),
			'student_name': request.POST.get('student_name', '').strip(),
			'student_branch': request.POST.get('student_branch', '').strip(),
		}
		if not all(form_data.values()):
			error = 'All student fields are required.'
		elif Student.objects.filter(pk=form_data['student_id']).exists():
			error = 'This student ID already exists.'
		else:
			Student.objects.create(**form_data)
			return redirect('student_list')
	return render(request, 'emp_list.html', {
		'students': Student.objects.all(),
		'action': 'create',
		'form_data': form_data,
		'error': error,
	})


def student_update(request, student_id):
	student = get_object_or_404(Student, student_id=student_id)
	error = None
	if request.method == 'POST':
		student_name = request.POST.get('student_name', '').strip()
		student_branch = request.POST.get('student_branch', '').strip()
		if not student_name or not student_branch:
			error = 'Student name and branch are required.'
		else:
			student.student_name = student_name
			student.student_branch = student_branch
			student.save()
			return redirect('student_list')
	return render(request, 'emp_list.html', {
		'students': Student.objects.all(),
		'student': student,
		'action': 'update',
		'error': error,
	})


def student_delete(request, student_id):
	student = get_object_or_404(Student, student_id=student_id)
	if request.method == 'POST':
		student.delete()
	return redirect('student_list')
