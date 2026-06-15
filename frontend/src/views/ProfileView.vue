<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import AppHeader from '@/components/AppHeader.vue';
import FooterSocials from '@/components/FooterSocials.vue';
import { apiFetch } from '@/api/http';
import type { UserProfile } from '@/types';

const router = useRouter();
const user = ref<UserProfile | null>(null);
const isLoading = ref(true);

const avatarSrc = computed(() => user.value?.avatar || '/logo.jpg');

const kdRatio = computed(() => {
  if (!user.value) return '0.00';
  return user.value.stats.deaths > 0
    ? (user.value.stats.kills / user.value.stats.deaths).toFixed(2)
    : user.value.stats.kills.toFixed(2);
});

const headshotRate = computed(() => {
  if (!user.value || user.value.stats.kills <= 0) return '0%';
  return `${Math.round((user.value.stats.headshots / user.value.stats.kills) * 100)}%`;
});

function formatDate(value: string | null | undefined): string {
  if (!value) return 'не указано';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'не указано';
  return new Intl.DateTimeFormat('ru-RU', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
}

async function loadProfile(): Promise<void> {
  try {
    user.value = await apiFetch<UserProfile>('/user/profile/');
  } catch {
    await router.push('/');
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadProfile);
</script>

<template>
  <AppHeader :user="user" :show-nav="false" @logout="user = null" />

  <main class="container profile-page-container">
    <RouterLink to="/" class="back-link">← Назад на главную</RouterLink>

    <template v-if="isLoading">
      <section class="profile-hero profile-loading">
        <div class="skeleton-card"></div>
      </section>
    </template>

    <template v-else-if="user">
      <section class="profile-hero profile-hero-premium">
        <img :src="avatarSrc" :alt="`Аватар ${user.username}`" class="profile-hero-avatar" />
        <div class="profile-hero-copy">
          <span class="eyebrow"><span></span> STEAM PROFILE</span>
          <h1>{{ user.username }}</h1>
          <p>Steam ID64: {{ user.steamId }}</p>
          <p>Steam ID2: {{ user.steamId2 || 'будет заполнен после входа' }}</p>
        </div>
        <div class="profile-rank-card">
          <small>УРОВЕНЬ</small>
          <strong>{{ user.stats.level }}</strong>
          <span>{{ user.roles.admin ? 'ADMIN' : user.roles.vip ? 'VIP' : 'PLAYER' }}</span>
        </div>
      </section>

      <section class="profile-grid-section">
        <article class="stats-card profile-wide-card">
          <h3>Аккаунт и входы</h3>
          <div class="info-row"><span>Дата регистрации:</span><strong>{{ formatDate(user.createdAt) }}</strong></div>
          <div class="info-row"><span>Первый вход:</span><strong>{{ formatDate(user.firstLoginAt) }}</strong></div>
          <div class="info-row"><span>Последний вход:</span><strong>{{ formatDate(user.lastLoginAt) }}</strong></div>
        </article>

        <article class="stats-card profile-wide-card">
          <h3>Активные привилегии</h3>
          <div v-for="privilege in user.privileges" :key="privilege.title" class="privilege-row" :class="{ inactive: !privilege.active }">
            <span>{{ privilege.title }}</span>
            <strong>{{ privilege.active ? 'Активно' : 'Неактивно' }}</strong>
            <small>{{ privilege.expiresAt ? `до ${formatDate(privilege.expiresAt)}` : 'без срока' }}</small>
          </div>
        </article>
      </section>

      <h2 class="section-title">📊 ЛИЧНЫЙ КАБИНЕТ</h2>
      <div class="stats-container profile-stats-grid">
        <div class="stats-card stat-highlight">
          <h3>Привилегии и баланс</h3>
          <div class="info-row">
            <span>VIP статус:</span>
            <strong :style="{ color: user.roles.vip ? '#10b981' : '#ef4444' }">{{ user.roles.vip ? 'Активен' : 'Нет' }}</strong>
          </div>
          <div class="info-row">
            <span>Админ:</span>
            <strong :style="{ color: user.roles.admin ? '#10b981' : '#ef4444' }">{{ user.roles.admin ? 'Да' : 'Нет' }}</strong>
          </div>
          <div class="info-row">
            <span>Баланс кредитов:</span>
            <strong style="color: #3b82f6;">{{ user.stats.points }} 💰</strong>
          </div>
        </div>

        <div class="stats-card stat-highlight">
          <h3>Статистика на сервере</h3>
          <div class="info-row"><span>Убийства:</span><strong style="color: #10b981;">{{ user.stats.kills }}</strong></div>
          <div class="info-row"><span>Смерти:</span><strong style="color: #f59e0b;">{{ user.stats.deaths }}</strong></div>
          <div class="info-row"><span>Headshots:</span><strong style="color: #06b6d4;">{{ user.stats.headshots }}</strong></div>
          <div class="info-row"><span>Headshot rate:</span><strong style="color: #93c5fd;">{{ headshotRate }}</strong></div>
          <div class="info-row"><span>K/D Ratio:</span><strong style="color: #ffffff;">{{ kdRatio }}</strong></div>
        </div>
      </div>
    </template>
  </main>

  <FooterSocials />
</template>
