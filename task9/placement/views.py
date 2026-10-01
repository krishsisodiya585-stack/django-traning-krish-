from functools import lru_cache
from pathlib import Path

import joblib
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .models import Student


@lru_cache(maxsize=1)
def get_prediction_artifacts():
	project_root = Path(__file__).resolve().parent.parent
	model = joblib.load(project_root / "mlmodel (1).pkl")
	scaler = joblib.load(project_root / "scalermodel (1).pkl")
	return model, scaler


def home(request):
	return render(request, "placement/home.html")


def register(request):
	if request.method == "POST":
		student_id = request.POST.get("student_id", "").strip()
		name = request.POST.get("name", "").strip()
		password = request.POST.get("password", "")
		email = request.POST.get("email", "").strip()

		if not all((student_id, name, password, email)):
			messages.error(request, "Please complete every field.")
		elif Student.objects.filter(student_id=student_id).exists():
			messages.error(request, "That student ID is already registered.")
		elif Student.objects.filter(name__iexact=name).exists():
			messages.error(request, "That student name is already registered. Please use your registered name at login.")
		elif Student.objects.filter(email__iexact=email).exists():
			messages.error(request, "That email address is already registered.")
		else:
			Student.objects.create(
				student_id=student_id,
				name=name,
				password=make_password(password),
				email=email,
			)
			messages.success(request, "Registration complete. Log in to continue.")
			return redirect("login")

	return render(request, "placement/register.html")


def login(request):
	if request.session.get("student_id"):
		return redirect("predict")

	if request.method == "POST":
		name = request.POST.get("name", "").strip()
		password = request.POST.get("password", "")
		student = Student.objects.filter(name__iexact=name).first()

		if student and check_password(password, student.password):
			request.session.cycle_key()
			request.session["student_id"] = student.pk
			request.session["student_name"] = student.name
			return redirect("predict")

		messages.error(request, "No matching account found. Register first, then try logging in.")

	return render(request, "placement/login.html")


def logout(request):
	request.session.flush()
	messages.info(request, "You have been logged out.")
	return redirect("home")


def predict(request):
	if not request.session.get("student_id"):
		messages.warning(request, "Please log in before starting a prediction.")
		return redirect("login")

	if request.method == "POST":
		try:
			values = {
				"cgpa": float(request.POST.get("cgpa", "")),
				"iq": float(request.POST.get("iq", "")),
				"profile_score": float(request.POST.get("profile_score", "")),
			}
		except (TypeError, ValueError):
			messages.error(request, "Enter a valid number for each score.")
			return render(request, "placement/predict.html")

		limits = {"cgpa": (0, 10), "iq": (0, 200), "profile_score": (0, 100)}
		if any(not low <= values[key] <= high for key, (low, high) in limits.items()):
			messages.error(request, "CGPA must be 0-10, IQ 0-200, and profile score 0-100.")
			return render(request, "placement/predict.html")

		features = [[values["cgpa"], values["iq"], values["profile_score"]]]
		model, scaler = get_prediction_artifacts()
		scaled_features = scaler.transform(features)
		prediction = int(model.predict(scaled_features)[0])
		return render(
			request,
			"placement/result.html",
			{"placed": prediction == 1, "scores": values},
		)

	return render(request, "placement/predict.html")
