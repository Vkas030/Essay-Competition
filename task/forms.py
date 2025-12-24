from django import forms
from .models import UserTask
import re


class TaskForm(forms.ModelForm):
    class Meta:
        model = UserTask
        fields = ["essay_title", "essay_text"]
        widgets = {
            "essay_title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter essay title"
            }),
            "essay_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Write your essay here..."
            }),
        }

    def clean_essay_text(self):
        text = self.cleaned_data.get("essay_text", "")
        plain_text = re.sub("<[^<]+?>", "", text).strip()

        if len(plain_text) < 500:
            raise forms.ValidationError(
                "Essay must be at least 500 characters long."
            )

        return text
