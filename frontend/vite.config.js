import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // Proxy API calls to FastAPI backend
      '/channels': {
        target: 'http://127.0.0.1:4343',
        changeOrigin: true,
      },
      '/runtime-files': {
        target: 'http://127.0.0.1:4343',
        changeOrigin: true,
      }
    }
  }
})
