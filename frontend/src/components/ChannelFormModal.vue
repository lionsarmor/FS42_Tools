<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-5xl shadow-xl overflow-y-auto max-h-[90vh]">
      <h3 class="text-xl font-semibold mb-4">
        {{ channel ? "Edit Channel" : "Add Channel" }}
      </h3>

      <form @submit.prevent="save" class="space-y-6">
        <!-- General -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">General</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1">Channel Name</label>
              <input v-model="form.station_conf.network_name" type="text"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" required />
            </div>
            <div>
              <label class="block text-sm mb-1">Channel Number</label>
              <input v-model.number="form.station_conf.channel_number" type="number" min="1"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" required />
            </div>
            <div>
              <label class="block text-sm mb-1">Network Type</label>
              <select v-model="form.station_conf.network_type"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option value="standard">Standard</option>
                <option value="loop">Loop</option>
                <option value="streaming">Streaming</option>
                <option value="web">Web</option>
                <option value="diagnostic">Diagnostic</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Standard Channel Options -->
        <div v-if="form.station_conf.network_type === 'standard'" class="space-y-4">
          <fieldset class="border border-brand-muted p-4 rounded-lg">
            <legend class="px-2 text-lg font-semibold">Standard Channel</legend>

            <!-- Tags -->
            <div>
              <label class="block text-sm mb-1">Tags (comma separated)</label>
              <input v-model="tagsInput" type="text"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>

            <!-- Commercial Free -->
            <div class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.station_conf.commercial_free" id="commercialFree" />
              <label for="commercialFree" class="text-sm">Commercial Free</label>
            </div>

            <!-- Break Strategy -->
            <div>
              <label class="block text-sm">Break Strategy</label>
              <select v-model="form.station_conf.break_strategy"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option value="standard">Standard</option>
                <option value="end">End</option>
                <option value="center">Center</option>
              </select>
            </div>

            <!-- Schedule Increment -->
            <div>
              <label class="block text-sm">Schedule Increment</label>
              <select v-model.number="form.station_conf.schedule_increment"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option :value="0">0</option>
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="15">15</option>
                <option :value="30">30</option>
                <option :value="60">60</option>
              </select>
            </div>

            <!-- Runtime Files -->
            <div v-for="field in fileFields" :key="field.key">
              <label class="block text-sm">{{ field.label }}</label>
              <div class="flex space-x-2">
                <select v-model="form.station_conf[field.key]"
                        class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted">
                  <option v-for="file in runtimeFiles[field.key]" :key="file" :value="`runtime/${file}`">
                    runtime/{{ file }}
                  </option>
                </select>
                <input
                  type="file"
                  :ref="el => fileInputs[field.key] = el"
                  class="hidden"
                  :accept="field.accept"
                  @change="onFileSelect($event, field.key)"
                />
                <button type="button" @click="triggerFileInput(field.key)"
                        class="px-2 py-1 bg-brand-accent text-white rounded">+ Upload</button>
              </div>
            </div>

            <!-- Scramble FX -->
            <div>
              <label class="block text-sm">Video Scramble FX</label>
              <select v-model="form.station_conf.video_scramble_fx"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option value="">None</option>
                <option v-for="fx in scrambleFxOptions" :key="fx" :value="fx">{{ fx }}</option>
              </select>
            </div>

            <!-- Station FX -->
            <div>
              <label class="block text-sm">Station FX</label>
              <input v-model="form.station_conf.station_fx" type="text"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>

            <!-- Panscan -->
            <div>
              <label class="block text-sm">Panscan</label>
              <input v-model.number="form.station_conf.panscan" type="number" step="0.1" min="0" max="2"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>

            <!-- Keep Aspect -->
            <div class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.station_conf.video_keepaspect" id="keepAspect" />
              <label for="keepAspect" class="text-sm">Keep Aspect Ratio</label>
            </div>

            <!-- Clip Shows -->
            <div>
              <label class="block text-sm mb-2">Clip Shows</label>
              <div v-for="(clip, i) in form.station_conf.clip_shows" :key="i" class="flex space-x-2 mb-2">
                <input v-model="clip.tags" placeholder="Tag folder" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
                <input v-model.number="clip.duration" type="number" min="5" placeholder="Minutes"
                       class="w-24 p-2 rounded bg-brand-bg border border-brand-muted" />
                <button type="button" @click="form.station_conf.clip_shows.splice(i,1)"
                        class="px-2 bg-brand-danger text-white rounded">✕</button>
              </div>
              <button type="button" @click="form.station_conf.clip_shows.push({tags:'',duration:60})"
                      class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Clip Show</button>
            </div>

            <!-- Special Subfolders -->
            <fieldset class="border border-brand-muted p-4 rounded-lg">
              <legend class="px-2 text-lg font-semibold">Special Subfolders</legend>
              <div v-for="(sf, i) in specialSubfolders" :key="i" class="flex space-x-2 mb-2">
                <select v-model="sf.type" class="p-2 rounded bg-brand-bg border border-brand-muted">
                  <option value="month">Month</option>
                  <option value="quarter">Quarter</option>
                  <option value="time">Time</option>
                  <option value="bump">Bump</option>
                  <option value="custom">Custom</option>
                </select>
                <input v-model="sf.value" placeholder="Value"
                       class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
                <button type="button" @click="specialSubfolders.splice(i,1)"
                        class="px-2 bg-brand-danger text-white rounded">✕</button>
              </div>
              <button type="button" @click="specialSubfolders.push({type:'month',value:''})"
                      class="px-3 py-1 bg-brand-accent text-white rounded">+ Add</button>
            </fieldset>
          </fieldset>
        </div>

        <!-- Loop -->
        <fieldset v-if="form.station_conf.network_type === 'loop'" class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Loop Channel</legend>
          <div class="flex items-center space-x-2">
            <input type="checkbox" v-model="form.station_conf.loop_shuffle" id="shuffle" />
            <label for="shuffle" class="text-sm">Shuffle Playback</label>
          </div>
        </fieldset>

        <!-- Streaming -->
        <fieldset v-if="form.station_conf.network_type === 'streaming'" class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Streaming Channel</legend>
          <div v-for="(url, i) in form.station_conf.streams" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.station_conf.streams[i]" type="text"
                   placeholder="Stream URL" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="form.station_conf.streams.splice(i,1)"
                    class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.station_conf.streams.push('')"
                  class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Stream</button>
        </fieldset>

        <!-- Web -->
        <fieldset v-if="form.station_conf.network_type === 'web' || form.station_conf.network_type === 'diagnostic'" class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Web Channel</legend>
          <div>
            <label class="block text-sm">Web URL</label>
            <input v-model="form.station_conf.web_url" type="text"
                   class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
          </div>
          <div class="grid grid-cols-2 gap-4 mt-2">
            <div class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.station_conf.fullscreen" id="fullscreen" />
              <label for="fullscreen" class="text-sm">Fullscreen</label>
            </div>
            <div class="flex items-center space-x-2">
              <input type="checkbox" v-model="form.station_conf.window_decorations" id="windowDeco" />
              <label for="windowDeco" class="text-sm">Window Decorations</label>
            </div>
            <div>
              <label class="block text-sm">Width</label>
              <input v-model.number="form.station_conf.width" type="number"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
              <label class="block text-sm">Height</label>
              <input v-model.number="form.station_conf.height" type="number"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
          </div>
        </fieldset>

        <!-- Save -->
        <div class="flex justify-end space-x-2">
          <button type="button" @click="$emit('close')"
                  class="px-4 py-2 bg-gray-600 rounded text-white">Cancel</button>
          <button type="submit"
                  class="px-4 py-2 bg-green-700 rounded text-white">Save</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch, onMounted } from "vue"
import axios from "axios"
import { useChannelsStore } from "../store/channels"

const props = defineProps({ channel: Object })
const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

// Runtime file lists populated from backend
const runtimeFiles = reactive({
  off_air_video: [],
  sign_off_video: [],
  standby_image: [],
  be_right_back_media: []
})

// Hidden file input refs
const fileInputs = reactive({})
const fileFields = [
  { key: "off_air_video", label: "Off-Air Video", accept: "video/*" },
  { key: "sign_off_video", label: "Sign-Off Video", accept: "video/*" },
  { key: "standby_image", label: "Standby Image", accept: "image/*" },
  { key: "be_right_back_media", label: "Be Right Back", accept: "video/*,image/*" }
]

// Default form structure
const form = reactive({
  station_conf: {
    network_name: "",
    channel_number: 1,
    network_type: "standard",
    tags: [],
    tag_colors: {},
    break_strategy: "standard",
    schedule_increment: 30,
    commercial_free: false,
    // --- runtime defaults ---
    off_air_video: "runtime/off_air_pattern.mp4",
    sign_off_video: "runtime/signoff.mp4",
    standby_image: "runtime/standby.png",
    be_right_back_media: "runtime/brb.png",
    // --- visual FX / playback ---
    video_scramble_fx: "",
    station_fx: "",
    panscan: 1.0,
    video_keepaspect: true,
    // --- content ---
    clip_shows: [],
    streams: [],
    // --- web / loop ---
    web_url: "",
    fullscreen: false,
    window_decorations: false,
    width: 720,
    height: 480,
    loop_shuffle: true
  }
})

// Scramble FX options
const scrambleFxOptions = [
  "horizontal_line","diagonal_lines","static_overlay","pixel_block","color_inversion",
  "severe_noise","wavy","random_block","chunky_scramble"
]

// Special subfolders
const specialSubfolders = reactive([])

// Tags field (comma-separated)
const tagsInput = computed({
  get: () => form.station_conf.tags?.join(", ") || "",
  set: (val) => {
    form.station_conf.tags = val.split(",").map(t => t.trim()).filter(Boolean)
  }
})

// Load available runtime files from backend
const loadRuntimeFiles = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:4343/api/runtime-files")
    Object.assign(runtimeFiles, res.data)
  } catch (err) {
    console.error("Failed to load runtime files", err)
  }
}

// Trigger file picker for uploads
const triggerFileInput = (key) => {
  const el = fileInputs[key]
  if (el && typeof el.click === "function") el.click()
}

// Update field when file is selected
const onFileSelect = (e, field) => {
  const file = e.target.files[0]
  if (file) form.station_conf[field] = `runtime/${file.name}`
}

// Watch channel prop and sync into form
watch(() => props.channel, (ch) => {
  if (ch) {
    const conf = JSON.parse(JSON.stringify(ch.config || ch.station_conf))

    // --- enforce baseline keys always exist ---
    conf.off_air_video       = conf.off_air_video       || "runtime/off_air_pattern.mp4"
    conf.sign_off_video      = conf.sign_off_video      || "runtime/signoff.mp4"
    conf.standby_image       = conf.standby_image       || "runtime/standby.png"
    conf.be_right_back_media = conf.be_right_back_media || "runtime/brb.png"

    form.station_conf = conf
  }
}, { immediate: true })

// Save channel
const save = async () => {
  form.station_conf.special_subfolders = specialSubfolders

  // Ensure runtime fields are always present before saving
  fileFields.forEach(f => {
    if (!form.station_conf[f.key]) {
      form.station_conf[f.key] = `runtime/${runtimeFiles[f.key][0] || ""}`
    }
  })

  if (props.channel) {
    await store.updateChannel(props.channel.name, form.station_conf)
  } else {
    await store.addChannel(form.station_conf)
  }
  emit("saved")
  emit("close")
}

onMounted(loadRuntimeFiles)
</script>
