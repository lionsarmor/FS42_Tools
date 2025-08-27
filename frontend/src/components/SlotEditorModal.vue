<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-md shadow-xl">
      <h3 class="text-lg font-semibold mb-4">
        Edit {{ day }} @ {{ hour }}h
      </h3>

      <!-- Tags -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Tags (comma separated)</label>
        <input v-model="tagsInput" type="text"
               class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
      </div>

      <!-- Event -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Event</label>
        <select v-model="form.event"
                class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
          <option value="">None</option>
          <option value="signoff">Signoff</option>
        </select>
      </div>

      <!-- Start / End bump -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Start Bump Path</label>
        <input v-model="form.start_bump" type="text"
               class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
      </div>
      <div class="mb-3">
        <label class="block text-sm font-medium">End Bump Path</label>
        <input v-model="form.end_bump" type="text"
               class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-2">
        <button @click="$emit('close')"
                class="px-3 py-2 rounded bg-brand-muted hover:bg-gray-600">
          Cancel
        </button>
        <button @click="save"
                class="px-3 py-2 rounded bg-brand-accent text-white hover:bg-brand-accentHover">
          Save
        </button>
      </div>
    </div>
  </div>
</template>
