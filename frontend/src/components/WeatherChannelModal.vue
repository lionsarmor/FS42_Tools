<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-3xl shadow-xl overflow-y-auto max-h-screen">
      <h3 class="text-lg font-semibold mb-4">
        {{ channel ? "Edit Weather Channel" : "Create Weather Channel" }}
      </h3>

      <form @submit.prevent="save">
        <!-- Name -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Channel Name</label>
          <input v-model="form.name" type="text" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Channel Number -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Channel Number</label>
          <input v-model.number="form.channel_number" type="number" min="1" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- IP Address -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Weather Server IP Address</label>
          <input v-model="form.ip" type="text" placeholder="100.93.192.114" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Location -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Location (City, State, Country)</label>
          <input v-model="form.location" type="text" placeholder="Rawlins, WY, USA" required
                 class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        </div>

        <!-- Toggles -->
        <fieldset class="border border-brand-muted p-4 rounded-lg mb-4">
          <legend class="px-2 text-sm font-semibold">Weather Options</legend>
          <div class="grid grid-cols-2 gap-2">
            <div v-for="opt in toggleOptions" :key="opt.key" class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.options[opt.key]" class="rounded text-brand-accent">
              <label class="text-sm">{{ opt.label }}</label>
            </div>
          </div>
        </fieldset>

        <!-- Display settings -->
        <fieldset class="border border-brand-muted p-4 rounded-lg mb-4">
          <legend class="px-2 text-sm font-semibold">Display Settings</legend>
          <div class="grid grid-cols-2 gap-4">
            <div v-for="sel in selectOptions" :key="sel.key">
              <label class="block text-sm font-medium">{{ sel.label }}</label>
              <input v-if="sel.type === 'number'" v-model.number="form.settings[sel.key]"
                     type="number" step="0.1" min="0.25" max="5"
                     class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text"/>
              <select v-else v-model="form.settings[sel.key]"
                      class="mt-1 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text">
                <option v-for="opt in sel.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>
          </div>

          <div class="flex items-center space-x-2 mt-3">
            <input type="checkbox" v-model="form.settings.kiosk" class="rounded text-brand-accent">
            <label class="text-sm">Kiosk Mode</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.autoplay" class="rounded text-brand-accent">
            <label class="text-sm">Autoplay Music</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.experimental" class="rounded text-brand-accent">
            <label class="text-sm">Experimental Features</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.hideWebamp" class="rounded text-brand-accent">
            <label class="text-sm">Hide Webamp</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.scanLines" class="rounded text-brand-accent">
            <label class="text-sm">Scan Lines</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.wide" class="rounded text-brand-accent">
            <label class="text-sm">Wide Mode</label>
          </div>
          <div class="flex items-center space-x-2 mt-2">
            <input type="checkbox" v-model="form.settings.autoRefresh" class="rounded text-brand-accent">
            <label class="text-sm">Auto Refresh</label>
          </div>
        </fieldset>

        <!-- Preview URL -->
        <div class="mb-4">
          <label class="block text-sm font-medium">Generated URL</label>
          <textarea readonly rows="4" :value="generatedUrl"
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
import axios from "axios"
import { useChannelsStore } from "../store/channels"

const store = useChannelsStore()


const API = import.meta.env.VITE_API_URL

const props = defineProps({ channel: Object })
const emit = defineEmits(["close", "saved"])

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
  { key: "marine-forecast", label: "Marine Forecast" },
  { key: "aqi-forecast", label: "Air Quality Forecast" },
]

const selectOptions = [
  { key: "windUnits", label: "Wind Units", options: [{ value: "1.00", label: "mph" }, { value: "2.00", label: "kph" }] },
  { key: "marineWindUnits", label: "Marine Wind Units", options: [{ value: "1.00", label: "knots" }, { value: "2.00", label: "mph" }] },
  { key: "marineWaveHeightUnits", label: "Marine Wave Height Units", options: [{ value: "1.00", label: "ft" }, { value: "2.00", label: "m" }] },
  { key: "temperatureUnits", label: "Temperature Units", options: [{ value: "1.00", label: "F" }, { value: "2.00", label: "C" }] },
  { key: "distanceUnits", label: "Distance Units", options: [{ value: "1.00", label: "miles" }, { value: "2.00", label: "km" }] },
  { key: "pressureUnits", label: "Pressure Units", options: [{ value: "1.00", label: "inHg" }, { value: "2.00", label: "hPa" }] },
  { key: "hoursFormat", label: "Hours Format", options: [{ value: "1.00", label: "12h" }, { value: "2.00", label: "24h" }] },
  { key: "speed", label: "Animation Speed", type: "number" },
]

const form = reactive({
  name: "Weather",
  channel_number: 1,
  ip: "100.93.192.114",
  location: "",
  options: {},
  settings: {
    windUnits: "2.00",
    marineWindUnits: "1.00",
    marineWaveHeightUnits: "1.00",
    temperatureUnits: "1.00",
    distanceUnits: "1.00",
    pressureUnits: "1.00",
    hoursFormat: "2.00",
    speed: 1.0,
    kiosk: false,
    autoplay: true,
    experimental: false,
    hideWebamp: false,
    scanLines: true,
    wide: true,
    autoRefresh: true,
  },
})

const generatedUrl = computed(() => {
  const base = `http://${form.ip}:9191/index.html?`
  const params = []

  for (const [key, val] of Object.entries(form.options)) {
    if (val) params.push(`${key}-checkbox=true`)
  }

  params.push(`settings-windUnits-select=${form.settings.windUnits}`)
  params.push(`settings-marineWindUnits-select=${form.settings.marineWindUnits}`)
  params.push(`settings-marineWaveHeightUnits-select=${form.settings.marineWaveHeightUnits}`)
  params.push(`settings-temperatureUnits-select=${form.settings.temperatureUnits}`)
  params.push(`settings-distanceUnits-select=${form.settings.distanceUnits}`)
  params.push(`settings-pressureUnits-select=${form.settings.pressureUnits}`)
  params.push(`settings-hoursFormat-select=${form.settings.hoursFormat}`)
  params.push(`settings-speed-select=${form.settings.speed.toFixed(2)}`)

  if (form.settings.kiosk) params.push("settings-kiosk-checkbox=true")
  if (form.settings.autoplay) params.push("settings-mediaPlaying-boolean=true")
  if (form.settings.experimental) params.push("settings-experimentalFeatures-checkbox=true")
  if (form.settings.hideWebamp) params.push("settings-hideWebamp-checkbox=true")
  if (form.settings.scanLines) params.push("settings-scanLines-checkbox=true")
  if (form.settings.wide) params.push("settings-wide-checkbox=true")
  if (form.settings.autoRefresh) params.push("chkAutoRefresh=true")

  if (form.location) {
    params.push(`latLonQuery=${encodeURIComponent(form.location)}`)
    params.push(`txtLocation=${encodeURIComponent(form.location)}`)
    params.push(`latLon=${encodeURIComponent(JSON.stringify({ lat: 41.7884, lon: -107.2364 }))}`)
  }

  return base + params.join("&")
})

onMounted(() => {
  if (props.channel?.config) {
    const cfg = props.channel.config
    form.name = cfg.network_name || props.channel.name || "Weather"
    form.channel_number = cfg.channel_number || 1
    form.ip = cfg.ip || "100.93.192.114"
    form.location = cfg.location || ""
    form.options = { ...cfg.options }
    form.settings = { ...form.settings, ...cfg.settings }
  }
})

const save = async () => {
  const conf = {
    network_name: form.name,                  // <- not form.network_name
    channel_number: form.channel_number,
    network_type: "web",                      // backend expects "web"
    web_url: generatedUrl.value               // <- use computed url
  }

  if (props.channel) {
    await store.updateChannel(props.channel.name, conf)
  } else {
    await store.addChannel(conf)
  }

  emit("saved")
  emit("close")
}

</script>
