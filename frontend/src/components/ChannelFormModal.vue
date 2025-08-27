<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-2xl shadow-xl">
      <h3 class="text-lg font-semibold mb-4">
        {{ channel ? "Edit Channel" : "Add Channel" }}
      </h3>

      <form @submit.prevent="save" class="space-y-4">
        <!-- Name -->
        <div>
          <label class="block text-sm font-medium">Name</label>
          <input v-model="form.name" type="text" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Channel Number -->
        <div>
          <label class="block text-sm font-medium">Channel Number</label>
          <input v-model.number="form.config.channel_number" type="number" min="1"
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Network Type -->
        <div>
          <label class="block text-sm font-medium">Network Type</label>
          <select v-model="form.config.network_type"
                  class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
            <option value="standard">Standard</option>
            <option value="loop">Loop</option>
            <option value="streaming">Streaming</option>
            <option value="web">Web</option>
          </select>
        </div>

        <!-- === Conditional fields === -->
        <div v-if="form.config.network_type === 'standard'" class="space-y-3">
          <div>
            <label class="block text-sm font-medium">Tags (comma separated)</label>
            <input v-model="tagsInput" type="text"
                   class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
          </div>

          <div>
            <label class="block text-sm font-medium">Break Strategy</label>
            <select v-model="form.config.break_strategy"
                    class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
              <option value="standard">Standard</option>
              <option value="end">End</option>
              <option value="center">Center</option>
            </select>
          </div>

<div class="mb-3">
  <label class="block text-sm font-medium">Schedule Increment</label>
  <select v-model.number="form.config.schedule_increment"
          class="mt-1 p-2 border border-gray-600 bg-gray-900 rounded w-full">
    <option :value="5">5 minutes</option>
    <option :value="10">10 minutes</option>
    <option :value="15">15 minutes</option>
    <option :value="20">20 minutes</option>
    <option :value="30">30 minutes (default)</option>
    <option :value="60">60 minutes</option>
  </select>
</div>
        </div>

        <!-- Streaming channel -->
        <div v-if="form.config.network_type === 'streaming'" class="space-y-2">
          <h4 class="text-sm font-semibold">Streams</h4>
          <div v-for="(s, i) in form.config.streams" :key="i"
               class="bg-brand-bg p-3 rounded mb-2 border border-brand-muted">
            <input v-model="s.url" placeholder="Stream URL"
                   class="w-full mb-1 p-1 rounded bg-brand-surface border border-brand-muted text-brand-text"/>
            <input v-model.number="s.duration" placeholder="Duration (minutes)" type="number"
                   class="w-full mb-1 p-1 rounded bg-brand-surface border border-brand-muted text-brand-text"/>
            <input v-model="s.title" placeholder="Title"
                   class="w-full mb-1 p-1 rounded bg-brand-surface border border-brand-muted text-brand-text"/>
            <button type="button"
                    @click="form.config.streams.splice(i,1)"
                    class="text-brand-danger hover:text-red-400 text-xs">Remove</button>
          </div>
          <button type="button"
                  @click="form.config.streams.push({url:'',duration:30,title:''})"
                  class="px-3 py-1 bg-brand-success text-white rounded hover:bg-green-600 text-sm">
            + Add Stream
          </button>
        </div>

        <!-- Web channel -->
        <div v-if="form.config.network_type === 'web'">
          <label class="block text-sm font-medium">Web URL</label>
          <input v-model="form.config.web_url"
                 placeholder="http://localhost:4242/static/diagnostics.html"
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Actions -->
        <div class="pt-4 flex justify-end space-x-2">
          <button type="button" @click="$emit('close')"
                  class="px-3 py-2 rounded bg-brand-muted hover:bg-gray-600">
            Cancel
          </button>
          <button type="submit"
                  class="px-3 py-2 rounded bg-brand-accent text-white hover:bg-brand-accentHover">
            Save
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, ref, computed } from "vue"
import { useChannelsStore } from "../store/channels"

const props = defineProps({ channel: Object })
const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

// 🆕 keep original name separately
const originalName = ref(null)

const form = reactive({
  name: "",
  path: "",
  config: {
    tags: [],
    channel_number: 1,
    network_type: "standard",
    break_strategy: "standard",
    schedule_increment: 30,
    streams: [],
    web_url: "",
  },
})

const tagsInput = computed({
  get: () => form.config.tags?.join(", ") || "",
  set: (val) => {
    form.config.tags = val.split(",").map(t => t.trim()).filter(t => t.length > 0)
  }
})

watch(
  () => props.channel,
  (ch) => {
    if (ch) {
      Object.assign(form, JSON.parse(JSON.stringify(ch)))
      originalName.value = ch.name   // 🆕 snapshot the old name
    } else {
      form.name = ""
      form.path = ""
      form.config = {
        tags: [],
        channel_number: 1,
        network_type: "standard",
        break_strategy: "standard",
        schedule_increment: 30,
        streams: [],
        web_url: "",
      }
      originalName.value = null
    }
  },
  { immediate: true }
)

const save = async () => {
  try {
    form.path = `/mnt/media01/projects/FS42-Tsar-Tools/catalog/${form.name}`
    if (props.channel) {
      await store.updateChannel(originalName.value, form) // ✅ always use the old name
    } else {
      await store.addChannel(form)
    }
    emit("saved")
    emit("close")
  } catch (err) {
    alert("Failed to save channel: " + err.message)
  }
}
</script>
