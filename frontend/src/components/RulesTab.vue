<script setup lang="ts">
import { ref, computed } from 'vue';
import type { RuleItem } from '@/types';

const props = defineProps<{
  rules: RuleItem[];
}>();

const opened = ref<number | null>(0);
const fallbackRules: RuleItem[] = [
  {
    id: 1,
    title: '1. Игровой процесс',
    description: 'Запрещено использование любых сторонних программ, скриптов, макросов или читов, дающих преимущество над другими игроками.',
    points: ['Запрещены читы, макросы, скрипты и стороннее ПО.', 'Запрещено намеренно мешать своей команде.', 'Наказание: от предупреждения до перманентного бана.'],
  },
  {
    id: 2,
    title: '2. Общение в чате и микрофоне',
    description: 'Запрещены оскорбления игроков, администрации, разжигание конфликтов, спам, флуд и реклама сторонних ресурсов.',
    points: ['Уважайте игроков и администрацию.', 'Не используйте микрофон для шума, музыки и спама.', 'Наказание: мут, кик или бан по ситуации.'],
  },
  {
    id: 3,
    title: '3. Обязанности Администрации',
    description: 'Администратор обязан следить за порядком и справедливо наказывать нарушителей.',
    points: ['Запрещено злоупотреблять правами.', 'Все спорные ситуации разбираются руководством проекта.', 'Администратор обязан сохранять спокойствие и объективность.'],
  },
];

const rulesToRender = computed(() => (props.rules.length ? props.rules : fallbackRules));

function toggle(index: number): void {
  opened.value = opened.value === index ? null : index;
}
</script>

<template>
  <div class="tab-content active">
    <div class="server-header">
      <div class="server-title">
        <i class="fa-solid fa-scale-balanced text-blue"></i>
        <h2>СВОД ПРАВИЛ ПРОЕКТА</h2>
      </div>
    </div>

    <section class="rules-intro">
      <span>FAIR PLAY</span>
      <h3>Правила нужны для комфортной игры и честной атмосферы</h3>
      <p>Раздел управляется через Django Admin: администратор может менять тексты и порядок без правки frontend-кода.</p>
    </section>

    <div class="rules-accordion">
      <div v-for="(rule, index) in rulesToRender" :key="rule.id" class="rules-item" :class="{ open: opened === index }">
        <button
          class="rules-question"
          type="button"
          :aria-expanded="opened === index"
          :aria-controls="`rule-answer-${rule.id}`"
          @click="toggle(index)"
        >
          <span>{{ rule.title }}</span> <i class="fa-solid fa-chevron-down"></i>
        </button>
        <div :id="`rule-answer-${rule.id}`" class="rules-answer">
          <p>{{ rule.description }}</p>
          <ul v-if="rule.points?.length" class="rules-points">
            <li v-for="point in rule.points" :key="point">{{ point }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
