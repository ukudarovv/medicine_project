from django.core.management.base import BaseCommand
from apps.warehouse.models import Warehouse
from apps.org.models import Branch


class Command(BaseCommand):
    help = 'Создает дефолтный склад для каждого филиала, если у него нет склада'

    def handle(self, *args, **options):
        branches = Branch.objects.all()
        
        if not branches.exists():
            self.stdout.write(
                self.style.WARNING('Нет филиалов в системе. Создайте филиал перед созданием склада.')
            )
            return
        
        created_count = 0
        for branch in branches:
            # Проверяем, есть ли у филиала хотя бы один склад
            if not branch.warehouses.exists():
                warehouse = Warehouse.objects.create(
                    branch=branch,
                    name=f'Основной склад - {branch.name}',
                    is_active=True
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан склад "{warehouse.name}" для филиала "{branch.name}"'
                    )
                )
        
        if created_count == 0:
            self.stdout.write(
                self.style.SUCCESS('У всех филиалов уже есть склады.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Всего создано складов: {created_count}')
            )



