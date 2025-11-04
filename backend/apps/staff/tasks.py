"""
Celery tasks for staff/HR module
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def check_task_deadlines():
    """
    Check for upcoming and overdue task deadlines
    Runs periodically (configure in celery beat)
    """
    from .models import EmployeeTask
    from apps.comms.tasks import send_notification
    
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
    
    return {
        'upcoming_24h': tasks_24h.count(),
        'overdue': overdue_tasks.count()
    }


@shared_task
def calculate_employee_salary(employee_id, period_from, period_to):
    """
    Calculate employee salary for given period
    """
    from .models import Employee, EmployeeSalarySchema
    from apps.visits.models import Visit, VisitService
    from apps.billing.models import Payment
    from django.db.models import Q, Sum
    
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return {'error': 'Employee not found'}
    
    # Get active salary schema for the period
    salary_schema = EmployeeSalarySchema.objects.filter(
        employee=employee,
        is_active=True,
        starts_at__lte=period_to
    ).filter(
        Q(ends_at__gte=period_from) | Q(ends_at__isnull=True)
    ).select_related('salary_template').first()
    
    if not salary_schema:
        return {'error': 'No active salary schema'}
    
    template = salary_schema.salary_template
    total_salary = 0
    breakdown = {}
    
    # 1. Commission from own sales (completed and paid visits)
    if template.pct_of_own_sales and template.pct_value:
        own_services = VisitService.objects.filter(
            visit__appointment__employee=employee,
            visit__status='completed',
            visit__created_at__range=[period_from, period_to]
        ).aggregate(total=Sum('price'))
        
        own_sales_amount = own_services.get('total') or 0
        commission = (own_sales_amount * template.pct_value) / 100
        
        total_salary += commission
        breakdown['own_sales_commission'] = {
            'base_amount': float(own_sales_amount),
            'percent': float(template.pct_value),
            'commission': float(commission)
        }
    
    # 2. Fixed salary
    if template.fixed_salary_enabled and template.fixed_amount:
        total_salary += template.fixed_amount
        breakdown['fixed_salary'] = float(template.fixed_amount)
    
    # 3. Minimum rate check
    if template.min_rate_enabled and template.min_rate_amount:
        if total_salary < template.min_rate_amount:
            breakdown['minimum_rate_applied'] = {
                'calculated': float(total_salary),
                'minimum': float(template.min_rate_amount)
            }
            total_salary = template.min_rate_amount
    
    return {
        'employee_id': employee_id,
        'employee_name': employee.full_name,
        'period_from': str(period_from),
        'period_to': str(period_to),
        'salary_template': template.name,
        'total_salary': float(total_salary),
        'currency': template.currency,
        'breakdown': breakdown
    }

