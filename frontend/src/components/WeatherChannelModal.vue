<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-2xl shadow-xl overflow-y-auto max-h-screen">
      <h3 class="text-lg font-semibold mb-4">
        {{ props.channel ? "Edit Weather Channel" : "Create Weather Channel" }}
      </h3>

      <form @submit.prevent="save">
        <!-- Name -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Channel Name</label>
          <input v-model="form.station_conf.network_name" type="text" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Channel Number -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Channel Number</label>
          <input v-model.number="form.station_conf.channel_number" type="number" min="1" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- IP Address -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Weather Server IP Address</label>
          <input v-model="form.station_conf.ip" type="text" placeholder="127.0.0.1" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Location -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Location (City, State, Country)</label>
          <input v-model="form.station_conf.location" type="text" placeholder="e.g. Seattle, WA, USA" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Toggles -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div v-for="opt in toggleOptions" :key="opt.key" class="flex items-center space-x-2">
            <input type="checkbox" v-model="form.station_conf.options[opt.key]" class="rounded text-brand-accent">
            <label class="text-sm">{{ opt.label }}</label>
          </div>
        </div>

        <!-- Display settings -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label class="block text-sm font-medium">Units</label>
            <select v-model="form.station_conf.settings.units"
                    class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
              <option value="us">US</option>
              <option value="metric">Metric</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium">Speed</label>
            <input v-model="form.station_conf.settings.speed" type="number" step="0.1" min="0.25" max="2"
                   class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
          </div>
          <div class="flex items-center space-x-2">
            <input type="checkbox" v-model="form.station_conf.settings.kiosk" class="rounded text-brand-accent">
            <label class="text-sm">Kiosk Mode</label>
          </div>
          <div class="flex items-center space-x-2">
            <input type="checkbox" v-model="form.station_conf.settings.autoplay" class="rounded text-brand-accent">
            <label class="text-sm">Autoplay Music</label>
          </div>
        </div>

        <!-- Preview URL -->
        <div class="mb-4">
          <label class="block text-sm font-medium">Generated URL</label>
          <textarea readonly rows="3" :value="generatedUrl"
                    class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-xs text-brand-text"></textarea>
        </div>

        <!-- Actions -->
        <div class="mt-6 flex justify-end space-x-2">
          <button type="button" @click="$emit('close')"
                  class="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600">
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
import { reactive, computed, onMounted } from "vue"
import { useChannelsStore } from "../store/channels"

const props = defineProps({
  channel: { type: Object, default: null }
})
const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

const toggleOptions = [
  { key: "hazards", label: "Hazards" },
  { key: "current-weather", label: "Current Weather" },
  { key: "latest-observations", label: "Latest Observations" },
  { key: "hourly", label: "Hourly Forecast" },
  { key: "hourly-graph", label: "Hourly Graph" },
  { key: "travel", label: "Travel" },
  { key: "regional-forecast", label: "Regional Forecast" },
  { key: "local-forecast", label: "Local Forecast" },
  { key: "extended-forecast", label: "Extended Forecast" },
  { key: "almanac", label: "Almanac" },
  { key: "spc-outlook", label: "SPC Outlook" },
  { key: "radar", label: "Radar" },
]

const form = reactive({
  station_conf: {
    network_name: "Weather",
    channel_number: 1,
    network_type: "weather",
    runtime_dir: "runtime/weather",

    ip: "127.0.0.1",
    location: "",
    web_url: "",

    options: {},
    settings: {
      units: "us",
      speed: 1.0,
      kiosk: true,
      autoplay: true,
    },
  }
})

const generatedUrl = computed(() => {
  const base = `http://${form.station_conf.ip}:9090/index.html?`
  const params = []

  for (const [key, val] of Object.entries(form.station_conf.options)) {
    if (val) params.push(`${key}-checkbox=true`)
  }

  params.push(`settings-units-select=${form.station_conf.settings.units}`)
  params.push(`settings-speed-select=${form.station_conf.settings.speed}`)
  params.push(`settings-kiosk-checkbox=${form.station_conf.settings.kiosk}`)
  params.push(`settings-mediaPlaying-boolean=${form.station_conf.settings.autoplay}`)

  if (form.station_conf.location) {
    params.push(`txtLocation=${encodeURIComponent(form.station_conf.location)}`)
    params.push(`latLonQuery=${encodeURIComponent(form.station_conf.location)}`)
  }

  return base + params.join("&")
})

onMounted(() => {
  if (props.channel?.config) {
    Object.assign(form.station_conf, JSON.parse(JSON.stringify(props.channel.config)))
  }
})

const save = async () => {
  const station_conf = {
    ...form.station_conf,
    web_url: generatedUrl.value
  }

  if (props.channel) {
    await store.updateChannel(form.station_conf.network_name, { station_conf })
  } else {
    await store.addChannel({ station_conf })
  }

  emit("saved")
  emit("close")
}
</script>
