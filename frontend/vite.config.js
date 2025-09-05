import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      allowedHosts: [
        'tools.radroddy.com',
        'localhost',
        '127.0.0.1'
      ],
      proxy: mode === 'development'
        ? {
            '/channels': {
              target: 'http://127.0.0.1:4343',
              changeOrigin: true,
            },
            '/runtime-files': {
              target: 'http://127.0.0.1:4343',
              changeOrigin: true,
            }
          }
        : undefined
    }
  }
})
