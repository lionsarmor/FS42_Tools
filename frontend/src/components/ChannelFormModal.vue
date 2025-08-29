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

        <!-- Standard Channel -->
        <div v-if="form.station_conf.network_type === 'standard'" class="space-y-4">
          <fieldset class="border border-brand-muted p-4 rounded-lg">
            <legend class="px-2 text-lg font-semibold">Standard Channel Options</legend>

            <div>
              <label class="block text-sm mb-1">Tags (comma separated)</label>
              <input v-model="tagsInput" type="text"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>

            <!-- Commercial Free -->
            <div class="flex items-center space-x-2">
              <input id="commercialFree" type="checkbox"
                     v-model="form.station_conf.commercial_free"
                     class="h-4 w-4 text-brand-accent border-brand-muted rounded" />
              <label for="commercialFree" class="text-sm font-medium">Commercial Free</label>
            </div>

            <div>
              <label class="block text-sm">Break Strategy</label>
              <select v-model="form.station_conf.break_strategy"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option value="standard">Standard</option>
                <option value="end">End</option>
                <option value="center">Center</option>
              </select>
            </div>

            <div>
              <label class="block text-sm">Schedule Increment</label>
              <select v-model.number="form.station_conf.schedule_increment"
                      class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option :value="0">0 (No breaks)</option>
                <option :value="5">5 minutes</option>
                <option :value="10">10 minutes</option>
                <option :value="15">15 minutes</option>
                <option :value="30">30 minutes (default)</option>
                <option :value="60">60 minutes</option>
              </select>
            </div>

            <!-- File Pickers -->
            <div>
              <label class="block text-sm">Off-Air Video</label>
              <input v-model="form.station_conf.off_air_path" type="text" readonly
                     class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
              <input type="file" ref="offAirInput" class="hidden" accept="video/*"
                     @change="onFileSelect($event, 'off_air_path')" />
              <button type="button" @click="triggerFileInput('offAirInput')"
                      class="px-2 py-1 bg-brand-accent text-white rounded">+ File</button>
            </div>

            <div>
              <label class="block text-sm">Sign-Off Video</label>
              <input v-model="form.station_conf.signoff_path" type="text" readonly
                     class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
              <input type="file" ref="signoffInput" class="hidden" accept="video/*"
                     @change="onFileSelect($event, 'signoff_path')" />
              <button type="button" @click="triggerFileInput('signoffInput')"
                      class="px-2 py-1 bg-brand-accent text-white rounded">+ File</button>
            </div>

            <div>
              <label class="block text-sm">Standby Image</label>
              <input v-model="form.station_conf.standby_image" type="text" readonly
                     class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
              <input type="file" ref="standbyInput" class="hidden" accept="image/*"
                     @change="onFileSelect($event, 'standby_image')" />
              <button type="button" @click="triggerFileInput('standbyInput')"
                      class="px-2 py-1 bg-brand-accent text-white rounded">+ File</button>
            </div>

            <div>
              <label class="block text-sm">Be Right Back Media</label>
              <input v-model="form.station_conf.be_right_back_media" type="text" readonly
                     class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
              <input type="file" ref="brbInput" class="hidden" accept="video/*,image/*"
                     @change="onFileSelect($event, 'be_right_back_media')" />
              <button type="button" @click="triggerFileInput('brbInput')"
                      class="px-2 py-1 bg-brand-accent text-white rounded">+ File</button>
            </div>
          </fieldset>
        </div>

        <!-- Save -->
        <div class="flex justify-end space-x-2">
          <button type="button" @click="$emit('close')"
                  class="px-4 py-2 bg-gray-600 rounded text-white hover:bg-gray-500">Cancel</button>
          <button type="submit"
                  class="px-4 py-2 bg-green-700 rounded text-white hover:bg-green-600">Save</button>
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
    off_air_path: "runtime/off_air_pattern.mp4",
    signoff_path: "runtime/signoff.mp4",
    standby_image: "runtime/standby.png",
    be_right_back_media: "runtime/brb.png",
    video_scramble_fx: "",
    panscan: 1.0,
    video_keepaspect: true,
    station_fx: ""
  }
})

const tagsInput = computed({
  get: () => form.station_conf.tags?.join(", ") || "",
  set: (val) => {
    form.station_conf.tags = val.split(",").map(t => t.trim()).filter(Boolean)
  }
})

// === File pickers ===
const offAirInput = ref(null)
const signoffInput = ref(null)
const standbyInput = ref(null)
const brbInput = ref(null)

const triggerFileInput = (refName) => {
  if (refName === "offAirInput") offAirInput.value.click()
  if (refName === "signoffInput") signoffInput.value.click()
  if (refName === "standbyInput") standbyInput.value.click()
  if (refName === "brbInput") brbInput.value.click()
}

const onFileSelect = (e, field) => {
  const file = e.target.files[0]
  if (file) {
    form.station_conf[field] = `runtime/${file.name}`
  }
}

// === Watch props ===
watch(() => props.channel, (ch) => {
  if (ch) {
    // clone channel into form
    form.station_conf = JSON.parse(JSON.stringify(ch.config || ch.station_conf))
  } else {
    form.station_conf = {
      network_name: "",
      channel_number: 1,
      network_type: "standard",
      tags: [],
      tag_colors: {}
    }
  }
}, { immediate: true })

const save = async () => {
  try {
    if (props.channel) {
      await store.updateChannel(props.channel.name, form.station_conf)
    } else {
      await store.addChannel(form.station_conf)
    }
    emit("saved")
    emit("close")
  } catch (err) {
    alert("Save failed: " + err.message)
  }
}
</script>
