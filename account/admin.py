from django.contrib import admin
from account.models import Account
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class AccountAdmin(BaseUserAdmin):

    @admin.display(description='📅 Joined date')
    def get_local_date_joined(self, obj):
        return timezone.localtime(obj.created_at).strftime('%d %B %Y %H:%M')
    get_local_date_joined.admin_order_field = 'created_at'

    @admin.display(description='Changed nickname')
    def get_local_date_changed(self, obj):
        return obj.changed_nickname.strftime('%d %B %Y %H:%M')
    
    @admin.display(description='Subscribers')
    def get_subscribers(self, obj):
        return obj.get_subcribers_count()
    
    # @admin.display(description='Posts')
    # def get_posts(self, obj):
    #     return obj.get_posts_count()

    list_display = ('username', 'id', 'email', 'get_local_date_joined', 'get_subscribers', 'is_verify', 'is_moderator', 'is_admin')
    list_filter = ('is_verify', 'is_moderator', 'is_admin', 'created_at',)
    fieldsets = (
        ('User credentials', {
            'fields': ('nickname', 'email')
        },),
        ('Personal info', {
            'fields': (('username', 'changed_nickname'), ('image_tag', 'image_tag_banner'), 
                       ('account_photo', 'account_banner'), 'city', 'country', 'birth_date', 'is_verify'),
        }),
        ('Statistics', {
            'fields': (('subscribers'), 'get_local_date_joined'),
        }),
        ('Group', {
            'fields':(('is_moderator'),),
        }),
        ('Permissions', {
            'fields': ('is_admin',),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'nickname', 'email', 'account_photo', 'is_verify', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username',)
    ordering = ('created_at',)
    readonly_fields=('get_local_date_joined', 'image_tag', 'image_tag_banner', 'is_moderator')
    filter_horizontal = ()

admin.site.register(Account, AccountAdmin)

from django.contrib.auth.models import Group
admin.site.unregister(Group)