from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Account, Post, Category, Comment, CartItem, Message, Transaction

# Register your models here.
class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInline, ) #tuple

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user','freelancer_key']

admin.site.register(Post)
admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(CartItem)
admin.site.register(Message)
