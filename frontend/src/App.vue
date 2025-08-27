<template>
  <div class="min-h-screen bg-brand-bg text-brand-text">
    <!-- Header -->
    <header class="bg-brand-accent text-white shadow">
      <div class="max-w-6xl mx-auto px-6 py-4 flex justify-between">
        <h1 class="text-2xl font-bold">📡 FS42 Tsar Tools</h1>
        <span class="text-sm opacity-80">Channel Configuration Suite</span>
      </div>
    </header>

    <!-- Router view -->
    <main class="max-w-6xl mx-auto px-6 py-6">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// nothing here
</script>
