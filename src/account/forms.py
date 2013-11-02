from django import forms
from core.models import User
from django.utils.translation import ugettext as _

class UpdateUserForm(forms.Form):
    email = forms.EmailField(required=True)
    current_password = forms.CharField(required=False, widget=forms.PasswordInput(), label=_("Current password"))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(), label=_("New password"))
    confirm_new_password = forms.CharField(required=False, widget=forms.PasswordInput(), label=_("Confirm password"))

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_('Wrong password.'))

        return current_password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        count = User.objects.filter(email=email.lower()).exclude(username=self.user.username.lower()).count()
        if (count):
            raise forms.ValidationError(_('Email must be unique.'))

        return email.lower()

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError(_("Enter the same password as above, for verification."))

        return confirm_new_password

    def save(self):
        email = self.cleaned_data.get('email')
        if self.user.email is not email:
            self.user.email = email

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            self.user.set_password(new_password)

        return self.user.save()
