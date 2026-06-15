<script setup lang="ts">
import { computed, ref } from 'vue';
import { ApiError, apiFetch, authUrl } from '@/api/http';
import type { AuthConfig, PurchaseResult, ShopProduct, UserProfile } from '@/types';

const props = defineProps<{
  products: ShopProduct[];
  user: UserProfile | null;
  auth: AuthConfig | null;
}>();

const fallbackProducts: ShopProduct[] = [
  {
    id: 1,
    title: 'SHIOMI STATUS',
    slug: 'shiomi-status',
    description: 'Полный доступ ко всем функциям: уникальный префикс [SHIOMI], иммунитет, доступ ко всем приватным скинам и ножам, х3 кредиты и кастомный цвет чата.',
    price: '599',
    period: '/ мес',
    productType: 'status',
    durationDays: 30,
    icon: 'fa-solid fa-gem',
    badge: 'EXCLUSIVE',
    highlight: 'shiomi',
  },
  {
    id: 2,
    title: 'VIP СТАТУС',
    slug: 'vip-status',
    description: 'Доступ к уникальным скинам, префиксам и тегам в табе, х2 кредиты.',
    price: '249',
    period: '/ мес',
    productType: 'vip',
    durationDays: 30,
    icon: 'fa-solid fa-crown text-blue',
    badge: '',
    highlight: 'default',
  },
  {
    id: 3,
    title: 'PREMIUM VIP',
    slug: 'premium-vip',
    description: 'Все права обычного VIP + иммунитет к кику, кастомные трейлы и аура.',
    price: '350',
    period: '/ мес',
    productType: 'premium',
    durationDays: 30,
    icon: 'fa-solid fa-shield-halved',
    badge: 'POPULAR',
    highlight: 'premium',
  },
  {
    id: 4,
    title: 'АДМИНКА',
    slug: 'admin',
    description: 'Возможность модерировать сервер, банить читеров и следить за порядком.',
    price: '650',
    period: '/ мес',
    productType: 'admin',
    durationDays: 30,
    icon: 'fa-solid fa-wand-magic-sparkles text-blue',
    badge: '',
    highlight: 'default',
  },
];

const isBuying = ref<number | null>(null);
const purchaseMessage = ref('');
const purchaseError = ref('');
const authPromptOpen = ref(false);
const productsToRender = computed(() => (props.products.length ? props.products : fallbackProducts));

function loginWithRecommendedProvider(): void {
  const target = props.auth?.recommendedLoginUrl || (props.auth?.devLoginEnabled ? '/api/auth/steam/dev/' : '/api/auth/steam/');
  window.location.href = target.startsWith('http') ? target : authUrl(target.replace(/^\/api/, ''));
}

function closeAuthPrompt(): void {
  authPromptOpen.value = false;
}

async function buy(product: ShopProduct): Promise<void> {
  if (!props.user) {
    purchaseError.value = 'Для создания заявки сначала войдите в профиль.';
    authPromptOpen.value = true;
    return;
  }

  if (isBuying.value) return;
  isBuying.value = product.id;
  purchaseMessage.value = '';
  purchaseError.value = '';

  try {
    const result = await apiFetch<PurchaseResult>('/shop/purchase/', {
      method: 'POST',
      body: JSON.stringify({ productId: product.id }),
    });
    purchaseMessage.value = `${result.purchase.productTitle}: ${result.detail}`;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      authPromptOpen.value = true;
      purchaseError.value = 'Сессия закончилась. Войдите снова и повторите покупку.';
    } else {
      purchaseError.value = error instanceof ApiError ? error.message : 'Не удалось создать заявку. Попробуйте позже.';
    }
  } finally {
    isBuying.value = null;
  }
}
</script>

<template>
  <div class="tab-content active">
    <div class="server-header">
      <div class="server-title">
        <i class="fa-solid fa-basket-shopping text-blue"></i>
        <h2>МАГАЗИН ДОНАТА</h2>
      </div>
    </div>

    <section class="shop-intro">
      <div>
        <span>SHIOMI STORE</span>
        <h3>Премиальные статусы для комфортной игры</h3>
      </div>
      <p>Покупка сейчас создаёт заявку в панели администратора. Проект уже готов к подключению реальной оплаты.</p>
    </section>

    <div v-if="purchaseMessage || purchaseError" class="shop-feedback" :class="{ error: purchaseError }" role="status">
      {{ purchaseError || purchaseMessage }}
    </div>

    <div class="shop-grid">
      <article
        v-for="product in productsToRender"
        :key="product.id"
        class="shop-card"
        :class="{ 'shiomi-status': product.highlight === 'shiomi', premium: product.highlight === 'premium' }"
      >
        <div v-if="product.badge" class="shop-card-badge" :class="{ 'status-gold': product.highlight === 'shiomi' }">{{ product.badge }}</div>
        <div class="shop-card-icon"><i :class="product.icon"></i></div>
        <div class="shop-meta"><span>{{ product.productType.toUpperCase() }}</span><span>{{ product.durationDays }} дней</span></div>
        <h3>{{ product.title }}</h3>
        <p>{{ product.description }}</p>
        <div class="shop-price">{{ product.price }} ₽ <span>{{ product.period }}</span></div>
        <button
          type="button"
          class="btn-buy-steam"
          :class="{ 'shiomi-btn': product.highlight === 'shiomi', 'premium-btn': product.highlight === 'premium' }"
          :disabled="isBuying === product.id"
          @click="buy(product)"
        >
          {{ isBuying === product.id ? 'Создаём заявку...' : 'Купить через Steam' }} <i class="fa-brands fa-steam"></i>
        </button>
      </article>
    </div>


    <div v-if="authPromptOpen" class="auth-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="shop-auth-title">
      <div class="auth-modal-card">
        <button type="button" class="auth-modal-close" aria-label="Закрыть окно авторизации" @click="closeAuthPrompt">x</button>
        <div class="auth-modal-icon"><i class="fa-brands fa-steam"></i></div>
        <h3 id="shop-auth-title">Войдите в профиль</h3>
        <p>Заявка на донат создаётся только для авторизованного Steam-профиля. На localhost используется безопасный DEV-вход без перехода на Steam OpenID.</p>
        <button type="button" class="btn-steam auth-modal-action" @click="loginWithRecommendedProvider">
          Войти через Steam <i class="fa-brands fa-steam"></i>
        </button>
      </div>
    </div>
  </div>
</template>
