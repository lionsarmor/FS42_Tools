<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-md shadow-xl">
      <h3 class="text-lg font-semibold mb-4">
        Edit {{ day }} @ {{ hour }}h
      </h3>
      <!-- Tags -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Tags</label>
        <select v-model="form.tags" multiple
                class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text h-28">
          <option v-for="tag in tags" :key="tag" :value="tag">{{ tag }}</option>
          <option value="off_air">Off-Air</option>
          <option value="signoff">Sign-Off</option>
        </select>
        <div class="flex flex-wrap mt-2 gap-1">
          <span v-for="tag in form.tags" :key="tag"
                class="px-2 py-1 rounded text-xs font-medium"
                :style="{ backgroundColor: isValidColor(tagColors?.[tag]) ? tagColors[tag] : '#666666' }">
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Start Bump -->
      <div class="mb-3">
        <label class="block text-sm font-medium">Start Bump</label>
        <select v-model="form.start_bump"
                class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
          <option value="">None</option>
          <option v-for="f in bumpFiles" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>

      <!-- End Bump -->
      <div class="mb-3">
        <label class="block text-sm font-medium">End Bump</label>
        <select v-model="form.end_bump"
                class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
          <option value="">None</option>
          <option v-for="f in bumpFiles" :key="f" :value="f">{{ f }}</option>
        </select>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-2">
        <button @click="$emit('close')"
                class="px-3 py-2 rounded bg-brand-muted hover:bg-brand-accent text-brand-text">
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
import { reactive, onMounted, ref } from "vue"
import axios from "axios"
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

// form state
const form = reactive({
  tags: props.slot?.tags || [],
  start_bump: props.slot?.start_bump || "",
  end_bump: props.slot?.end_bump || ""
})

// bump dropdown files
const bumpFiles = ref([])

function isValidColor(color) {
  return typeof color === "string" && /^#[0-9A-Fa-f]{6}$/.test(color)
}

const loadFiles = async () => {
  try {
    const res = await axios.get(`/channels/${props.channel}/bump`)
    bumpFiles.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.warn("Failed to load bump files", err)
    bumpFiles.value = []
  }
}

const save = async () => {
  await store.patchSlot(props.channel, props.day, props.hour, { ...form })
  emit("saved")
  emit("close")
}

onMounted(loadFiles)
</script>

