# Django Training Projects

This repository contains Django exercises and related learning projects, organized into separate folders.

To run an individual Django project, open its folder containing `manage.py`, install its dependencies, and run:

```powershell
python manage.py migrate
python manage.py runserver
```

The `task10` folder contains a library management system with librarian signup/login, a dashboard, and book issue records. It uses SQLite by default; optional MySQL synchronization is configured through environment variables in `task10/task10/settings.py`.