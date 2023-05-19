from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from django.forms import PasswordInput

from .models import Account, Category, Post, Profile, Comment
from ckeditor.fields import RichTextField

class UserSellerRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Apellido',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre de Usuario',
    }))
    freelancer_key = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Clave de freelancer',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Correo Electrónico'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar Contraseña',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'freelancer_key']
    
    def clean_freelancer_key(self):
        freelancer_key = self.cleaned_data.get('freelancer_key')
        if Account.objects.filter(freelancer_key=freelancer_key).exists():
            raise ValidationError('Esta clave de identificación ya está registrada.')
        return freelancer_key

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        account = Account(user=user, freelancer_key=self.cleaned_data['freelancer_key'])
        account.save()
        return user
    
class UserBuyerRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Apellido',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre de Usuario',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Correo Electrónico'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirmar Contraseña',
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('','Buscar categoría escribiendo')] + list(self.fields['category'].choices)[1:]

    detailed_description = RichTextField()
    STATUS_CHOICES = (
        ('1 día', '1 día'),
        ('2 días', '2 días'),
        ('3 días', '3 días'),
        ('4 días', '4 días'),
        ('5 días', '5 días'),
        ('6 días', '6 días'),
        ('1 semana', '1 semana'),
        ('2 semanas', '2 semanas'),
        ('3 semanas', '3 semanas'),
        ('1 mes', '1 mes'),
        ('2 meses', '2 meses'),
    )
    delivery_time = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control', 
    }))
    image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image2 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image3 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    price = forms.DecimalField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Introduce el precio aquí (por ejemplo, 10.99)',
    }))
    is_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
        'style': 'width: 22px; height: 22px;',
    }), required=True)

    class Meta:
        model = Post
        fields = ['category', 'title', 'content', 'delivery_time', 'detailed_description', 'image', 'image2', 'image3', 'price', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el título aquí',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explica brevemente sobre ti y que haces',
                'rows': 10,
            }),
        }

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Apellido',
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Nombre de Usuario',
    }))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Correo Electrónico'
    }))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    user_image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Bio',
        'rows': 5,
        'cols': 40,
    }))
    class Meta:
        model = Profile
        fields = ['user_image', 'bio']

class UpdatePostForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={
        'class': 'form-control',
    }), empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = [('','Buscar categoría escribiendo')] + list(self.fields['category'].choices)[1:]

    STATUS_CHOICES = (
        ('1 día', '1 día'),
        ('2 días', '2 días'),
        ('3 días', '3 días'),
        ('4 días', '4 días'),
        ('5 días', '5 días'),
        ('6 días', '6 días'),
        ('1 semana', '1 semana'),
        ('2 semanas', '2 semanas'),
        ('3 semanas', '3 semanas'),
        ('1 mes', '1 mes'),
        ('2 meses', '2 meses'),
    )
    delivery_time = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control', 
    }))
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Título',
    }))
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Contenido',
        'rows': 5,
        'cols': 40,
    }))
    detailed_description = RichTextField()
    price = forms.DecimalField(widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Introduce el precio aquí (por ejemplo, 10.99)',
    }))
    is_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input custom-control-input',
        'id': 'customSwitch2',
    }))
    image = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image2 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    image3 = forms.ImageField(widget=ClearableFileInput(attrs={
        'class': 'form-control',
    }), required=False)
    class Meta:
        model = Post
        fields = [
            'category', 'title', 'content', 'delivery_time', 'detailed_description', 
            'image', 'image2', 'image3', 'price', 'is_active',
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Ingrese su reseña aquí...',
                'rows': 4,
                'cols': 50
            }),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'id': 'reply-input',
                'placeholder': 'Ingrese su reseña aquí...',
                'rows': 1,
            }),
        }

class PasswordConfirmationForm(forms.Form):
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control'}), label='Password')
