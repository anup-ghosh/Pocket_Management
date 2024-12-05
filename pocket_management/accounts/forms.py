from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # Regular expression for validating phone numbers
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+016XXXXXXXX'. Up to 15 digits allowed."
    )

    username = forms.CharField(
        label="Username",
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'autocomplete': 'username',
        })
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )

    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name',
        })
    )

    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name',
        })
    )

    phone_number = forms.CharField(
        label="Phone Number",
        validators=[phone_regex],
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+999999999',
            'autocomplete': 'tel',
        })
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
            'data-toggle': 'password',
        }),
        help_text="""
            <ul class="text-muted small">
                <li>At least 8 characters long</li>
                <li>Must include uppercase and lowercase letters</li>
                <li>Must include at least one number</li>
                <li>Must include at least one special character</li>
            </ul>
        """
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
            'data-toggle': 'password',
        })
    )

    preferred_currency = forms.ChoiceField(
        label="Preferred Currency",
        choices=CustomUser.CURRENCY_CHOICES,
        initial='BDT',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    monthly_budget = forms.DecimalField(
        label="Monthly Budget",
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Set your monthly budget',
            'step': '0.01',
        })
    )

    savings_goal = forms.DecimalField(
        label="Savings Goal",
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Set your savings goal',
            'step': '0.01',
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'preferred_currency', 'monthly_budget', 
            'savings_goal', 'password1', 'password2'
        ]

    def clean_username(self):
        """Ensure username is unique and meets requirements."""
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters long.")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        """Ensure email is unique and valid."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_password1(self):
        """Ensure password meets complexity requirements."""
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one number.")
        if not any(not char.isalnum() for char in password):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password

    def clean(self):
        """Additional validation for the entire form."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "The two password fields must match.")

        # Ensure first_name and last_name don't contain numbers
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if first_name and any(char.isdigit() for char in first_name):
            self.add_error('first_name', "First name should not contain numbers.")
            
        if last_name and any(char.isdigit() for char in last_name):
            self.add_error('last_name', "Last name should not contain numbers.")

        return cleaned_data

    def save(self, commit=True):
        """Save the user with additional fields."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.preferred_currency = self.cleaned_data['preferred_currency']
        
        if self.cleaned_data.get('monthly_budget'):
            user.monthly_budget = self.cleaned_data['monthly_budget']
        if self.cleaned_data.get('savings_goal'):
            user.savings_goal = self.cleaned_data['savings_goal']

        if commit:
            user.save()
        return user