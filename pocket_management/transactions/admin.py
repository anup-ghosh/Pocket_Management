from django.contrib import admin

# Register your models here.
from .models import Transaction
from .models import Budget
from .models import CustomUser


admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(CustomUser)
