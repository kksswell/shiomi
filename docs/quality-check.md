# Quality check

Проверки, выполненные перед упаковкой архива:

```bash
cd backend
python -m py_compile $(find . -name '*.py')
python manage.py check
python manage.py makemigrations --check --dry-run
```

```bash
cd frontend
npm install --no-audit --fund=false
npm run build
```

Результат:

- Django system check: без ошибок.
- Django migrations check: изменений моделей без миграций не найдено.
- Vue/Vite production build: успешно.
- Docker Compose YAML: `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.prod.yml` валидны.

Примечание: проверка истории миграций при `makemigrations --check --dry-run` может показывать предупреждение о недоступном PostgreSQL, если команда выполняется вне Docker. Это не является ошибкой структуры миграций; полноценный запуск миграций выполняется через `docker compose exec backend python manage.py migrate` после старта `db`.
