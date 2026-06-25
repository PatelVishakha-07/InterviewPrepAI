from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class InterviewSession(models.Model):
    QUESTION_TYPE_CHOICE = [
        ("qa", "Questions & Answers"),
        ("mcq", "MCQ")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20)
    no_of_ques = models.IntegerField()

    ques_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICE, default="qa")

    generated_ques = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} ({self.ques_type})"

""" class InterviewHistory(models.Model):
    role = models.CharField(max_length=50)
    level = models.CharField(max_length=50)
    generated_question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.role """