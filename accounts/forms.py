from django import forms
from .models import Account    

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'class': 'mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
        'class': 'mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = (
                'mt-1 block w-full rounded-md border border-gray-300 shadow-sm '
                'focus:ring-teal-500 focus:border-teal-500 sm:text-sm p-2 text-black'
            )

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password  = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )
