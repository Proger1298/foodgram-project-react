from django.contrib import admin

from users.models import BlackListedToken, Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email', )
    empty_value_display = '-empty-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


@admin.register(BlackListedToken)
class BlackListedTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'token',
        'timestamp'
    )
