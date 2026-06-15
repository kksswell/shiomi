FROM node:20-alpine AS base

ARG NPM_CONFIG_REGISTRY=https://registry.npmmirror.com/
ENV NPM_CONFIG_REGISTRY=${NPM_CONFIG_REGISTRY} \
    npm_config_registry=${NPM_CONFIG_REGISTRY} \
    npm_config_audit=false \
    npm_config_fund=false \
    npm_config_update_notifier=false \
    npm_config_fetch_retries=5 \
    npm_config_fetch_retry_mintimeout=20000 \
    npm_config_fetch_retry_maxtimeout=120000 \
    npm_config_fetch_timeout=120000

WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --fund=false --legacy-peer-deps --package-lock=false
COPY . .

FROM base AS development
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
RUN npm run build

FROM nginx:1.27-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
