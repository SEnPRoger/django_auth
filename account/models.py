from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import shutil
from pathlib import Path

class AccountManager(BaseUserManager):
    def create_user(self, username, nickname, email, birth_date=None, account_photo=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        
        if len(password) < 8:
            raise ValueError('Password must have at least 8 symbols')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nickname=nickname,
            account_photo=account_photo,
            birth_date=birth_date,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            nickname=nickname,
            birth_date=None,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

def username_photo_path(instance, filename):
        # file will be uploaded to media/accounts/account.id/username.extension,
        #                     like media/accounts/1/SEnPRoger.jpg
        extension = filename.split('.')[1]
        return 'accounts/{0}/{1}_photo.{2}'.format(instance.id, instance.nickname, extension)

def username_banner_path(instance, filename):
        # file will be uploaded to media/accounts/account.id/username.extension,
        #                     like media/accounts/1/SEnPRoger.jpg
        extension = filename.split('.')[1]
        return 'accounts/{0}/{1}_banner.{2}'.format(instance.id, instance.nickname, extension)

# Create your models here.
class Account(AbstractBaseUser):
    username            = models.CharField(verbose_name='👤 Username', max_length=32, blank=False)
    nickname            = models.CharField(verbose_name='👤 Nickname', max_length=32, blank=False, unique=True, help_text='Nickname should be unique')
    email               = models.EmailField(verbose_name='📬 Email', max_length=32, blank=False, unique=True, help_text='Email should be unique')

    birth_date          = models.DateField(verbose_name='🥳 Birth date', blank=True, null=True)
    
    account_photo       = models.ImageField(verbose_name='🖼 Change account photo', upload_to=username_photo_path, blank=True, null=True)
    account_banner      = models.ImageField(verbose_name='Change account banner', upload_to=username_banner_path, blank=True, null=True)
    
    city                = models.CharField(verbose_name = '🏡 City', max_length=64, blank=True, null=True)
    country             = models.CharField(verbose_name = '🏙 Country', max_length=64, blank=True, null=True)
    biography           = models.TextField(verbose_name = '🏙 Biography', max_length=256, blank=True, null=True)
    changed_nickname    = models.DateTimeField(verbose_name='Changed nickname date', default=timezone.now, help_text='Nickname can be changed every 24 hours')

    #related_posts       = models.ManyToManyField('post.Post', blank=True, related_name='posts_set')
    blocked_accounts    = models.ManyToManyField("self", verbose_name = 'Blocked accounts', blank=True, null=True, related_name='blocked_accounts_set', 
                                                    symmetrical=False)
    subscribers         = models.ManyToManyField("self", blank=True, null=True, related_name='subscribers_set', 
                                                    symmetrical=False)

    is_verify           = models.BooleanField(verbose_name = 'Is verified account ☑️', default=False)
    is_blocked          = models.BooleanField(verbose_name = '⛔️ Is account blocked', default=False)
    is_moderator        = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    is_admin            = models.BooleanField(default=False)

    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['email', 'username']

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def image_tag(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="150" height="150" style="border-radius: 50%%"; />' % (self.account_photo.url))
    image_tag.short_description = '🖼 Account photo'
    image_tag.allow_tags = True

    def get_image(self):
        if self.account_photo:
            return self.account_photo.url
        
    def image_tag_banner(self):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="791" height="150" style="border-radius: 20px"; />' % (self.account_banner.url))
    image_tag_banner.short_description = '🖼 Account banner'
    image_tag_banner.allow_tags = True

    def get_image_banner(self):
        if self.account_banner:
            return self.account_banner.url

    def get_subcribers_count(self):
        return self.subscribers.count()
    
    def get_posts_count(self):
        return self.related_posts.count()

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_image = self.account_photo
            self.account_photo = None
            super(Account, self).save(*args, **kwargs)
            self.account_photo = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(Account, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        try:
            if self.account_photo != None:
                photo_path = Path(self.account_photo.path)
                photo_folder = photo_path.parent
                shutil.rmtree(photo_folder)
        except:
            pass
        super().delete()

class VerificationCode(models.Model):
    email = models.CharField(max_length=32, blank=False, null=True)
    code = models.CharField(max_length=32, blank=False, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

class VerifiedAccount(models.Model):
    account = models.ForeignKey('account.Account', blank=False, null=False, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    changed_date = models.DateTimeField(default=timezone.now)
    social_link = models.TextField(blank=True, null=True)
    provided_by = models.ForeignKey('account.Account', related_name='provided_by', blank=True, null=True, on_delete=models.CASCADE)