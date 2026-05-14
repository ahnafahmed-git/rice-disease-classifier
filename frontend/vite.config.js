import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// ⚠️ Change 'rice-disease-classifier' to your exact GitHub repository name
export default defineConfig({
  plugins: [react()],
  base: '/rice-disease-classifier/',
})