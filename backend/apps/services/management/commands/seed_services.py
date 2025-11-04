from django.core.management.base import BaseCommand
from apps.services.models import ServiceCategory, Service
from apps.org.models import Organization


class Command(BaseCommand):
    help = 'Seed service categories and services'

    def handle(self, *args, **options):
        # Get first organization
        org = Organization.objects.first()
        if not org:
            self.stdout.write(self.style.ERROR('No organization found. Please create one first.'))
            return

        # Clear existing data
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()

        # Create categories
        reception_cat = ServiceCategory.objects.create(
            organization=org,
            name='Прием врача-стоматолога или зубного врача',
            code='CAT001',
            order=1
        )

        diagnostic_cat = ServiceCategory.objects.create(
            organization=org,
            name='Основные диагностические услуги',
            code='CAT002',
            order=2
        )

        anesthesia_cat = ServiceCategory.objects.create(
            organization=org,
            name='Анестезия',
            code='CAT003',
            order=3
        )

        restoration_cat = ServiceCategory.objects.create(
            organization=org,
            name='Восстановление зубов и целостности зубного ряда',
            code='CAT004',
            order=4
        )

        endo_cat = ServiceCategory.objects.create(
            organization=org,
            name='Лечение осложнений кариеса (эндодонтия)',
            code='CAT005',
            order=5
        )

        prevention_cat = ServiceCategory.objects.create(
            organization=org,
            name='Профилактика заболеваний полости рта',
            code='CAT006',
            order=6
        )

        aesthetic_cat = ServiceCategory.objects.create(
            organization=org,
            name='Эстетическая стоматология',
            code='CAT007',
            order=7
        )

        prosthetics_cat = ServiceCategory.objects.create(
            organization=org,
            name='Услуги по изготовлению и починке зубных протезов',
            code='CAT008',
            order=8
        )

        surgery_cat = ServiceCategory.objects.create(
            organization=org,
            name='Хирургическая стоматология',
            code='CAT009',
            order=9
        )

        pediatric_cat = ServiceCategory.objects.create(
            organization=org,
            name='Детская стоматология',
            code='CAT010',
            order=10
        )

        # Create services
        services_data = [
            {
                'category': reception_cat,
                'name': 'Прием (осмотр, консультация) врача-стоматолога-терапевта первичный',
                'code': 'B01.065.001',
                'base_price': 5000,
                'unit': 'service'
            },
            {
                'category': reception_cat,
                'name': 'Прием (осмотр, консультация) врача-стоматолога-терапевта повторный',
                'code': 'B01.065.002',
                'base_price': 3000,
                'unit': 'service'
            },
            {
                'category': reception_cat,
                'name': 'Прием (осмотр, консультация) врача-стоматолога-хирурга первичный',
                'code': 'B01.065.003',
                'base_price': 6000,
                'unit': 'service'
            },
            {
                'category': diagnostic_cat,
                'name': 'Рентгенография одного зуба',
                'code': 'A06.07.010',
                'base_price': 1500,
                'unit': 'service'
            },
            {
                'category': diagnostic_cat,
                'name': 'Ортопантомография',
                'code': 'A06.07.011',
                'base_price': 4000,
                'unit': 'service'
            },
            {
                'category': anesthesia_cat,
                'name': 'Аппликационная анестезия',
                'code': 'A11.07.001',
                'base_price': 500,
                'unit': 'service'
            },
            {
                'category': anesthesia_cat,
                'name': 'Инфильтрационная анестезия',
                'code': 'A11.07.002',
                'base_price': 1000,
                'unit': 'service'
            },
            {
                'category': anesthesia_cat,
                'name': 'Проводниковая анестезия',
                'code': 'A11.07.003',
                'base_price': 1500,
                'unit': 'service'
            },
            {
                'category': restoration_cat,
                'name': 'Наложение временной пломбы',
                'code': 'A16.07.002',
                'base_price': 2000,
                'unit': 'tooth'
            },
            {
                'category': restoration_cat,
                'name': 'Восстановление зуба пломбой I, V, VI класс по Блэку',
                'code': 'A16.07.002.001',
                'base_price': 8000,
                'unit': 'tooth'
            },
            {
                'category': restoration_cat,
                'name': 'Восстановление зуба пломбой II, III класс по Блэку',
                'code': 'A16.07.002.002',
                'base_price': 10000,
                'unit': 'tooth'
            },
            {
                'category': restoration_cat,
                'name': 'Восстановление зуба пломбой IV класс по Блэку',
                'code': 'A16.07.002.003',
                'base_price': 12000,
                'unit': 'tooth'
            },
            {
                'category': endo_cat,
                'name': 'Лечение пульпита одноканального зуба',
                'code': 'A16.07.008.001',
                'base_price': 15000,
                'unit': 'tooth'
            },
            {
                'category': endo_cat,
                'name': 'Лечение пульпита двухканального зуба',
                'code': 'A16.07.008.002',
                'base_price': 20000,
                'unit': 'tooth'
            },
            {
                'category': endo_cat,
                'name': 'Лечение пульпита трехканального зуба',
                'code': 'A16.07.008.003',
                'base_price': 25000,
                'unit': 'tooth'
            },
            {
                'category': prevention_cat,
                'name': 'Профессиональная гигиена полости рта и зубов',
                'code': 'A16.07.051',
                'base_price': 12000,
                'unit': 'service'
            },
            {
                'category': prevention_cat,
                'name': 'Снятие зубных отложений ультразвуком (1 зуб)',
                'code': 'A16.07.051.001',
                'base_price': 500,
                'unit': 'tooth'
            },
            {
                'category': aesthetic_cat,
                'name': 'Отбеливание зубов клиническое',
                'code': 'A16.07.054',
                'base_price': 80000,
                'unit': 'service',
                'is_expensive': True
            },
            {
                'category': surgery_cat,
                'name': 'Удаление зуба простое',
                'code': 'A16.07.001.001',
                'base_price': 5000,
                'unit': 'tooth'
            },
            {
                'category': surgery_cat,
                'name': 'Удаление зуба сложное',
                'code': 'A16.07.001.002',
                'base_price': 10000,
                'unit': 'tooth'
            },
        ]

        for service_data in services_data:
            Service.objects.create(
                organization=org,
                **service_data
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {ServiceCategory.objects.count()} categories '
                f'and {Service.objects.count()} services'
            )
        )
