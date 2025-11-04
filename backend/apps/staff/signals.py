"""
Signals for HR module
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import EmployeeTask, EmployeeTaskComment
from apps.comms.tasks import send_notification


@receiver(post_save, sender=EmployeeTask)
def task_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when task is created
    """
    if created:
        # Send notification to assignee
        if instance.assignee and instance.assignee.user:
            send_notification.delay(
                user_id=instance.assignee.user.id,
                title='Новая задача',
                message=f'Вам назначена задача: {instance.title}',
                notification_type='task_assigned',
                related_object_id=instance.id
            )
        
        # Send notification to author (confirmation)
        if instance.author and instance.author.id != (instance.assignee.user.id if instance.assignee.user else None):
            send_notification.delay(
                user_id=instance.author.id,
                title='Задача создана',
                message=f'Задача "{instance.title}" создана и назначена {instance.assignee.full_name}',
                notification_type='task_created',
                related_object_id=instance.id
            )


@receiver(pre_save, sender=EmployeeTask)
def task_status_changed_notification(sender, instance, **kwargs):
    """
    Send notification when task status changes
    """
    if instance.pk:  # Only for updates
        try:
            old_instance = EmployeeTask.objects.get(pk=instance.pk)
            
            # Status changed
            if old_instance.status != instance.status:
                # Notify assignee
                if instance.assignee and instance.assignee.user:
                    status_labels = dict(EmployeeTask.STATUS_CHOICES)
                    send_notification.delay(
                        user_id=instance.assignee.user.id,
                        title='Статус задачи изменён',
                        message=f'Задача "{instance.title}" изменила статус на: {status_labels.get(instance.status)}',
                        notification_type='task_status_changed',
                        related_object_id=instance.id
                    )
                
                # Notify author
                if instance.author:
                    status_labels = dict(EmployeeTask.STATUS_CHOICES)
                    send_notification.delay(
                        user_id=instance.author.id,
                        title='Статус задачи изменён',
                        message=f'Задача "{instance.title}" ({instance.assignee.full_name}) изменила статус на: {status_labels.get(instance.status)}',
                        notification_type='task_status_changed',
                        related_object_id=instance.id
                    )
        except EmployeeTask.DoesNotExist:
            pass


@receiver(post_save, sender=EmployeeTaskComment)
def task_comment_notification(sender, instance, created, **kwargs):
    """
    Send notification when comment is added to task
    """
    if created:
        task = instance.task
        
        # Notify assignee (if comment not from assignee)
        if task.assignee and task.assignee.user and task.assignee.user.id != instance.author.id:
            send_notification.delay(
                user_id=task.assignee.user.id,
                title='Новый комментарий к задаче',
                message=f'К задаче "{task.title}" добавлен комментарий',
                notification_type='task_comment',
                related_object_id=task.id
            )
        
        # Notify author (if comment not from author)
        if task.author and task.author.id != instance.author.id:
            send_notification.delay(
                user_id=task.author.id,
                title='Новый комментарий к задаче',
                message=f'К задаче "{task.title}" добавлен комментарий',
                notification_type='task_comment',
                related_object_id=task.id
            )


def check_upcoming_deadlines():
    """
    Celery task to check for upcoming task deadlines
    Should be called periodically (e.g., every hour)
    """
    from django.db.models import Q
    
    now = timezone.now()
    
    # Check tasks with deadline in next 24 hours
    deadline_24h = now + timedelta(hours=24)
    tasks_24h = EmployeeTask.objects.filter(
        status__in=['new', 'in_progress'],
        deadline_at__lte=deadline_24h,
        deadline_at__gt=now
    ).select_related('assignee__user', 'author')
    
    for task in tasks_24h:
        if task.assignee and task.assignee.user:
            hours_left = int((task.deadline_at - now).total_seconds() / 3600)
            send_notification.delay(
                user_id=task.assignee.user.id,
                title='Приближается дедлайн',
                message=f'Задача "{task.title}" истекает через {hours_left} ч.',
                notification_type='task_deadline_soon',
                related_object_id=task.id
            )
    
    # Check overdue tasks
    overdue_tasks = EmployeeTask.objects.filter(
        status__in=['new', 'in_progress'],
        deadline_at__lt=now
    ).select_related('assignee__user', 'author')
    
    for task in overdue_tasks:
        if task.assignee and task.assignee.user:
            send_notification.delay(
                user_id=task.assignee.user.id,
                title='Задача просрочена',
                message=f'Задача "{task.title}" просрочена!',
                notification_type='task_overdue',
                related_object_id=task.id
            )

