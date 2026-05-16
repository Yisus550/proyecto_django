from django import forms

from .models import Lugar, Visita


class VisitaForm(forms.ModelForm):
    # lugar = forms.ModelChoiceField(
    #         queryset=Lugar.objects.all(),
    #         empty_label="-- Seleccione un lugar --",
    #         label="Lugar*"
    #         )

    class Meta:
        model = Visita
        fields = ["lugar", "fecha", "resena", "calificacion", "platillo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "resena": forms.Textarea(attrs={"rows": 3}),
            "calificacion": forms.NumberInput(attrs={"min": 1, "max": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
