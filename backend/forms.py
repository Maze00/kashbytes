from django import forms


# ---------------------------------------------------------------
# Change user data form for admin, it will helps to activate and
# deactivate the users
# ---------------------------------------------------------------
class ChangeUserDataForm(forms.Form):

    CHOICES = (
        (True, 'Activate'),
        (False, 'Deactivate')
    )

    action = forms.CharField(
        widget=forms.Select(choices=CHOICES, attrs={"class": "form-control"})
    )
