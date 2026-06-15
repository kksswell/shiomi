# Optimization report

## Главные изменения

1. Frontend по умолчанию запускается как production build, а не Vite dev server.
2. Добавлен отдельный `docker-compose.dev.yml` для hot reload.
3. Удалены внешние CDN-зависимости из `index.html`.
4. Добавлены локальные CSS fallback-иконки.
5. Добавлены gzip/cache headers в Nginx.
6. Уменьшен backend Dockerfile и ускорена установка зависимостей через настраиваемый `PIP_INDEX_URL`.
7. Ускорена проверка CS2-сервера: `GAME_SERVER_TIMEOUT=0.7`, кэш 30 секунд.
8. Добавлены PostgreSQL indexes для основных read-paths.
9. Добавлены Docker healthcheck для backend/frontend/db.
10. Улучшена адаптивность для мобильных экранов.

## Проверки

- Python backend проходит синтаксическую проверку через `python -m compileall`.
- JSON-конфиги frontend валидны.
- Docker Compose YAML валиден через YAML parser.
- Runtime-мусор удалён из итогового архива: `.env`, `node_modules`, `__pycache__`, `*.pyc`.

## Ограничение

В архиве не было дампа старой MySQL-базы, поэтому реальные старые данные не переносились. Используется новая PostgreSQL-схема и дефолтные seed-данные через Django migration.


## Дополнительная финальная оптимизация

- Магазин переведён с заглушки `alert()` на рабочую модель заявок `PurchaseRequest` и DRF endpoint `/api/shop/purchase/`.
- Заявки на покупки доступны в Django Admin с фильтрами по статусу, товару и дате.
- Рулетка бонусов синхронизирована с backend-наградами из `/api/bonus/rewards/`, поэтому изменения в админке сразу попадают на сайт.
- Открытие кейса защищено транзакцией и блокировкой строки пользователя, что исключает двойной daily spin при одновременных запросах.
- Локальный backend теперь умеет читать `.env` из корня репозитория и из `backend/.env`, поэтому запуск через `.venv` стал безопаснее.
- Dev override получил корректный healthcheck на Vite-порт `5173`.
- Внешний Unsplash-фон удалён и заменён CSS-градиентом, чтобы первая загрузка не зависела от внешнего CDN.
