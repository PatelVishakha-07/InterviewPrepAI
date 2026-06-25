import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .gemini_service import get_questions
from .models import InterviewSession
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER


@login_required
def generate_questions(request):
    questions = None
    ques_type = None

    if request.method == "POST":
        role = request.POST.get("role")
        difficulty = request.POST.get("difficulty")
        no_of_ques = request.POST.get("num_questions")
        ques_type = request.POST.get("question_type")

        # get_questions returns a Python list/dict — keep it for rendering
        questions = get_questions(role, difficulty, no_of_ques, ques_type)

        # Save as JSON string in the database
        InterviewSession.objects.create(
            user=request.user,
            role=role,
            difficulty=difficulty,
            no_of_ques=no_of_ques,
            ques_type=ques_type,                      # new field — see models.py
            generated_ques=json.dumps(questions),
        )

    return render(request, "generate_questions.html", {
        "questions": questions,
        "ques_type": ques_type,
    })


@login_required
def history(request):
    sessions = InterviewSession.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "history.html", {"sessions": sessions})


@login_required
def session_detail(request, id):
    session = get_object_or_404(InterviewSession, id=id, user=request.user)

    try:
        questions = json.loads(session.generated_ques)
        if not isinstance(questions, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):

        questions = [{"question": line, "answer": "", "explanation": ""}
                     for line in session.generated_ques.splitlines() if line.strip()]

    return render(request, "session_detail.html", {
        "session": session,
        "questions": questions,
    })


@login_required
def delete_session(request, id):
    session = get_object_or_404(InterviewSession, id=id, user=request.user)
    session.delete()
    return redirect("history")

@login_required
def download_pdf(request, id):
    session = get_object_or_404(InterviewSession, id=id, user=request.user)

    try:
        questions = json.loads(session.generated_ques)
        if not isinstance(questions, list):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        questions = [{"questions":line, "answer":"", "explanation":""}
                     for line in session.generated_ques.splitlines() if line.strip()]
        
    response = HttpResponse(content_type = "application/pdf")
    filename = f"interview_{session.role.replace(' ','_')}_{session.id}.pdf"

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response,
        pagesize = A4,
        leftMargin = 20*mm,
        rightMargin = 20*mm,
        topMargin = 20*mm,
        bottomMargin = 20*mm,
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "Title",
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_CENTER,
        spaceAfter=4
    )

    style_subtitle = ParagraphStyle(
        "Subtitle",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    style_meta = ParagraphStyle(
        "QLabel",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=2,
    )

    style_q_label = ParagraphStyle(
        "QLabel",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=2,
    )

    style_question = ParagraphStyle(
        "Question",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
        leading=16,
    )

    style_answer_label = ParagraphStyle(
        "AnswerLabel",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#16a34a"),
        spaceAfter=2,
    )

    style_answer = ParagraphStyle(
        "Answer",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
        leading=15,
    )

    style_explanation = ParagraphStyle(
        "Explanation",
        fontSize=9,
        fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#1e40af"),
        spaceAfter=0,
        leading=14,
        leftIndent=8,
        borderPad=4,
    )

    style_option = ParagraphStyle(
        "Option",
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#334155"),
        spaceAfter=3,
        leading=14,
    )

    style_correct = ParagraphStyle(
        "Correct",
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#166534"),
        spaceAfter=3,
        leading=14,
    )

    story = []
    story.append(Paragraph("🤖 AI Interview Question Generator", style_title))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"Role: {session.role}  •  Difficulty: {session.difficulty}  •  Type: {session.get_ques_type_display()}", style_subtitle))
    story.append(Paragraph(f"Generated on {session.created_at.strftime('%d %b %Y, %I:%M %p')}  •  {session.no_of_ques} Questions", style_meta))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb")))
    story.append(Spacer(1, 6*mm))

    if session.ques_type == "mcq":
        for i, item in enumerate(questions, 1):
            # Question block background via Table
            q_text = item.get("question", "")
            correct = item.get("answer", "")
            explanation = item.get("explanation", "")
            options = item.get("options", {})
 
            story.append(Paragraph(f"QUESTION {i}", style_q_label))
            story.append(Paragraph(q_text, style_question))

            # Options
            for key, val in options.items():
                is_correct = (key == correct)
                label = f"{'✓ ' if is_correct else ''}{key}. {val}"
                story.append(Paragraph(label, style_correct if is_correct else style_option))
 
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph(f"✅ Correct Answer: {correct}", style_answer_label))

            if explanation:
                story.append(Paragraph(f"Explanation: {explanation}", style_explanation))
 
            story.append(Spacer(1, 4*mm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
            story.append(Spacer(1, 4*mm))
        
        else:
            for i, item in enumerate(questions, 1):
                q_text = item.get("question", "")
                answer = item.get("answer", "")
                explanation = item.get("explanation", "")
    
                story.append(Paragraph(f"QUESTION {i}", style_q_label))
                story.append(Paragraph(q_text, style_question))
                story.append(Paragraph("Answer:", style_answer_label))
                story.append(Paragraph(answer, style_answer))

                if explanation:
                    story.append(Paragraph(f"Explanation: {explanation}", style_explanation))
    
                story.append(Spacer(1, 4*mm))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
                story.append(Spacer(1, 4*mm))

        doc.build(story)
        return response