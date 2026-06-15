# Docker build troubleshooting

## NPM `Exit handler never called`

Если Docker падает на frontend-сборке с ошибкой:

```text
npm error Exit handler never called!
```

Причины обычно две:

1. нестабильная сеть Docker Desktop до npm registry;
2. lock-файл был создан в другом окружении и содержит недоступные `resolved` URL.

В проекте frontend Dockerfile намеренно использует `package.json`, а не `package-lock.json`, чтобы сборка не зависела от чужих внутренних registry URL.

Рекомендуемые команды:

```bash
docker compose down --remove-orphans
docker builder prune -f
docker compose build --no-cache frontend
docker compose build --no-cache backend
docker compose up -d
```

В `.env` можно использовать зеркало:

```env
NPM_CONFIG_REGISTRY=https://registry.npmmirror.com/
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

Если интернет стабильный, можно вернуть официальные registry:

```env
NPM_CONFIG_REGISTRY=https://registry.npmjs.org/
PIP_INDEX_URL=https://pypi.org/simple
```
