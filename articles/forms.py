from django import forms

class ExpressionForm(forms.Form):
    expression = forms.ChoiceField(choices=[('Orbán', 'Orbán'), ('Gyurcsány', 'Gyurcsány')], widget=forms.CheckboxSelectMultiple)
