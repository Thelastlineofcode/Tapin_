import {
    defineConfig
} from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    root: '.', // Keep root at project root
    publicDir: 'frontend/src/assets', // Public assets from frontend
    server: {
        port: 3000
    },
    build: {
        outDir: 'dist',
    },
    resolve: {
        alias: {
            '@': '/frontend/src'
        }
    }
})
