"""
Management command to encrypt existing plain IINs

Usage:
    python manage.py encrypt_existing_iins [--dry-run]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.patients.models import Patient
from apps.patients.utils.encryption import encrypt_iin, hash_iin


class Command(BaseCommand):
    help = 'Encrypt existing plain IINs for all patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be encrypted without actually encrypting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        # Find patients with plain IIN but no encrypted IIN
        patients_to_encrypt = Patient.objects.filter(
            iin__isnull=False
        ).exclude(
            iin=''
        ).filter(
            iin_enc=''
        )
        
        total_count = patients_to_encrypt.count()
        self.stdout.write(f'Found {total_count} patients with plain IINs to encrypt')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('No patients need encryption'))
            return
        
        encrypted_count = 0
        error_count = 0
        
        for patient in patients_to_encrypt:
            try:
                plain_iin = patient.iin
                
                if dry_run:
                    self.stdout.write(
                        f'Would encrypt IIN for patient #{patient.id}: {patient.full_name}'
                    )
                else:
                    # Encrypt and hash
                    patient.iin_enc = encrypt_iin(plain_iin)
                    patient.iin_hash = hash_iin(plain_iin)
                    patient.save(update_fields=['iin_enc', 'iin_hash'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Encrypted IIN for patient #{patient.id}: {patient.full_name}'
                        )
                    )
                
                encrypted_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to encrypt IIN for patient #{patient.id}: {e}'
                    )
                )
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would encrypt {encrypted_count} patients'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully encrypted {encrypted_count} patients'))
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {error_count} patients'))
        
        self.stdout.write('=' * 60)

