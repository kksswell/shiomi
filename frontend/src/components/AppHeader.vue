<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { authUrl, apiFetch } from '@/api/http';
import type { ActiveTab, AuthConfig, UserProfile } from '@/types';

const props = defineProps<{
  activeTab?: ActiveTab;
  user: UserProfile | null;
  showNav?: boolean;
  auth?: AuthConfig | null;
}>();

const emit = defineEmits<{
  'change-tab': [tab: ActiveTab];
  'logout': [];
}>();

const router = useRouter();
const tabs: Array<{ key: ActiveTab; label: string; icon: string }> = [
  { key: 'play', label: 'Играть', icon: 'fa-solid fa-play' },
  { key: 'shop', label: 'Магазин', icon: 'fa-solid fa-basket-shopping' },
  { key: 'bonus', label: 'Бонусы', icon: 'fa-solid fa-gift' },
  { key: 'rules', label: 'Правила', icon: 'fa-solid fa-scale-balanced' },
];

const activeTab = computed(() => props.activeTab || 'play');
const avatarSrc = computed(() => props.user?.avatar || '/logo.jpg');

function loginWithSteam(): void {
  const target = props.auth?.recommendedLoginUrl || (props.auth?.devLoginEnabled ? '/api/auth/steam/dev/' : '/api/auth/steam/');
  window.location.href = target.startsWith('http') ? target : authUrl(target.replace(/^\/api/, ''));
}

async function logout(): Promise<void> {
  try {
    await apiFetch('/auth/logout/', { method: 'POST' });
  } finally {
    emit('logout');
    await router.push('/');
  }
}
</script>

<template>
  <header class="header">
    <RouterLink to="/" class="logo-section" aria-label="SHIOMI на главную">
      <div class="logo-icon">SHIOMI</div>
      <span class="logo-text">SHIO<span>MI</span></span>
    </RouterLink>

    <nav v-if="showNav !== false" class="nav" aria-label="Основная навигация">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="nav-link"
        :class="{ active: activeTab === tab.key }"
        @click="emit('change-tab', tab.key)"
      >
        <i :class="tab.icon"></i> {{ tab.label }}
      </button>
    </nav>

    <div id="authContainer" class="auth-actions">
      <template v-if="!user">
        <button type="button" class="btn-steam" id="steamBtn" @click="loginWithSteam">
          <span>Войти через Steam</span> <i class="fa-brands fa-steam"></i>
        </button>
      </template>

      <div v-else id="userProfile" class="user-profile-block">
        <RouterLink to="/profile" class="clickable-profile" aria-label="Открыть профиль игрока">
          <img :src="avatarSrc" :alt="`Аватар ${user.username}`" class="avatar-img" loading="lazy" />
          <div class="profile-info">
            <span class="user-name-text">{{ user.username }}</span>
            <span class="status-badge">{{ user.roles.vip ? 'VIP' : 'Игрок' }}</span>
          </div>
        </RouterLink>
        <button type="button" class="logout-link" title="Выйти" aria-label="Выйти из профиля" @click="logout">
          <i class="fa-solid fa-right-from-bracket"></i>
        </button>
      </div>
    </div>
  </header>
</template>
