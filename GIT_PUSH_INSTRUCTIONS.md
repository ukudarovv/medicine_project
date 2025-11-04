# Git Push Instructions - KZ Adaptation

## Подготовка к коммиту

Текущее состояние: **Sprint 1 полностью завершен, Sprint 2 модели созданы**

## Команды для push в репозиторий

```bash
# 1. Проверить текущий статус
git status

# 2. Добавить все измененные файлы
git add .

# 3. Создать коммит с описанием изменений
git commit -m "feat: KZ market adaptation - Sprint 1-2 backend implementation

Sprint 1 (Completed):
- Add IIN (Individual Identification Number) validation with Luhn algorithm
- Add Patient KZ fields: iin_verified, kato_address, osms_status, osms_category
- Add ConsentHistory model for GDPR/KZ compliance audit trail
- Add KATO (Kazakhstan Administrative Territorial) reference data
- Add KZ-specific settings: currency KZT, timezone Asia/Almaty
- Add API endpoints: verify-iin, save-consent, consent-history
- Add frontend: IIN verification button, OSMS fields in PatientModal
- Add migration: 0005_add_kz_identity_fields

Sprint 2 (Models Created):
- Extend Visit model: diary_structured, templates_used fields
- Add VisitFile model for file attachments (x-rays, photos, documents)
- Add Waitlist model for patient waitlist management
- Add PatientContact model for detailed contact history tracking

Files Added/Modified:
- backend/apps/patients/models.py (Patient + ConsentHistory)
- backend/apps/patients/validators.py (IIN validation)
- backend/apps/patients/kato_utils.py (KATO helper utilities)
- backend/apps/patients/serializers.py (new serializers)
- backend/apps/patients/views.py (new API endpoints)
- backend/apps/patients/admin.py (ConsentHistory admin)
- backend/apps/patients/urls.py (routing updates)
- backend/apps/patients/fixtures/kato.json (KATO reference)
- backend/apps/patients/migrations/0005_add_kz_identity_fields.py
- backend/apps/visits/models.py (Visit extensions + VisitFile)
- backend/apps/calendar/models.py (Waitlist)
- backend/apps/comms/models.py (PatientContact)
- backend/config/settings/base.py (KZ settings)
- frontend/src/components/PatientModal.vue (IIN + OSMS fields)
- CHANGELOG.md (v1.2.0 section)
- docs/kz-features.md (new documentation)
- KZ_ADAPTATION_SUMMARY.md (implementation summary)
- GIT_PUSH_INSTRUCTIONS.md (this file)

Breaking Changes: None
Migrations Required: Yes (patients, visits, calendar, comms)

See CHANGELOG.md and KZ_ADAPTATION_SUMMARY.md for details."

# 4. Push в репозиторий
git push origin master
```

## Альтернативный вариант (feature branch)

Если хотите сначала создать feature branch:

```bash
# 1. Создать и переключиться на ветку feature
git checkout -b feature/kz-adaptation

# 2. Добавить все файлы
git add .

# 3. Коммит (тот же текст, что и выше)
git commit -m "feat: KZ market adaptation - Sprint 1-2 backend implementation
..."

# 4. Push в feature branch
git push origin feature/kz-adaptation

# 5. Создать Pull Request на GitHub
# Перейти на https://github.com/ukudarovv/medicine_project
# и создать Pull Request из feature/kz-adaptation в master
```

## Что было изменено

### Новые файлы (19)
```
backend/apps/patients/validators.py
backend/apps/patients/kato_utils.py
backend/apps/patients/fixtures/kato.json
backend/apps/patients/migrations/0005_add_kz_identity_fields.py
docs/kz-features.md
KZ_ADAPTATION_SUMMARY.md
GIT_PUSH_INSTRUCTIONS.md
```

### Изменены файлы (12)
```
backend/apps/patients/models.py
backend/apps/patients/serializers.py
backend/apps/patients/views.py
backend/apps/patients/urls.py
backend/apps/patients/admin.py
backend/apps/visits/models.py
backend/apps/calendar/models.py
backend/apps/comms/models.py
backend/config/settings/base.py
frontend/src/components/PatientModal.vue
CHANGELOG.md
```

## После push

1. **Проверить на GitHub:**
   - Перейти: https://github.com/ukudarovv/medicine_project
   - Убедиться, что все файлы загружены
   - Проверить CHANGELOG.md

2. **Создать Release (опционально):**
   - На GitHub: Releases → Draft a new release
   - Tag: v1.2.0-beta
   - Title: "KZ Market Adaptation - Sprint 1-2"
   - Description: скопировать из CHANGELOG.md

3. **Следующие шаги:**
   - Применить миграции на dev/staging
   - Протестировать IIN validation
   - Продолжить Sprint 2 (API, print templates, frontend)

## Важно

⚠️ **Перед push убедитесь:**
- [ ] Нет конфликтов с master
- [ ] Все файлы сохранены
- [ ] CHANGELOG.md обновлен
- [ ] Миграция создана (но не применена на продакшене!)

⚠️ **Не забудьте после деплоя:**
```bash
python manage.py migrate
python manage.py loaddata kato
```

## Troubleshooting

### Если возникла ошибка при push:

```bash
# Проверить удаленный репозиторий
git remote -v

# Должно быть:
# origin  https://github.com/ukudarovv/medicine_project.git (fetch)
# origin  https://github.com/ukudarovv/medicine_project.git (push)

# Если нет, добавить:
git remote add origin https://github.com/ukudarovv/medicine_project.git

# Если нужно обновить из удаленного репозитория:
git pull origin master --rebase
```

### Если есть конфликты:

```bash
# Разрешить конфликты вручную в файлах
# После разрешения:
git add .
git rebase --continue
git push origin master
```

## Контакты

По вопросам push:
- GitHub: https://github.com/ukudarovv/medicine_project
- Issues: https://github.com/ukudarovv/medicine_project/issues

---

**Created:** November 4, 2025  
**Repository:** https://github.com/ukudarovv/medicine_project

