from django import forms
from .models import City
from telegram_auth.models import ParserSetting

class ParserForm(forms.ModelForm):
    city = forms.ModelChoiceField(queryset=City.objects.all(), label="Город")

    class Meta:
        model = ParserSetting
        fields = ['city', 'keywords', 'excludes', 'groups']
        widgets = {
            'keywords': forms.HiddenInput(attrs={'id': 'id_keywords'}),
            'excludes': forms.HiddenInput(attrs={'id': 'id_excludes'}),  # Добавьте это
            'groups': forms.HiddenInput(attrs={'id': 'id_groups'}),
        }