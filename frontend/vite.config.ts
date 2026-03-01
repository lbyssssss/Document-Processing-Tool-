import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    allowedHosts: ['.monkeycode-ai.online'],
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        timeout: 300000,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log(`Proxying: ${req.method} ${req.url} -> http://localhost:3001${req.url}`)
          })
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log(`Proxy response: ${req.method} ${req.url} -> Status: ${proxyRes.statusCode}`)
          })
          proxy.on('error', (err, _req, _res) => {
            console.log('Proxy error:', err)
          })
        }
      },
    },
  },
  preview: {
    allowedHosts: ['.monkeycode-ai.online'],
  },
})
