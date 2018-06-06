import os
import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.fields import ThumbnailerImageField

from nc_core.utils import memcached_property

__all__ = [
    'User'
]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


def upload_logo(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = '{name}.{ext}'.format(name=str(uuid.uuid4()), ext=ext)
    return os.path.join('accounts', 'photo', new_filename)


class User(AbstractBaseUser, PermissionsMixin):
    CACHE_PREFIX = "User#"

    company = models.ForeignKey(
        'nc_core.Company',
        verbose_name=_("company"),
        related_name='users',
        default=None,
        blank=True,
        null=True
    )

    email = models.EmailField(
        verbose_name=_('email address'),
        blank=True,
        unique=True
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        auto_now_add=True
    )

    module_permissions = models.ManyToManyField(
        'nc_modules.Module',
        verbose_name=_("Module permissions"),
        related_name="users",
        blank=True
    )

    first_name = models.CharField(
        _("first name"),
        max_length=512
    )

    last_name = models.CharField(
        _("last name"),
        max_length=512
    )

    middle_name = models.CharField(
        _("middle name"),
        max_length=512,
        blank=True
    )

    notes = models.CharField(
        _("extra info"),
        max_length=1024,
        null=False,
        blank=True,
        default=''
    )

    birthday = models.DateField(
        _("birthday"),
        null=True,
        blank=True
    )

    position = models.CharField(
        _("position"),
        max_length=255,
        blank=True,
        help_text="Manager, etc"
    )

    legal_person = models.BooleanField(
        _("legal person"),
        default=False
    )

    logo = ThumbnailerImageField(
        _("avatar"),
        default=None,
        upload_to=upload_logo,
        blank=True,
        null=True
    )

    data_items = GenericRelation('nc_core.DataItem')

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def short_name(self):
        middle_name = (self.middle_name[0].upper() + ".") if self.middle_name else ""
        first_name = (self.first_name[0].upper() + ".") if self.first_name else ""
        last_name = self.last_name.capitalize()
        return " ".join(filter(None, (last_name, first_name, middle_name))) or getattr(self, self.USERNAME_FIELD)

    @property
    def full_name(self):
        return " ".join(map(str.capitalize, filter(None, (self.last_name, self.first_name, self.middle_name)))) \
               or getattr(self, self.USERNAME_FIELD)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.full_name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.short_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @memcached_property(
        key=lambda self: self.CACHE_PREFIX + str(self.id),
        timeout=settings.CACHES_DURATIONS.get("DEFAULT_PROPERTY", 60)
    )
    def is_company_owner(self):
        return self.company_id and self.company.owner_id == self.id

    class Meta:
        verbose_name = _("auth user")
        verbose_name_plural = _("auth users")
