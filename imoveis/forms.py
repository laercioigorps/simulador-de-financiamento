from django import forms
from django.core.exceptions import ValidationError
import datetime


class SimulacaoFormulario(forms.Form):
    valor_do_imovel = forms.DecimalField(min_value=0)
    valor_da_entrada = forms.DecimalField(min_value=0)
    data_nascimento = forms.DateField()
    prestacoes = forms.ChoiceField(
        choices=(("120", "120"), ("180", "180"), ("240", "240"), ("360", "360"))
    )
    incluir_ITBI = forms.BooleanField(required=False)
    amortizacao = forms.ChoiceField(choices=(("SAC", "SAC"), ("PRICE", "PRICE")))

    def clean(self):
        cleaned_data = super().clean()
        v_imovel = cleaned_data.get("valor_do_imovel")
        v_entrada = cleaned_data.get("valor_da_entrada")

        if v_entrada and v_imovel and (v_entrada < (v_imovel * 20 / 100)):
            self.add_error(
                "valor_da_entrada",
                "Entrada não pode ser menor que 20% do valor do imovel",
            )

        return cleaned_data

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get("data_nascimento")
        hoje = datetime.date.today()
        mesmo_dia_18_anos_atras = datetime.date(
            day=hoje.day, month=hoje.month, year=hoje.year - 18
        )
        if data_nascimento > mesmo_dia_18_anos_atras:
            raise ValidationError(
                "É necessario ser maior de idade para realizar financiamento!"
            )

        return data_nascimento
