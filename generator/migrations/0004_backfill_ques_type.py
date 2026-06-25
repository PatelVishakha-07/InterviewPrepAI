import json
from django.db import migrations


def backfill_ques_type(apps, schema_editor):
    InterviewSession = apps.get_model("generator", "InterviewSession")

    for session in InterviewSession.objects.all():
        if session.ques_type:
            continue

        try:
            data = json.loads(session.generated_ques)
            if isinstance(data, list) and data and "options" in data[0]:
                session.ques_type = "mcq"
            else:
                session.ques_type = "qa"
        except Exception:
            session.ques_type = "qa"

        session.save(update_fields=["ques_type"])


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("generator", "0003_interviewsession_ques_type"),
    ]

    operations = [
        migrations.RunPython(backfill_ques_type, reverse_backfill),
    ]