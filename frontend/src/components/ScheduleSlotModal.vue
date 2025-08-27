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
               placeholder="caps/sb.mp4"
               class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
      </div>
      <div class="mb-3">
        <label class="block text-sm font-medium">End Bump Path</label>
        <input v-model="form.end_bump" type="text"
               placeholder="caps/eb.mp4"
               class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-2">
        <button @click="$emit('close')"
                class="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600">
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

<script setup>
import { reactive, computed } from "vue"
import { useChannelsStore } from "../store/channels"

const props = defineProps({
  channelName: String,
  day: String,
  hour: Number,
  slot: { type: Object, default: () => ({}) }
})
const emit = defineEmits(["close"])
const store = useChannelsStore()

// Local form
const form = reactive({
  tags: props.slot.tags || [],
  event: props.slot.event || "",
  start_bump: props.slot.start_bump || "",
  end_bump: props.slot.end_bump || "",
})

// Tags input as comma-separated
const tagsInput = computed({
  get: () => Array.isArray(form.tags) ? form.tags.join(", ") : form.tags || "",
  set: (val) => {
    form.tags = val.split(",").map(t => t.trim()).filter(t => t.length > 0)
  }
})

const save = async () => {
  const slotData = {}
  if (form.tags && form.tags.length) slotData.tags = form.tags
  if (form.event) slotData.event = form.event
  if (form.start_bump) slotData.start_bump = form.start_bump
  if (form.end_bump) slotData.end_bump = form.end_bump

  await store.patchSlot(props.channelName, props.day, props.hour, slotData)
  emit("close")
}
</script>
