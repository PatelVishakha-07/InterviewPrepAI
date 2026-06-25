from django.urls import path
from . import views

urlpatterns = [
    path("generate/", views.generate_questions, name="generate"),
    path("history/", views.history, name="history"),
    path("history/<int:id>", views.session_detail, name="session_detail"),
    path("delete/<int:id>", views.delete_session, name="delete_session"),
    path("download/<int:id>", views.download_pdf, name="download_pdf"),
]