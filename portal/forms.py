from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search articles or error codes",
                "aria-label": "Search",
            }
        ),
    )
