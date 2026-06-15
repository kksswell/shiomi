<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import AppHeader from '@/components/AppHeader.vue';
import FooterSocials from '@/components/FooterSocials.vue';
import ServerModal from '@/components/ServerModal.vue';
import ServerTab from '@/components/ServerTab.vue';
import ShopTab from '@/components/ShopTab.vue';
import BonusTab from '@/components/BonusTab.vue';
import RulesTab from '@/components/RulesTab.vue';
import { apiFetch } from '@/api/http';
import type { ActiveTab, AuthConfig, BootstrapPayload, CaseReward, GameServer, RuleItem, ServerStatus, ShopProduct, UserProfile } from '@/types';

const activeTab = ref<ActiveTab>('play');
const user = ref<UserProfile | null>(null);
const products = ref<ShopProduct[]>([]);
const rules = ref<RuleItem[]>([]);
const rewards = ref<CaseReward[]>([]);
const servers = ref<GameServer[]>([]);
const auth = ref<AuthConfig | null>(null);
const serverModalOpen = ref(false);
const isBooting = ref(true);
const bootstrapWarning = ref('');
const status = ref<ServerStatus>({
  players: 0,
  maxPlayers: 24,
  online: false,
  host: '170.168.115.48',
  port: 27115,
});

let onlineTimer: number | undefined;

function setTab(tab: ActiveTab): void {
  activeTab.value = tab;
  window.history.replaceState(null, '', `#${tab}`);
}

function applyBootstrap(payload: BootstrapPayload): void {
  user.value = payload.profile;
  status.value = payload.server;
  products.value = payload.products;
  rules.value = payload.rules;
  rewards.value = payload.rewards;
  servers.value = payload.servers || [];
  auth.value = payload.auth;
}

function applyQueryMessages(): void {
  const params = new URLSearchParams(window.location.search);
  const authStatus = params.get('auth');
  if (authStatus === 'failed') bootstrapWarning.value = 'Steam не подтвердил авторизацию. Проверьте URL возврата и попробуйте снова.';
  if (authStatus === 'server-error') bootstrapWarning.value = 'Steam временно недоступен или соединение было сброшено. Для localhost доступен DEV-вход, если он включён в .env.';
  if (authStatus === 'success') window.history.replaceState(null, '', window.location.pathname + window.location.hash);
}

async function loadBootstrap(): Promise<void> {
  try {
    const payload = await apiFetch<BootstrapPayload>('/bootstrap/', { timeoutMs: 2500 });
    applyBootstrap(payload);
  } catch {
    bootstrapWarning.value = bootstrapWarning.value || 'Часть данных временно недоступна. Сайт работает в безопасном fallback-режиме.';
    await Promise.allSettled([loadProfile(), loadCatalog(), loadServerStatus()]);
  } finally {
    isBooting.value = false;
  }
}

async function loadProfile(): Promise<void> {
  try {
    user.value = await apiFetch<UserProfile>('/user/profile/');
  } catch {
    user.value = null;
  }
}

async function loadServerStatus(): Promise<void> {
  try {
    status.value = await apiFetch<ServerStatus>('/server/status/', { timeoutMs: 1200 });
  } catch {
    status.value = { ...status.value, online: false, players: 0 };
  }
}

async function loadCatalog(): Promise<void> {
  try {
    products.value = await apiFetch<ShopProduct[]>('/shop/products/');
  } catch {
    products.value = [];
  }

  try {
    rules.value = await apiFetch<RuleItem[]>('/rules/');
  } catch {
    rules.value = [];
  }

  try {
    rewards.value = await apiFetch<CaseReward[]>('/bonus/rewards/');
  } catch {
    rewards.value = [];
  }
}

onMounted(() => {
  const hashTab = window.location.hash.replace('#', '') as ActiveTab;
  if (['play', 'shop', 'bonus', 'rules'].includes(hashTab)) activeTab.value = hashTab;
  applyQueryMessages();
  void loadBootstrap();
  onlineTimer = window.setInterval(loadServerStatus, 20000);
});

onUnmounted(() => {
  if (onlineTimer) window.clearInterval(onlineTimer);
});
</script>

<template>
  <AppHeader :active-tab="activeTab" :user="user" :auth="auth" @change-tab="setTab" @logout="user = null" />

  <main class="container">
    <div v-if="bootstrapWarning" class="app-warning">{{ bootstrapWarning }}</div>

    <section v-if="isBooting" class="page-skeleton" aria-label="Загрузка сайта">
      <div class="skeleton-line skeleton-title"></div>
      <div class="skeleton-card"></div>
      <div class="skeleton-dots"><span></span><span></span><span></span></div>
    </section>

    <template v-else>
      <ServerTab v-if="activeTab === 'play'" :status="status" :servers="servers" @open-server="serverModalOpen = true" @change-tab="setTab" />
      <ShopTab v-else-if="activeTab === 'shop'" :products="products" :user="user" :auth="auth" />
      <BonusTab v-else-if="activeTab === 'bonus'" :user="user" :rewards="rewards" :auth="auth" @profile-updated="loadProfile" />
      <RulesTab v-else :rules="rules" />

      <section v-if="user" class="stats-section">
        <h2 class="section-title">📊 Мой Личный Кабинет</h2>
        <div class="stats-container">
          <div class="stats-card">
            <h3>Привилегии и Баланс</h3>
            <div class="info-row">
              <span>VIP статус:</span>
              <strong :style="{ color: user.roles.vip ? '#10b981' : '#ef4444' }">{{ user.roles.vip ? 'Активен' : 'Нет' }}</strong>
            </div>
            <div class="info-row">
              <span>Баланс кредитов:</span>
              <strong style="color: #3b82f6;">{{ user.stats.points }} 💰</strong>
            </div>
          </div>

          <div class="stats-card">
            <h3>Статистика на сервере</h3>
            <div class="info-row"><span>Убийства:</span><strong style="color: #10b981;">{{ user.stats.kills }}</strong></div>
            <div class="info-row"><span>Смерти:</span><strong style="color: #f59e0b;">{{ user.stats.deaths }}</strong></div>
            <div class="info-row">
              <span>K/D Ratio:</span>
              <strong style="color: #ffffff;">{{ user.stats.deaths > 0 ? (user.stats.kills / user.stats.deaths).toFixed(2) : user.stats.kills.toFixed(2) }}</strong>
            </div>
          </div>
        </div>
      </section>
    </template>
  </main>

  <ServerModal v-model="serverModalOpen" :status="status" :server="servers[0]" />
  <FooterSocials />
</template>
