<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-5xl shadow-xl overflow-y-auto max-h-[90vh]">
      <h3 class="text-xl font-semibold mb-4">
        {{ channel ? "Edit Guide Channel" : "Create Guide Channel" }}
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
          </div>
        </fieldset>

        <!-- Appearance -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Appearance</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <input type="checkbox" v-model="form.station_conf.fullscreen" id="fullscreen" />
              <label for="fullscreen" class="text-sm">Fullscreen</label>
            </div>
            <div>
              <input type="checkbox" v-model="form.station_conf.window_decorations" id="windowDeco" />
              <label for="windowDeco" class="text-sm">Window Decorations</label>
            </div>
            <div>
              <label class="block text-sm">Width</label>
              <input type="number" v-model.number="form.station_conf.width"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
              <label class="block text-sm">Height</label>
              <input type="number" v-model.number="form.station_conf.height"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
              <label class="block text-sm">Top Background</label>
              <select v-model="form.station_conf.top_bg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Bottom Background</label>
              <select v-model="form.station_conf.bottom_bg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Fonts -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Fonts</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm">Message Font</label>
              <select v-model="form.station_conf.message_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Network Font</label>
              <select v-model="form.station_conf.network_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Font</label>
              <select v-model="form.station_conf.schedule_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Messages -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Messages</legend>
          <div v-for="(msg, i) in form.station_conf.messages" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.station_conf.messages[i]" type="text" placeholder="Add message"
                   class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="form.station_conf.messages.splice(i,1)"
                    class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.station_conf.messages.push('')"
                  class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Message</button>
        </fieldset>

        <!-- Images -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Images</legend>
          <div v-for="(img, i) in form.station_conf.images" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.station_conf.images[i]" type="text"
                   class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" readonly />
            <button type="button" @click="form.station_conf.images.splice(i,1)"
                    class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.station_conf.images.push('')"
                  class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Image</button>
        </fieldset>

        <!-- Footer -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Footer</legend>
          <div v-for="(msg, i) in form.station_conf.footer_messages" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.station_conf.footer_messages[i]" type="text" placeholder="Add message"
                   class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="form.station_conf.footer_messages.splice(i,1)"
                    class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.station_conf.footer_messages.push('')"
                  class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Footer</button>
        </fieldset>

        <!-- Colors -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Colors</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm">Message Text Color</label>
              <select v-model="form.station_conf.message_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Text Color</label>
              <select v-model="form.station_conf.schedule_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Highlight Color</label>
              <select v-model="form.station_conf.schedule_highlight_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Background Sound -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Sound</legend>
          <div class="flex space-x-2">
            <input v-model="form.station_conf.sound_to_play" type="text"
                   class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <input type="file" ref="soundInput" class="hidden" @change="onSoundSelect" />
            <button type="button" @click="triggerSoundUpload"
                    class="px-3 py-1 bg-brand-accent text-white rounded">+ File</button>
          </div>
        </fieldset>

        <!-- Options -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Options</legend>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm">Rotation Rate (seconds)</label>
              <input v-model.number="form.station_conf.message_rotation_rate" type="number" min="1"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
              <label class="block text-sm">Padding</label>
              <input v-model.number="form.station_conf.pad" type="number" min="0"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
              <label class="block text-sm">Message Font Size</label>
              <input v-model.number="form.station_conf.message_font_size" type="number" min="6"
                     class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
          </div>
          <div class="flex items-center space-x-2 mt-4">
            <input type="checkbox" v-model="form.station_conf.normalize_title" />
            <label class="text-sm">Normalize Titles</label>
          </div>
        </fieldset>

        <!-- Save -->
        <div class="flex justify-end space-x-2">
          <button type="button" @click="$emit('close')" class="px-4 py-2 bg-gray-600 rounded text-white hover:bg-gray-500">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-green-700 rounded text-white hover:bg-green-600">Save Guide</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from "vue"
import axios from "axios"
import { useChannelsStore } from "../store/channels"

const props = defineProps({ channel: Object })
const emit = defineEmits(["close", "saved"])
const store = useChannelsStore()

const API = import.meta.env.VITE_API_URL

const fonts = ref([])
const colors = ["white","black","gray","yellow","red","green","blue1","blue2","blue3","blue4","purple"]

const soundInput = ref(null)
const form = reactive({ station_conf: {} })

// Load system fonts
const loadFonts = async () => {
  try {
    const res = await axios.get(`${API}/fonts`)
    fonts.value = res.data.fonts || []
  } catch (err) {
    console.error("Failed to fetch fonts", err)
    fonts.value = ["Arial","Courier","Times New Roman","Verdana","Tahoma","Georgia"]
  }
}

onMounted(async () => {
  if (props.channel?.config) {
    form.station_conf = JSON.parse(JSON.stringify(props.channel.config))
  } else {
    try {
      const res = await axios.get(`${API}/channels/baseline/guide`)
      form.station_conf = res.data.station_conf
    } catch (err) {
      console.error("Failed to fetch guide baseline:", err)
    }
  }
  loadFonts()
})

const triggerSoundUpload = () => soundInput.value?.click()
const onSoundSelect = (e) => {
  const file = e.target.files[0]
  if (file) form.station_conf.sound_to_play = `runtime/guide/${file.name}`
}

const save = async () => {
  const payload = form.station_conf   // << not wrapped
  if (props.channel) {
    await store.updateChannel(props.channel.name, payload)
  } else {
    await store.addChannel(payload)
  }
  emit("saved")
  emit("close")
}

</script>
