# Steam / bonus fixes

## Что было исправлено

1. На localhost кнопка `Войти через Steam` больше не отправляет браузер напрямую на `steamcommunity.com/openid/login`.
2. При `STEAM_DEV_LOGIN_ENABLED=true` backend сам перенаправляет `/api/auth/steam/` на безопасный `/api/auth/steam/dev/`, если запрос пришёл с `localhost` или `127.0.0.1`.
3. Кнопка `Крутить колесо` больше не открывает Steam OpenID, если пользователь не вошёл. Вместо этого показывается аккуратное модальное окно с предложением войти.
4. Кнопки покупки доната также больше не ведут напрямую в Steam при отсутствии авторизации. Они показывают понятное состояние и открывают модальное окно входа.

## Почему Steam выдавал Access Denied

Steam OpenID может блокировать прямой локальный переход через `steamcommunity.com/openid/login` из-за связки localhost, политики Akamai/EdgeSuite, нестабильного VPN/провайдера или некорректного production-domain окружения. Поэтому для локальной разработки используется DEV-вход, а реальный Steam OpenID включается только на домене с HTTPS.

## Для локальной разработки

В `.env` должно быть:

```env
STEAM_DEV_LOGIN_ENABLED=true
FRONTEND_URL=http://localhost
BACKEND_URL=http://localhost
STEAM_OPENID_REALM=http://localhost/
STEAM_RETURN_URL=http://localhost/api/auth/steam/return/
```

## Для VPS / production

В `.env` нужно заменить:

```env
STEAM_DEV_LOGIN_ENABLED=false
FRONTEND_URL=https://example.com
BACKEND_URL=https://example.com
STEAM_OPENID_REALM=https://example.com/
STEAM_RETURN_URL=https://example.com/api/auth/steam/return/
STEAM_API_KEY=your_steam_web_api_key
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_SSL_REDIRECT=true
```
