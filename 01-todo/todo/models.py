from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Todo(models.Model):
    """
    Model representing a TODO item.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200, help_text="Title of the TODO item")
    description = models.TextField(blank=True, help_text="Detailed description of the TODO")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the TODO"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the TODO"
    )
    due_date = models.DateTimeField(null=True, blank=True, help_text="Due date for the TODO")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the TODO was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the TODO was last updated")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="When the TODO was completed")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='todos',
        help_text="User who owns this TODO"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'TODO'
        verbose_name_plural = 'TODOs'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def mark_as_completed(self):
        """Mark the TODO as completed and set the completion timestamp."""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def is_overdue(self):
        """Check if the TODO is overdue."""
        from django.utils import timezone
        if self.due_date and self.status != 'completed':
            return timezone.now() > self.due_date
        return False
