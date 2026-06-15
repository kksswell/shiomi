# Vania_Sait / SHIOMI CS2

Обновлённый сайт игрового проекта **SHIOMI / BlueSen Shiomi** в сеттинге CS2: тёмный премиальный интерфейс, Steam-авторизация, серверы, магазин доната, правила, бонусное колесо и профиль игрока.

## Стек

Frontend:
- Vue 3
- Vite
- TypeScript
- SCSS
- CSS variables
- Tailwind CSS

Backend:
- Django 5
- Django REST Framework
- PostgreSQL
- Django Admin
- Django media на VPS
- подготовка к S3-compatible storage через `django-storages`

Инфраструктура:
- Docker Compose
- Nginx
- Gunicorn
- Ubuntu VPS-ready конфиги
- Certbot / Let’s Encrypt-ready структура
- Cloudflare DNS-ready инструкция
- Sentry-ready настройки
- Uptime Kuma
- pg_dump backup
- cron backup
- media archive scripts

## Новая структура

```text
Vania_Sait/
├── backend/                  # Django + DRF
│   ├── apps/portal/          # Steam, серверы, магазин, правила, бонусы, заявки
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/         # Steam OpenID и статус CS2-сервера
│   ├── config/               # Django settings / urls / wsgi / asgi
│   └── requirements.txt
├── frontend/                 # Vue 3 + Vite + TS
│   ├── src/
│   │   ├── api/              # API-клиент
│   │   ├── components/       # Header, Server, Shop, Bonus, Rules, Modal
│   │   ├── views/            # Home/Profile
│   │   ├── styles/           # SCSS, variables, responsive UI
│   │   └── types/            # TypeScript-типы API
│   └── public/               # logo/favicons/manifest
├── deploy/                   # nginx, certbot, backup scripts, cron
├── docs/                     # отчёты и инструкции
├── docker-compose.yml
├── docker-compose.dev.yml
└── docker-compose.prod.yml
```

## Локальный запуск

```bash
cd ~/Desktop/Vania_Sait
cp .env.example .env
docker compose up -d --build
```

После запуска:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

Открыть:

```text
http://localhost
http://localhost/admin/
http://localhost/api/health/
http://localhost/api/health/ready/
```

## DEV-режим с Vite hot reload

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

## Steam авторизация

Production-сценарий использует Steam OpenID:

```env
STEAM_API_KEY=your_steam_web_api_key
STEAM_OPENID_REALM=https://example.com/
STEAM_RETURN_URL=https://example.com/api/auth/steam/return/
FRONTEND_URL=https://example.com
BACKEND_URL=https://example.com
```

Для локального тестирования можно оставить:

```env
STEAM_DEV_LOGIN_ENABLED=true
```

Тогда основная кнопка входа на localhost автоматически использует безопасный backend DEV-вход и не открывает `steamcommunity.com/openid/login`. На VPS обязательно поставить:

```env
STEAM_DEV_LOGIN_ENABLED=false
```

Если в браузере при переходе на `steamcommunity.com/openid/login` появляется `Access Denied` или `ERR_CONNECTION_RESET`, это обычно связано с localhost/VPN/провайдером/политикой Steam/Akamai. Для разработки включён DEV-вход, а реальный Steam OpenID проверяется уже на домене с HTTPS.

## Основные API

```text
GET  /api/bootstrap/
GET  /api/server/status/
GET  /api/servers/
GET  /api/user/profile/
GET  /api/auth/steam/
GET  /api/auth/steam/return/
GET  /api/auth/steam/dev/
POST /api/auth/logout/
GET  /api/shop/products/
POST /api/shop/purchase/
GET  /api/rules/
GET  /api/bonus/rewards/
POST /api/bonus/spin/
```

## Что управляется через Django Admin

- Steam-пользователи, роли, кредиты, статистика, сроки VIP/Admin.
- Игровые серверы: host, port, режим, описание, mock/auto-статус, фон, сортировка.
- Донат-товары: название, описание, цена, тип, срок действия, бейдж, активность.
- Правила: заголовок, описание, пункты, сортировка.
- Награды бонусного колеса: шанс, редкость, кредиты, VIP/Admin выдача.
- Заявки на покупки.

При старте контейнера backend выполняет `python manage.py seed_defaults`, поэтому безопасные дефолтные серверы, товары, правила и награды создаются автоматически, если база пустая.

## Подготовка к Ubuntu VPS

1. Установить Docker и Docker Compose plugin.
2. Скопировать проект на сервер.
3. Создать `.env` из `.env.example`.
4. Заменить домен `example.com` в `.env` и `deploy/nginx/default.prod.conf`.
5. Указать сильные пароли и секреты.
6. Выключить debug и DEV-вход:

```env
DJANGO_DEBUG=false
STEAM_DEV_LOGIN_ENABLED=false
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_SSL_REDIRECT=true
SECURE_HSTS_SECONDS=31536000
```

7. Запустить production compose:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Certbot / Let’s Encrypt

На VPS после настройки DNS и Nginx:

```bash
sudo certbot certonly --webroot \
  -w ./deploy/certbot/www \
  -d example.com \
  -d www.example.com
```

Затем подключить SSL server block в `deploy/nginx/default.prod.conf` и перезапустить Nginx-контейнер.

## Cloudflare DNS

- `A` record: `example.com` → IP VPS
- `A` record: `www` → IP VPS
- SSL/TLS mode: Full или Full Strict после установки сертификата.
- Proxy включать после проверки прямого HTTPS.

## Backups

PostgreSQL:

```bash
./deploy/scripts/backup_postgres.sh
```

Media:

```bash
./deploy/scripts/archive_media.sh
```

Полный backup:

```bash
./deploy/scripts/backup_all.sh
```

Пример cron лежит в:

```text
deploy/cron.example
```

## Sentry

Для включения указать:

```env
SENTRY_DSN=https://...
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

## Uptime Kuma

```bash
docker compose --profile monitoring up -d uptime-kuma
```

Панель:

```text
http://localhost:3001
```

## Проверки текущей сборки

В этой итерации выполнены:

```bash
python -m py_compile $(find backend -name '*.py')
python manage.py check
python manage.py makemigrations --check --dry-run
npm run build
```

`makemigrations` может показывать warning о недоступной БД, если локально не поднят контейнер PostgreSQL. Структурно миграции актуальны.

## Ограничения

В архивах нет дампа старой базы данных и нет реального Steam Web API Key. Поэтому реальные пользователи, VIP-статусы, покупки и статистика не переносились. Система готова к заполнению через Django Admin и к подключению реального CS2/Steam окружения.


## Если Docker падает на npm install

См. `docs/docker-build-troubleshooting.md`. Frontend Dockerfile использует `package.json` без lock-файла, чтобы сборка не зависела от недоступных registry URL из чужого окружения.


## Исправления последней итерации

- Кнопка `Войти через Steam` на localhost больше не ведёт напрямую на Steam OpenID и не вызывает `Access Denied`; при `STEAM_DEV_LOGIN_ENABLED=true` используется `/api/auth/steam/dev/`.
- Backend дополнительно защищает `/api/auth/steam/`: если запрос пришёл с `localhost` и DEV-вход включён, он сам перенаправляет на безопасный DEV-вход.
- Кнопка `Крутить колесо` больше не открывает Steam. Если пользователь не авторизован, появляется аккуратное модальное окно входа.
- Кнопки покупки доната при отсутствии авторизации также показывают модальное окно, а не ломают страницу.
- Добавлен `docs/auth-bonus-fixes.md` с объяснением Steam/localhost и production-настроек.
