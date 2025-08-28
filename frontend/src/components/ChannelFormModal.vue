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

        <!-- === Standard channel fields === -->
        <div v-if="form.config.network_type === 'standard'" class="space-y-3">
          <div>
            <label class="block text-sm font-medium">Tags (comma separated)</label>
            <input v-model="tagsInput" type="text"
                   class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
          </div>

          <!-- Commercial Free -->
          <div class="flex items-center space-x-2">
            <input id="commercialFree" type="checkbox" v-model="form.config.commercial_free"
                  class="h-4 w-4 text-brand-accent border-brand-muted rounded focus:ring-brand-accent">
            <label for="commercialFree" class="text-sm font-medium">Commercial Free</label>
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

          <!-- Schedule Increment -->
          <div>
            <label class="block text-sm font-medium">Schedule Increment</label>
            <select v-model.number="form.config.schedule_increment"
                    class="mt-1 p-2 border border-brand-muted bg-brand-bg rounded w-full">
              <option :value="5">5 minutes</option>
              <option :value="10">10 minutes</option>
              <option :value="15">15 minutes</option>
              <option :value="20">20 minutes</option>
              <option :value="30">30 minutes (default)</option>
              <option :value="60">60 minutes</option>
            </select>
          </div>

          <!-- Off-Air -->
          <div>
            <label class="block text-sm font-medium">Off-Air Path</label>
            <select v-model="form.config.off_air_path"
                    class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
              <option disabled value="">-- Select Off-Air File --</option>
              <option v-for="f in runtimeFiles" :key="f" :value="`runtime/${f}`">{{ f }}</option>
            </select>
          </div>

          <!-- Sign-Off -->
          <div>
            <label class="block text-sm font-medium">Sign-Off Path</label>
            <select v-model="form.config.signoff_path"
                    class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
              <option disabled value="">-- Select Sign-Off File --</option>
              <option v-for="f in runtimeFiles" :key="f" :value="`runtime/${f}`">{{ f }}</option>
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
import { reactive, watch, ref, computed, onMounted } from "vue"
import { useChannelsStore } from "../store/channels"
import axios from "axios"

const props = defineProps({ channel: Object })
const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

const originalName = ref(null)
const runtimeFiles = ref([])

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
    off_air_path: "",   // ✅ match backend key
    signoff_path: "",   // ✅ match backend key
    commercial_free: false
  },
})

const tagsInput = computed({
  get: () => form.config.tags?.join(", ") || "",
  set: (val) => {
    form.config.tags = val.split(",").map(t => t.trim()).filter(t => t.length > 0)
  }
})

watch(() => props.channel, (ch) => {
  if (ch) {
    Object.assign(form, JSON.parse(JSON.stringify(ch)))
    if (form.config.commercial_free === undefined) {
      form.config.commercial_free = false
    }
    if (!form.config.off_air_path) form.config.off_air_path = ""
    if (!form.config.signoff_path) form.config.signoff_path = ""
    originalName.value = ch.name
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
      off_air_path: "",
      signoff_path: "",
      commercial_free: false
    }
    originalName.value = null
  }
}, { immediate: true })

onMounted(async () => {
  try {
    const res = await axios.get("http://127.0.0.1:4343/runtime-files")
    runtimeFiles.value = res.data.files
  } catch (err) {
    console.error("Failed to fetch runtime files", err)
  }
})

const save = async () => {
  try {
    form.path = `${import.meta.env.VITE_FS42_ROOT}/FieldStation42/catalog/${form.name}`

    if (props.channel) {
      await store.updateChannel(originalName.value, form)
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
