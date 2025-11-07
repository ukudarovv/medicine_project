from django.db import models
from django.core.exceptions import ValidationError
from apps.org.models import Branch, Room
from apps.staff.models import Employee
from apps.patients.models import Patient


class Availability(models.Model):
    """
    Availability/Schedule template for employees
    """
    WEEKDAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='availabilities'
    )
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'availabilities'
        verbose_name = 'Availability'
        verbose_name_plural = 'Availabilities'
        ordering = ['weekday', 'time_from']
        unique_together = ['employee', 'weekday', 'time_from']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_weekday_display()} {self.time_from}-{self.time_to}"
    
    def clean(self):
        if self.time_from >= self.time_to:
            raise ValidationError('Time from must be before time to')


class Appointment(models.Model):
    """
    Appointment/Booking model
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('booked', 'Забронировано'),
        ('confirmed', 'Подтверждено'),
        ('in_progress', 'В процессе'),
        ('done', 'Выполнено'),
        ('no_show', 'Не пришёл'),
        ('canceled', 'Отменено'),
    ]
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='appointments',
        help_text='Нельзя удалить пациента, у которого есть записи на прием'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    
    # DateTime
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    
    # Status and flags
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked', db_index=True)
    is_primary = models.BooleanField(default=False, help_text='Первичный приём')
    is_urgent = models.BooleanField(default=False, help_text='Срочный')
    
    # Notes
    note = models.TextField(blank=True, help_text='Примечание к записи')
    cancellation_reason = models.TextField(blank=True)
    
    # Meta
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['branch', 'start_datetime']),
            models.Index(fields=['employee', 'start_datetime']),
            models.Index(fields=['patient', 'start_datetime']),
            models.Index(fields=['status', 'start_datetime']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.employee.full_name} ({self.start_datetime})"
    
    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError('Start time must be before end time')
        
        # Check for overlapping appointments for the same employee
        overlapping = Appointment.objects.filter(
            employee=self.employee,
            start_datetime__lt=self.end_datetime,
            end_datetime__gt=self.start_datetime
        ).exclude(
            id=self.id
        ).exclude(
            status__in=['canceled', 'no_show']
        )
        
        if overlapping.exists():
            raise ValidationError('Employee has overlapping appointments')
        
        # Check for overlapping appointments for the same room (if room is set)
        if self.room:
            overlapping_room = Appointment.objects.filter(
                room=self.room,
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime
            ).exclude(
                id=self.id
            ).exclude(
                status__in=['canceled', 'no_show']
            )
            
            if overlapping_room.exists():
                raise ValidationError('Room is already booked for this time')
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes"""
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() / 60)
    
    @property
    def color(self):
        """Get color based on status or employee"""
        status_colors = {
            'draft': '#9E9E9E',
            'booked': '#2196F3',
            'confirmed': '#00C2A8',
            'in_progress': '#FF9800',
            'done': '#4CAF50',
            'no_show': '#F44336',
            'canceled': '#FFCDD2',
        }
        return status_colors.get(self.status, self.employee.color)


class AppointmentResource(models.Model):
    """
    Resources allocated to an appointment
    """
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='allocated_resources'
    )
    resource = models.ForeignKey(
        'org.Resource',
        on_delete=models.CASCADE,
        related_name='appointment_allocations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'appointment_resources'
        unique_together = ['appointment', 'resource']
        verbose_name = 'Appointment Resource'
        verbose_name_plural = 'Appointment Resources'
    
    def __str__(self):
        return f"{self.appointment} - {self.resource.name}"


class Waitlist(models.Model):
    """
    Patient waitlist for appointments (Sprint 2)
    """
    TIME_WINDOW_CHOICES = [
        ('morning', 'Утро (9:00-12:00)'),
        ('afternoon', 'День (12:00-17:00)'),
        ('evening', 'Вечер (17:00-20:00)'),
        ('any', 'Любое время'),
    ]
    
    STATUS_CHOICES = [
        ('waiting', 'Ожидает'),
        ('contacted', 'Связались'),
        ('scheduled', 'Записан'),
        ('cancelled', 'Отменен'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='waitlist_entries'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Желаемая услуга'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Желаемый врач'
    )
    
    # Date preferences
    preferred_date = models.DateField(null=True, blank=True, help_text='Конкретная дата')
    preferred_period_start = models.DateField(null=True, blank=True, help_text='Начало периода')
    preferred_period_end = models.DateField(null=True, blank=True, help_text='Конец периода')
    time_window = models.CharField(max_length=20, choices=TIME_WINDOW_CHOICES, default='any')
    
    # Details
    priority = models.IntegerField(default=0, help_text='Приоритет (0=обычный, выше=важнее)')
    comment = models.TextField(blank=True, help_text='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    
    # Contact tracking
    contacted_at = models.DateTimeField(null=True, blank=True)
    contacted_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waitlist_contacts'
    )
    contact_result = models.TextField(blank=True, help_text='Результат связи')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'waitlist'
        verbose_name = 'Waitlist Entry'
        verbose_name_plural = 'Waitlist Entries'
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['status', 'preferred_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_status_display()}"


class Break(models.Model):
    """
    Employee breaks in schedule (lunch, meeting, etc.)
    """
    TYPE_CHOICES = [
        ('lunch', 'Обед'),
        ('break', 'Перерыв'),
        ('meeting', 'Совещание'),
        ('other', 'Другое'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='breaks'
    )
    break_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='break')
    
    # Date and time
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Details
    note = models.TextField(blank=True, help_text='Примечание к перерыву')
    
    # Recurring break
    is_recurring = models.BooleanField(default=False, help_text='Повторяется каждый день')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'breaks'
        verbose_name = 'Break'
        verbose_name_plural = 'Breaks'
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'start_time']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_break_type_display()} ({self.date} {self.start_time}-{self.end_time})"
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Start time must be before end time')
        
        # Check for overlapping breaks for the same employee on the same date
        overlapping = Break.objects.filter(
            employee=self.employee,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        
        if overlapping.exists():
            raise ValidationError('Employee has overlapping breaks on this date')