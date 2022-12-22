from django.db import models
import binascii
from django.contrib.auth.models import User
import uuid
from django.utils.translation import gettext_lazy as _
import os


class Token(models.Model):
    """
    The default authorization token model.
    """

    key: str = models.CharField(_("Key"), max_length=40, primary_key=True)
    user_id: uuid.UUID
    user: User = models.OneToOneField(
        User,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    created_at = models.DateTimeField(_("Created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    def __str__(self):
        return f"Token of {self.user}"

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()
