<script setup lang="ts">
import { computed, ref } from 'vue';
import type { GameServer, ServerStatus } from '@/types';

const props = defineProps<{
  modelValue: boolean;
  status: ServerStatus;
  server?: GameServer;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

const copied = ref(false);
const serverAddress = computed(() => props.server?.address || `${props.status.host}:${props.status.port}`);
const title = computed(() => props.server?.title || 'SHIOMI PUBLIC');
const mode = computed(() => props.server?.mode || 'Соревновательный режим');
const description = computed(() => props.server?.description || 'Классический соревновательный режим с уникальными скинами, тёмной атмосферой и удобным входом через Steam.');
const connectUrl = computed(() => props.server?.connectUrl || `steam://connect/${serverAddress.value}`);
const mapName = computed(() => props.server?.mapName || 'CS2 Community');

async function copyServerIp(): Promise<void> {
  try {
    await navigator.clipboard.writeText(serverAddress.value);
  } catch {
    const input = document.getElementById('serverIpInput') as HTMLInputElement | null;
    input?.select();
    document.execCommand('copy');
  }
  copied.value = true;
  window.setTimeout(() => {
    copied.value = false;
  }, 1800);
}
</script>

<template>
  <Teleport to="body">
    <div class="modal-overlay" :class="{ active: props.modelValue }" @click.self="emit('update:modelValue', false)">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="server-modal-title">
        <button class="modal-close-btn" type="button" aria-label="Закрыть окно" @click="emit('update:modelValue', false)">&times;</button>
        <div class="modal-server-badge">CS2 СЕРВЕР • {{ mapName }}</div>
        <h3 id="server-modal-title" class="modal-server-title">SHIOMI {{ title }}</h3>
        <p class="modal-server-desc">{{ description }}</p>

        <div class="modal-info-grid">
          <div class="modal-info-item">
            <span class="info-label">Текущий статус</span>
            <span class="info-value text-blue"><i class="fa-solid fa-circle-check"></i> {{ props.status.online ? 'Работает' : 'Нет ответа' }}</span>
          </div>
          <div class="modal-info-item">
            <span class="info-label">Режим</span>
            <span class="info-value">{{ mode }}</span>
          </div>
          <div class="modal-info-item">
            <span class="info-label">Игроки онлайн</span>
            <span class="info-value">{{ props.status.players }} / {{ props.status.maxPlayers }}</span>
          </div>
          <div class="modal-info-item">
            <span class="info-label">Steam connect</span>
            <span class="info-value">Готов</span>
          </div>
        </div>

        <div class="ip-address-block">
          <span class="ip-title">АДРЕС ДЛЯ ПОДКЛЮЧЕНИЯ</span>
          <div class="ip-input-wrapper">
            <input id="serverIpInput" type="text" :value="serverAddress" readonly aria-label="IP адрес сервера" />
            <button class="btn-copy-ip" type="button" title="Копировать IP" @click="copyServerIp">
              <i class="fa-regular fa-copy"></i>
            </button>
          </div>
          <span v-if="copied" class="copy-toast">IP скопирован</span>
        </div>

        <a :href="connectUrl" class="btn-connect-server">
          ПОДКЛЮЧИТЬСЯ <i class="fa-solid fa-angles-right"></i>
        </a>
      </div>
    </div>
  </Teleport>
</template>
