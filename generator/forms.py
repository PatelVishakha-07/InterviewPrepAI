from django import forms

class InterviewForm(forms.Form):
    role = forms.CharField(max_length=50)

    level_choice = [("Fresher","Fresher"), ("Intermediate","Intermediate"), ("Advanced", "Advanced")]

    level = forms.ChoiceField(choices=level_choice)