# Checkmate Online Testing

A Django MCQ testing app for the `task8` project. It uses Django's built-in user authentication and SQLite by default.

## Run it

From the `task8` directory in PowerShell:

```powershell
..\workspace\Scripts\python.exe manage.py migrate
..\workspace\Scripts\python.exe manage.py seed_sample_quizzes
..\workspace\Scripts\python.exe manage.py createsuperuser
..\workspace\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/` to register as a student. Use `/admin/` with the superuser to publish and manage quizzes, questions, and choices. Each question needs at least two choices and exactly one correct choice.

## Data model

- `auth.User` stores usernames and Django-hashed passwords.
- `StudentProfile` stores a student's full name and unique email; each profile belongs to one user.
- `Quiz` contains published test metadata.
- `Question` belongs to a quiz and has a unique position within it.
- `Choice` belongs to a question and has a unique position within it.
- `Attempt` links one student to one quiz attempt and snapshots the submitted score. A student can have many completed attempts but only one open attempt per quiz.
- `Answer` links one attempt to one question, records the selected choice, and snapshots correctness, awarded points, possible points, and the correct answer text.

Quiz submissions are scored on the server and saved in a database transaction. Students can only view their own results; staff can review all attempts in the admin.