<template>
  <div class="app-shell">
    <header class="app-header" role="banner">
      <nav class="nav" aria-label="Main navigation">
        <span class="nav-brand">Resume Builder</span>
        <ul class="nav-links" role="list">
          <li>
            <RouterLink to="/" class="nav-link" active-class="nav-link--active">
              Profile
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/generate" class="nav-link" active-class="nav-link--active">
              Generate Resume
            </RouterLink>
          </li>
        </ul>
      </nav>
    </header>

    <div v-if="globalError" class="error-banner" role="alert">
      <span>{{ globalError }}</span>
      <button class="error-dismiss" @click="globalError = null" aria-label="Dismiss error">
        ✕
      </button>
    </div>

    <main class="app-main" id="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const globalError = ref<string | null>(null)

onMounted(() => {
  window.addEventListener('unhandledrejection', (event) => {
    globalError.value = 'An unexpected error occurred. Please try again.'
    event.preventDefault()
  })
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-surface, #f9fafb);
}

.app-header {
  background: #fff;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-3, 12px) var(--space-4, 16px);
  display: flex;
  align-items: center;
  gap: var(--space-6, 24px);
}

.nav-brand {
  font-weight: 700;
  font-size: var(--font-lg, 16px);
  color: var(--color-primary, #1a56db);
}

.nav-links {
  display: flex;
  gap: var(--space-4, 16px);
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  text-decoration: none;
  color: var(--color-muted, #6b7280);
  font-size: var(--font-base, 14px);
  font-weight: 500;
  padding: var(--space-1, 4px) var(--space-2, 8px);
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
}

.nav-link:hover {
  color: var(--color-primary, #1a56db);
  background: #eff6ff;
}

.nav-link--active {
  color: var(--color-primary, #1a56db);
  font-weight: 700;
}

.app-main {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: var(--space-6, 24px) var(--space-4, 16px);
}

.error-banner {
  background: #fef2f2;
  border-bottom: 1px solid #fca5a5;
  color: #b91c1c;
  padding: var(--space-2, 8px) var(--space-4, 16px);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-sm, 12px);
}

.error-dismiss {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: var(--font-base, 14px);
  padding: 0 var(--space-1, 4px);
}
</style>
