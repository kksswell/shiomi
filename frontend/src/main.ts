import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import HomeView from './views/HomeView.vue';
import ProfileView from './views/ProfileView.vue';
import './styles/main.scss';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/profile', name: 'profile', component: ProfileView },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

createApp(App).use(router).mount('#app');
