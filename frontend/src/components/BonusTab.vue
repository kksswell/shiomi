<script setup lang="ts">
import { computed, ref } from 'vue';
import { apiFetch, authUrl, ApiError } from '@/api/http';
import type { AuthConfig, CaseReward, SpinResult, UserProfile } from '@/types';

const props = defineProps<{
  user: UserProfile | null;
  rewards: CaseReward[];
  auth: AuthConfig | null;
}>();

const emit = defineEmits<{
  'profile-updated': [];
}>();

const baseRewards: CaseReward[] = [
  { id: 1, title: '100 Кредитов', rarity: 'gray', icon: 'fa-solid fa-coins', chance: 40 },
  { id: 2, title: '500 Кредитов', rarity: 'blue', icon: 'fa-solid fa-coins', chance: 30 },
  { id: 3, title: 'VIP (3 дня)', rarity: 'cyan', icon: 'fa-solid fa-crown', chance: 18 },
  { id: 4, title: 'PREMIUM (3 дня)', rarity: 'purple', icon: 'fa-solid fa-shield-halved', chance: 8 },
  { id: 5, title: 'АДМИНКА (3 дня)', rarity: 'red', icon: 'fa-solid fa-wand-magic-sparkles', chance: 3.5 },
  { id: 6, title: 'SHIOMI STATUS', rarity: 'gold', icon: 'custom-logo', chance: 0.5 },
];

const rarityColor: Record<CaseReward['rarity'], string> = {
  gray: '#64748b',
  blue: '#3b82f6',
  cyan: '#06b6d4',
  purple: '#a855f7',
  red: '#ef4444',
  gold: '#eab308',
};

const rewardsToUse = computed(() => (props.rewards.length ? props.rewards : baseRewards));
const wheelTransform = ref('rotate(0deg)');
const wheelTransition = ref('none');
const isSpinning = ref(false);
const resultMessage = ref('');
const resultReward = ref<CaseReward | null>(null);
const authPromptOpen = ref(false);

const wheelGradient = computed(() => {
  const rewards = rewardsToUse.value;
  const segment = 360 / rewards.length;
  return `conic-gradient(${rewards
    .map((reward, index) => {
      const start = Math.max(0, index * segment - 0.4);
      const end = (index + 1) * segment;
      return `${rarityColor[reward.rarity]} ${start}deg ${end}deg`;
    })
    .join(', ')})`;
});

const nextSpinText = computed(() => {
  const date = props.user?.nextSpinAvailableAt;
  if (!date) return '';
  const time = new Date(date).getTime();
  if (Number.isNaN(time) || time <= Date.now()) return '';
  return new Intl.DateTimeFormat('ru-RU', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(time));
});

function loginWithRecommendedProvider(): void {
  const target = props.auth?.recommendedLoginUrl || (props.auth?.devLoginEnabled ? '/api/auth/steam/dev/' : '/api/auth/steam/');
  window.location.href = target.startsWith('http') ? target : authUrl(target.replace(/^\/api/, ''));
}

function closeAuthPrompt(): void {
  authPromptOpen.value = false;
}

async function spinWheel(): Promise<void> {
  if (!props.user) {
    authPromptOpen.value = true;
    resultMessage.value = 'Чтобы получить ежедневный бонус, сначала войдите в профиль.';
    return;
  }

  if (isSpinning.value) return;
  isSpinning.value = true;
  resultMessage.value = '';
  resultReward.value = null;

  try {
    const spin = await apiFetch<SpinResult>('/bonus/spin/', { method: 'POST' });
    const rewards = rewardsToUse.value;
    const index = Math.max(0, rewards.findIndex((reward) => reward.id === spin.reward.id));
    const segment = 360 / rewards.length;
    const targetAngle = 360 * 6 + (360 - (index * segment + segment / 2));

    wheelTransition.value = 'none';
    wheelTransform.value = 'rotate(0deg)';
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        wheelTransition.value = 'transform 5.4s cubic-bezier(0.12, 0.76, 0.18, 1)';
        wheelTransform.value = `rotate(${targetAngle}deg)`;
      });
    });

    window.setTimeout(() => {
      resultReward.value = spin.reward;
      resultMessage.value = `ВЫ ВЫИГРАЛИ: ${spin.reward.title}`;
      isSpinning.value = false;
      emit('profile-updated');
    }, 5600);
  } catch (error) {
    isSpinning.value = false;
    if (error instanceof ApiError && error.status === 401) {
      authPromptOpen.value = true;
      resultMessage.value = 'Сессия закончилась. Войдите снова и повторите прокрутку.';
      return;
    }
    if (error instanceof ApiError && error.status === 429) {
      resultMessage.value = 'Ежедневный бонус уже получен. Возвращайтесь позже.';
      return;
    }
    resultMessage.value = 'Не удалось прокрутить колесо. Попробуйте позже.';
  }
}
</script>

<template>
  <div class="tab-content active">
    <div class="server-header">
      <div class="server-title">
        <i class="fa-solid fa-gift text-blue"></i>
        <h2>КОЛЕСО БОНУСОВ</h2>
      </div>
    </div>

    <section class="bonus-wheel-section">
      <div class="bonus-wheel-copy">
        <span class="eyebrow"><span></span> DAILY DROP</span>
        <h3>Ежедневное колесо SHIOMI</h3>
        <p>Результат выбирается на backend, сохраняется в PostgreSQL и защищён от повторного получения в течение 24 часов.</p>
        <div v-if="nextSpinText" class="bonus-cooldown">Следующий бонус: {{ nextSpinText }}</div>
      </div>

      <div class="bonus-wheel-layout">
        <div class="wheel-stage">
          <div class="wheel-pointer" aria-hidden="true"></div>
          <div class="bonus-wheel" :style="{ background: wheelGradient, transform: wheelTransform, transition: wheelTransition }">
            <div class="wheel-inner-ring"></div>
            <div
              v-for="(reward, index) in rewardsToUse"
              :key="`wheel-${reward.id}`"
              class="wheel-label"
              :style="{ transform: `rotate(${index * (360 / rewardsToUse.length) + 360 / rewardsToUse.length / 2}deg) translateY(-152px) rotate(-${index * (360 / rewardsToUse.length) + 360 / rewardsToUse.length / 2}deg)` }"
            >
              {{ reward.title.split(' ')[0] }}
            </div>
            <div class="wheel-center">
              <div class="logo-icon">SHIOMI</div>
              <span>DROP</span>
            </div>
          </div>
          <div class="wheel-glow" aria-hidden="true"></div>
        </div>

        <div class="bonus-panel">
          <button type="button" class="btn-open-case" :disabled="isSpinning" @click="spinWheel">
            {{ isSpinning ? 'КРУТИМ...' : 'КРУТИТЬ КОЛЕСО' }}
          </button>
          <div v-if="!user" class="bonus-auth-hint">Войдите в профиль, чтобы забрать ежедневный бонус. На localhost используется безопасный DEV-вход.</div>
          <div class="case-win-notif" :class="{ show: resultMessage }">
            <span v-if="resultReward" class="rarity-dot" :class="resultReward.rarity"></span>
            {{ resultMessage }}
          </div>
        </div>
      </div>

      <div class="case-odds-table modern-odds">
        <h3><i class="fa-solid fa-list-ul text-blue"></i> Возможные призы и вероятности</h3>
        <div class="odds-grid">
          <div v-for="reward in rewardsToUse" :key="reward.id" class="odd-item" :class="{ 'gold-text': reward.rarity === 'gold' }">
            <span class="rarity-dot" :class="reward.rarity"></span> {{ reward.title }} <small>{{ reward.chance }}%</small>
          </div>
        </div>
      </div>
    </section>


    <div v-if="authPromptOpen" class="auth-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="bonus-auth-title">
      <div class="auth-modal-card">
        <button type="button" class="auth-modal-close" aria-label="Закрыть окно авторизации" @click="closeAuthPrompt">x</button>
        <div class="auth-modal-icon"><i class="fa-brands fa-steam"></i></div>
        <h3 id="bonus-auth-title">Нужен вход через Steam</h3>
        <p>Колесо защищено backend-логикой и привязано к профилю игрока. В локальном режиме кнопка использует DEV-вход и не открывает Steam OpenID напрямую.</p>
        <button type="button" class="btn-steam auth-modal-action" @click="loginWithRecommendedProvider">
          Войти через Steam <i class="fa-brands fa-steam"></i>
        </button>
      </div>
    </div>
  </div>
</template>
