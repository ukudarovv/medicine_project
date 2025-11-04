from django.contrib.auth.models import AbstractUser
from django.db import models
import pyotp


class User(AbstractUser):
    """
    Custom user model with additional fields
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('branch_admin', 'Branch Admin'),
        ('doctor', 'Doctor'),
        ('registrar', 'Registrar'),
        ('cashier', 'Cashier'),
        ('warehouse', 'Warehouse'),
        ('marketer', 'Marketer'),
        ('readonly', 'Read Only'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='readonly')
    phone = models.CharField(max_length=20, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True)
    
    # Multi-tenant fields
    organization = models.ForeignKey(
        'org.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def generate_totp_secret(self):
        """Generate a new TOTP secret"""
        self.totp_secret = pyotp.random_base32()
        self.save(update_fields=['totp_secret'])
        return self.totp_secret
    
    def get_totp_uri(self):
        """Get provisioning URI for QR code"""
        if not self.totp_secret:
            self.generate_totp_secret()
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email or self.username,
            issuer_name='Medicine ERP'
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)


class UserBranchAccess(models.Model):
    """
    Many-to-many relationship between users and branches with additional fields
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branch_access')
    branch = models.ForeignKey('org.Branch', on_delete=models.CASCADE, related_name='user_access')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_branch_access'
        unique_together = ['user', 'branch']
        verbose_name = 'User Branch Access'
        verbose_name_plural = 'User Branch Access'
    
    def __str__(self):
        return f"{self.user.username} - {self.branch.name}"

