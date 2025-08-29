<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-md shadow-xl">
      <h3 class="text-lg font-semibold mb-4">
        Edit {{ day }} @ {{ hour }}h
      </h3>

      <!-- Tags -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Tags</label>
        <select
          v-model="form.tags"
          multiple
          class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text h-28"
        >
          <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
          <option value="off_air">Off-Air</option>
          <option value="signoff">Sign-Off</option>
        </select>

        <div class="flex flex-wrap mt-2 gap-1">
          <span
            v-for="tag in form.tags"
            :key="tag"
            class="px-2 py-1 rounded text-xs font-medium text-white"
            :style="{ backgroundColor: getTagColor(tag) }"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Start Bump -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Start Bump</label>
        <div class="flex gap-2 items-center">
          <input
            type="text"
            v-model="form.start_bump"
            readonly
            class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted"
          />
          <input
            type="file"
            ref="startBumpInput"
            class="hidden"
            accept="video/*"
            @change="onFileSelect($event, 'start_bump')"
          />
          <button
            type="button"
            @click="triggerFileInput('startBumpInput')"
            class="px-2 py-1 bg-brand-accent text-white rounded"
          >
            + File
          </button>
        </div>
      </div>

      <!-- End Bump -->
      <div class="mb-3">
        <label class="block text-sm font-medium">End Bump</label>
        <div class="flex gap-2 items-center">
          <input
            type="text"
            v-model="form.end_bump"
            readonly
            class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted"
          />
          <input
            type="file"
            ref="endBumpInput"
            class="hidden"
            accept="video/*"
            @change="onFileSelect($event, 'end_bump')"
          />
          <button
            type="button"
            @click="triggerFileInput('endBumpInput')"
            class="px-2 py-1 bg-brand-accent text-white rounded"
          >
            + File
          </button>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-2">
        <button
          @click="$emit('close')"
          class="px-3 py-2 rounded bg-brand-muted hover:bg-brand-accent text-brand-text"
        >
          Cancel
        </button>
        <button
          @click="save"
          class="px-3 py-2 rounded bg-brand-accent text-white hover:bg-brand-accentHover"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import { useChannelsStore } from "../store/channels"

const props = defineProps({
  day: String,
  hour: Number,
  channel: String,
  tags: Array,
  tagColors: Object,
  slot: Object
})

const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

const form = reactive({
  tags: props.slot?.tags || [],
  start_bump: props.slot?.start_bump || "",
  end_bump: props.slot?.end_bump || ""
})

// === Color logic (matches SchedulePage) ===
const defaultTagColors = {
  off_air: "#ff0000",   // 🔴 red
  signoff: "#ff7f00"    // 🟠 orange
}

function isValidColor(color) {
  return typeof color === "string" && /^#[0-9A-Fa-f]{6}$/.test(color)
}

function getTagColor(tag) {
  if (isValidColor(props.tagColors?.[tag])) return props.tagColors[tag]
  if (defaultTagColors[tag]) return defaultTagColors[tag]
  return "#3b52f6" // 🔵 fallback
}

// === File inputs ===
const startBumpInput = ref(null)
const endBumpInput = ref(null)

function triggerFileInput(refName) {
  if (refName === "startBumpInput") startBumpInput.value.click()
  if (refName === "endBumpInput") endBumpInput.value.click()
}

function onFileSelect(e, field) {
  const file = e.target.files[0]
  if (file) form[field] = `runtime/${file.name}`
}

const save = async () => {
  await store.patchSlot(props.channel, props.day, props.hour, { ...form })
  emit("saved")
  emit("close")
}
</script>
