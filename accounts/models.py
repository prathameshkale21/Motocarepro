from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role so the same login system serves
    customers, mechanics, and admins."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        MECHANIC = "mechanic", "Mechanic"
        ADMIN = "admin", "Admin"

    class SecurityQuestion(models.TextChoices):
        PET = "pet", "What was the name of your first pet?"
        SCHOOL = "school", "What was the name of your first school?"
        CITY = "city", "In which city were you born?"
        MOTHER = "mother", "What is your mother's maiden name?"
        BIKE = "bike", "What was the make of your first bike?"
        NICKNAME = "nickname", "What was your childhood nickname?"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    reward_points = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=12, blank=True, unique=True, null=True)

    security_question = models.CharField(
        max_length=20, choices=SecurityQuestion.choices, default=SecurityQuestion.PET
    )
    security_answer = models.CharField(
        max_length=128,
        blank=True,
        help_text="Stored as a one-way hash, same as a password.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_mechanic(self):
        return self.role == self.Role.MECHANIC

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def set_security_answer(self, raw_answer):
        """Hash and store the security answer, case/whitespace-insensitive."""
        normalized = raw_answer.strip().lower()
        self.security_answer = make_password(normalized)

    def check_security_answer(self, raw_answer):
        if not self.security_answer:
            return False
        normalized = raw_answer.strip().lower()
        try:
            return check_password(normalized, self.security_answer)
        except (ValueError, TypeError):
            return False

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
