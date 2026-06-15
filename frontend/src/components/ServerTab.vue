<script setup lang="ts">
import { computed } from 'vue';
import type { ActiveTab, GameServer, ServerStatus } from '@/types';

const props = defineProps<{
  status: ServerStatus;
  servers: GameServer[];
}>();

const emit = defineEmits<{
  'open-server': [];
  'change-tab': [tab: ActiveTab];
}>();

const fallbackServer = computed<GameServer>(() => ({
  id: 0,
  title: 'PUBLIC',
  slug: 'public',
  mode: 'Соревновательный режим',
  mapName: 'CS2 Community',
  description: 'Премиальный PUBLIC-сервер SHIOMI: тёмный интерфейс, честная игра, бонусы и Steam-профиль.',
  host: props.status.host,
  port: props.status.port,
  address: `${props.status.host}:${props.status.port}`,
  players: props.status.players,
  maxPlayers: props.status.maxPlayers,
  online: props.status.online,
  updatedAt: props.status.updatedAt,
  imageUrl: '',
  connectUrl: `steam://connect/${props.status.host}:${props.status.port}`,
}));

const serverList = computed(() => (props.servers.length ? props.servers : [fallbackServer.value]));
const mainServer = computed(() => serverList.value[0] || fallbackServer.value);
</script>

<template>
  <div class="tab-content active">
    <section class="hero-panel" aria-labelledby="hero-title">
      <div class="hero-copy">
        <div class="eyebrow"><span></span> CS2 PROJECT • STEAM COMMUNITY</div>
        <h1 id="hero-title">SHIOMI PUBLIC — тёмный CS2-сервер с премиальной атмосферой</h1>
        <p>
          Играй в соревновательном режиме, отслеживай онлайн, забирай ежедневные бонусы и управляй донатом через Steam-профиль.
          Данные сервера и интерфейса идут через backend API, чтобы сайт был готов к реальному продакшену.
        </p>
        <div class="hero-actions">
          <button type="button" class="hero-primary" @click="emit('open-server')">
            Подключиться к серверу <i class="fa-solid fa-angles-right"></i>
          </button>
          <button type="button" class="hero-secondary" @click="emit('change-tab', 'bonus')">Открыть бонус</button>
        </div>
      </div>

      <div class="hero-status-card">
        <span class="server-online-state" :class="{ offline: !mainServer.online }">
          {{ mainServer.online ? 'SERVER ONLINE' : 'SERVER NO RESPONSE' }}
        </span>
        <strong>{{ mainServer.players }} / {{ mainServer.maxPlayers }}</strong>
        <small>игроков онлайн</small>
        <div class="hero-pulse" aria-hidden="true"></div>
      </div>
    </section>

    <div class="server-header">
      <div class="server-title">
        <i class="fa-solid fa-layer-group text-blue"></i>
        <h2>ДОСТУПНЫЕ СЕРВЕРА <span>CS2</span></h2>
      </div>
      <span class="player-count">ОБЩИЙ ОНЛАЙН: <strong>{{ props.status.players }}</strong></span>
    </div>

    <div class="server-content-area server-content-area-modern">
      <div class="server-card-layout server-card-layout-modern">
        <button
          v-for="server in serverList"
          :key="server.id || server.slug"
          class="server-card-main server-card-premium"
          type="button"
          @click="emit('open-server')"
        >
          <div class="server-card-glare" aria-hidden="true"></div>
          <div class="card-inner">
            <div class="card-header-info">
              <span class="server-card-kicker">CS2 • {{ server.mapName || 'COMMUNITY' }}</span>
              <h3>{{ server.title }}</h3>
              <p>{{ server.mode }}</p>
            </div>
            <div class="card-status-footer">
              <span class="server-online-state" :class="{ offline: !server.online }">
                {{ server.online ? 'ONLINE' : 'NO RESPONSE' }}
              </span>
              <span class="slots-badge"><i class="fa-solid fa-users"></i> {{ server.players }} / {{ server.maxPlayers }}</span>
            </div>
          </div>
        </button>
      </div>

      <div class="server-info-grid">
        <article class="mini-info-card">
          <span>01</span>
          <h3>Steam-ready</h3>
          <p>Авторизация, профиль, заявки, бонусы и logout завязаны на безопасную backend-сессию.</p>
        </article>
        <article class="mini-info-card">
          <span>02</span>
          <h3>Backend drop</h3>
          <p>Результат колеса рассчитывается на Django backend, сохраняется в PostgreSQL и не подкручивается через frontend.</p>
        </article>
        <article class="mini-info-card">
          <span>03</span>
          <h3>Server API</h3>
          <p>Список серверов управляется через Django Admin и готов к замене mock-данных на Source Query.</p>
        </article>
      </div>
    </div>
  </div>
</template>
