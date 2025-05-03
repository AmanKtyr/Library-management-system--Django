from django.db import models
from django.conf import settings
from apps.books.models import BookCopy, Book
from apps.libraries.models import Library
from django.utils import timezone
import uuid
from datetime import timedelta

class Transaction(models.Model):
    """Model representing a transaction (borrowing or returning a book)."""
    TRANSACTION_TYPE_CHOICES = (
        ('BORROW', 'Borrow'),
        ('RETURN', 'Return'),
        ('RESERVE', 'Reserve'),
        ('CANCEL_RESERVATION', 'Cancel Reservation'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    )

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='transactions')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    return_date = models.DateTimeField(blank=True, null=True)

    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)
    fine_payment_date = models.DateTimeField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_transactions',
        limit_choices_to={'user_type__in': ['SUPER_ADMIN', 'LIBRARY_ADMIN', 'STAFF']}
    )

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_id} - {self.book_copy.book.title} - {self.user.email}"

    def is_overdue(self):
        if self.transaction_type == 'BORROW' and self.status == 'COMPLETED' and self.due_date:
            return timezone.now() > self.due_date
        return False

    def calculate_fine(self, fine_rate_per_day=1.00):
        """Calculate fine for overdue books."""
        if self.is_overdue():
            days_overdue = (timezone.now() - self.due_date).days
            return days_overdue * fine_rate_per_day
        return 0.00

class MembershipPlan(models.Model):
    """Model representing a membership plan for library members."""
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_days = models.PositiveIntegerField()
    max_books_allowed = models.PositiveIntegerField()
    max_borrowing_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    """Model representing a user's membership in a specific library."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, related_name='memberships')

    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    membership_number = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'library')

    def __str__(self):
        return f"{self.user.email} - {self.library.name} - {self.plan.name}"

    def is_expired(self):
        return timezone.now().date() > self.end_date

    def save(self, *args, **kwargs):
        if not self.membership_number:
            # Generate a unique membership number
            self.membership_number = f"MEM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Reservation(models.Model):
    """Model representing a book reservation."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='reservations')

    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_reservations'
    )
    processed_date = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reservation_date']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.book.title}"

    def save(self, *args, **kwargs):
        # Set expiry date if not already set (default to 3 days from reservation)
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expiry_date

    def mark_as_expired(self):
        if self.status in ['PENDING', 'CONFIRMED'] and self.is_expired():
            self.status = 'EXPIRED'
            self.save()

    def confirm(self, staff_user=None):
        if self.status == 'PENDING':
            self.status = 'CONFIRMED'
            if staff_user:
                self.processed_by = staff_user
                self.processed_date = timezone.now()
            self.save()

    def cancel(self, staff_user=None):
        if self.status in ['PENDING', 'CONFIRMED']:
            self.status = 'CANCELLED'
            if staff_user:
                self.processed_by = staff_user
                self.processed_date = timezone.now()
            self.save()

    def complete(self, staff_user=None):
        if self.status == 'CONFIRMED':
            self.status = 'COMPLETED'
            if staff_user:
                self.processed_by = staff_user
                self.processed_date = timezone.now()
            self.save()


class MembershipRequest(models.Model):
    """Model representing a pending membership request for a library."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_requests')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='membership_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_membership_requests',
        limit_choices_to={'user_type__in': ['SUPER_ADMIN', 'LIBRARY_ADMIN', 'STAFF']}
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'library')
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.user.email} - {self.library.name} - {self.status}"


class MemberAttendance(models.Model):
    """Model representing a member's attendance at the library."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='member_attendances')
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    purpose = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_attendances',
        limit_choices_to={'user_type__in': ['SUPER_ADMIN', 'LIBRARY_ADMIN', 'STAFF']}
    )

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.user.email} - {self.check_in_time.strftime('%Y-%m-%d %H:%M')}"

    def duration(self):
        """Calculate the duration of the visit in minutes."""
        if self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            return int(delta.total_seconds() / 60)
        return None


class LibraryPlan(models.Model):
    """Model representing a library's operational plan or program."""
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=100, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    success_metrics = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_library_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.library.name} - {self.name}"

    def is_expired(self):
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False
