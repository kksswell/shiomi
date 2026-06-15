import { fileURLToPath, URL } from 'node:url';
import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendUrl = env.VITE_DEV_BACKEND_URL || 'http://backend:8000';

  return {
    plugins: [vue()],
    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
        '/admin': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
        '/media': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
        '/static': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      cssCodeSplit: true,
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vue: ['vue', 'vue-router'],
          },
        },
      },
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  };
});
