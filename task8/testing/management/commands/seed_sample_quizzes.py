from django.core.management.base import BaseCommand
from django.db import transaction

from testing.models import Choice, Question, Quiz


SAMPLE_QUIZZES = (
    {
        "title": "Everyday Science",
        "description": "A quick check of the science concepts you meet every day.",
        "questions": (
            ("Which planet is known as the Red Planet?", 1, (("Mars", True), ("Venus", False), ("Jupiter", False), ("Mercury", False))),
            ("What gas do plants absorb from the air?", 1, (("Oxygen", False), ("Carbon dioxide", True), ("Nitrogen", False), ("Hydrogen", False))),
            ("At sea level, water boils at what temperature?", 1, (("50°C", False), ("90°C", False), ("100°C", True), ("120°C", False))),
        ),
    },
    {
        "title": "Numbers & Logic",
        "description": "Warm up your problem-solving skills with a few fundamentals.",
        "questions": (
            ("What is 12 × 8?", 1, (("86", False), ("96", True), ("108", False), ("88", False))),
            ("Which number is prime?", 1, (("21", False), ("27", False), ("29", True), ("33", False))),
            ("What is the next number in the sequence 2, 4, 8, 16?", 1, (("24", False), ("30", False), ("32", True), ("36", False))),
        ),
    },
    {
        "title": "Digital Basics",
        "description": "Review the building blocks behind computers and the web.",
        "questions": (
            ("What does CPU stand for?", 1, (("Central Processing Unit", True), ("Computer Power Utility", False), ("Core Program Upload", False), ("Central Program User", False))),
            ("Which language is used to structure web pages?", 1, (("HTML", True), ("SQL", False), ("Bash", False), ("R", False))),
            ("How many bits are in a byte?", 1, (("4", False), ("8", True), ("16", False), ("32", False))),
        ),
    },
)


class Command(BaseCommand):
    help = "Create three sample quizzes for trying the student workflow."

    def handle(self, *args, **options):
        created_count = 0
        for sample in SAMPLE_QUIZZES:
            with transaction.atomic():
                quiz, _ = Quiz.objects.get_or_create(
                    title=sample["title"],
                    defaults={"description": sample["description"], "is_published": True},
                )
                if quiz.questions.exists():
                    self.stdout.write(f"Kept existing quiz: {quiz.title}")
                    continue

                for question_position, (text, points, choices) in enumerate(sample["questions"], start=1):
                    question = Question.objects.create(
                        quiz=quiz,
                        text=text,
                        points=points,
                        position=question_position,
                    )
                    Choice.objects.bulk_create(
                        [
                            Choice(question=question, text=choice_text, is_correct=is_correct, position=position)
                            for position, (choice_text, is_correct) in enumerate(choices, start=1)
                        ]
                    )
                quiz.is_published = True
                quiz.save(update_fields=("is_published",))
                created_count += 1
                self.stdout.write(f"Created sample quiz: {quiz.title}")

        self.stdout.write(self.style.SUCCESS(f"Ready. Created {created_count} sample quiz(es)."))