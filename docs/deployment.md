# Инструкция по деплою Medicine ERP

## Production Deployment

### Требования
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7
- MinIO (опционально, можно использовать S3)
- Домен с SSL сертификатом

### Шаги деплоя

#### 1. Подготовка сервера

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Клонирование проекта

```bash
git clone https://github.com/ukudarovv/medicine_project.git
cd medicine_project
```

#### 3. Настройка окружения

```bash
# Создать .env файл
cp env.example .env

# Отредактировать .env для production
nano .env
```

Обязательные параметры для production:
```env
DJANGO_SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

POSTGRES_DB=medicine_erp_prod
POSTGRES_USER=medicine_user
POSTGRES_PASSWORD=<strong-password>

SMS_PROVIDER=iqsms  # или другой провайдер
SMS_API_KEY=<your-api-key>
```

#### 4. Настройка SSL (Nginx + Certbot)

```bash
# Установка Nginx
sudo apt install nginx certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 5. Запуск проекта

```bash
# Сборка образов
docker-compose -f docker-compose.prod.yml build

# Запуск контейнеров
docker-compose -f docker-compose.prod.yml up -d

# Миграции
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Создание суперпользователя
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Загрузка начальных данных
docker-compose -f docker-compose.prod.yml exec backend python manage.py seed_initial_data
```

#### 6. Настройка резервного копирования

```bash
# Создать скрипт backup.sh
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T db pg_dump -U postgres medicine_erp_prod > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
EOF

chmod +x backup.sh

# Добавить в crontab (каждые 6 часов)
(crontab -l 2>/dev/null; echo "0 */6 * * * /path/to/backup.sh") | crontab -
```

#### 7. Мониторинг и логи

```bash
# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.prod.yml logs -f backend

# Статус сервисов
docker-compose -f docker-compose.prod.yml ps
```

## Обновление production

```bash
# Получить последние изменения
git pull origin main

# Остановить сервисы
docker-compose -f docker-compose.prod.yml down

# Пересобрать образы
docker-compose -f docker-compose.prod.yml build

# Запустить
docker-compose -f docker-compose.prod.yml up -d

# Миграции
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Сбор статики
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Производительность

### Оптимизация PostgreSQL

```sql
-- Настроить параметры в postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB
```

### Оптимизация Redis

```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

## Безопасность

1. Использовать сильные пароли для БД
2. Включить firewall (UFW)
3. Регулярно обновлять зависимости
4. Настроить fail2ban
5. Использовать HTTPS
6. Включить 2FA для всех администраторов

## Мониторинг

Рекомендуется настроить:
- Prometheus + Grafana для метрик
- Sentry для отслеживания ошибок
- ELK stack для логов
- Uptime monitoring (UptimeRobot, Pingdom)

