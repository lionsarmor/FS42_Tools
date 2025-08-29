<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-5xl shadow-xl overflow-y-auto max-h-[90vh]">
      <h3 class="text-xl font-semibold mb-4">Create Guide Channel</h3>

      <form @submit.prevent="save" class="space-y-6">

        <!-- General -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">General</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm mb-1">Channel Name</label>
              <input v-model="form.station_conf.network_name" type="text" class="w-full p-2 rounded bg-brand-bg border border-brand-muted" required />
            </div>
            <div>
              <label class="block text-sm mb-1">Channel Number</label>
              <input v-model.number="form.station_conf.channel_number" type="number" min="1" class="w-full p-2 rounded bg-brand-bg border border-brand-muted" required />
            </div>
          </div>
        </fieldset>

        <!-- Appearance -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Appearance</legend>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-sm">Fullscreen</label><input type="checkbox" v-model="form.fullscreen" /></div>
            <div><label class="block text-sm">Window Decorations</label><input type="checkbox" v-model="form.window_decorations" /></div>
            <div><label class="block text-sm">Width</label><input type="number" v-model.number="form.width" class="w-full p-2 rounded bg-brand-bg border border-brand-muted" /></div>
            <div><label class="block text-sm">Height</label><input type="number" v-model.number="form.height" class="w-full p-2 rounded bg-brand-bg border border-brand-muted" /></div>

            <div>
              <label class="block text-sm">Top Background</label>
              <select v-model="form.top_bg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Bottom Background</label>
              <select v-model="form.bottom_bg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
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
              <select v-model="form.message_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Network Font</label>
              <select v-model="form.network_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Font</label>
              <select v-model="form.schedule_font_family" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Messages -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Messages</legend>
          <div v-for="(msg, i) in form.messages" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.messages[i]" type="text" placeholder="Add message" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="form.messages.splice(i,1)" class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.messages.push('')" class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Message</button>
        </fieldset>

        <!-- Images -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
        <legend class="px-2 text-lg font-semibold">Images</legend>

        <div v-for="(img, i) in form.images" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.images[i]" type="text" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" readonly />
            <button type="button" @click="removeImage(i)" class="px-2 bg-brand-danger text-white rounded">✕</button>
        </div>

        <button type="button" @click="triggerImageUpload" class="px-3 py-1 bg-brand-accent text-white rounded">
            + Add Image
        </button>
        <input type="file" ref="imageInput" class="hidden" accept="image/*" multiple @change="onImageSelect" />
        </fieldset>

        <!-- Footer -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Footer</legend>
          <div v-for="(msg, i) in form.footer_messages" :key="i" class="flex space-x-2 mb-2">
            <input v-model="form.footer_messages[i]" type="text" placeholder="Add message" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="form.footer_messages.splice(i,1)" class="px-2 bg-brand-danger text-white rounded">✕</button>
          </div>
          <button type="button" @click="form.footer_messages.push('')" class="px-3 py-1 bg-brand-accent text-white rounded">+ Add Footer</button>
        </fieldset>

        <!-- Colors -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Colors</legend>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm">Message Text Color</label>
              <select v-model="form.message_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Text Color</label>
              <select v-model="form.schedule_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm">Schedule Highlight Color</label>
              <select v-model="form.schedule_highlight_fg" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option v-for="c in colors" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
        </fieldset>

        <!-- Background Sound -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
          <legend class="px-2 text-lg font-semibold">Sound</legend>
          <div class="flex space-x-2">
            <input v-model="form.sound_to_play" type="text" class="flex-1 p-2 rounded bg-brand-bg border border-brand-muted" />
            <button type="button" @click="triggerSoundUpload" class="px-3 py-1 bg-brand-accent text-white rounded">+ File</button>
            <input type="file" ref="soundInput" class="hidden" @change="onSoundSelect" />
          </div>
        </fieldset>

                <!-- Message Options -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
        <legend class="px-2 text-lg font-semibold">Message Options</legend>
        <div class="grid grid-cols-3 gap-4">
            <div>
            <label class="block text-sm">Rotation Rate (seconds)</label>
            <input v-model.number="form.message_rotation_rate" type="number" min="1"
                class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
            <label class="block text-sm">Padding</label>
            <input v-model.number="form.pad" type="number" min="0"
                class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
            <label class="block text-sm">Message Font Size</label>
            <input v-model.number="form.message_font_size" type="number" min="6"
                class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
        </div>
        </fieldset>

        <!-- Schedule Options -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
        <legend class="px-2 text-lg font-semibold">Schedule Options</legend>
        <div class="grid grid-cols-3 gap-4">
            <div>
            <label class="block text-sm">Rows to Show</label>
            <input v-model.number="form.schedule_row_count" type="number" min="1"
                class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
            <label class="block text-sm">Border Width</label>
            <input v-model.number="form.schedule_border_width" type="number" min="0"
                class="w-full p-2 rounded bg-brand-bg border border-brand-muted" />
            </div>
            <div>
            <label class="block text-sm">Border Style</label>
            <select v-model="form.schedule_border_relief" class="w-full p-2 rounded bg-brand-bg border border-brand-muted">
                <option value="flat">Flat</option>
                <option value="raised">Raised</option>
                <option value="sunken">Sunken</option>
                <option value="ridge">Ridge</option>
                <option value="groove">Groove</option>
            </select>
            </div>
        </div>
        </fieldset>

        <!-- General Toggles -->
        <fieldset class="border border-brand-muted p-4 rounded-lg">
        <legend class="px-2 text-lg font-semibold">Other</legend>
        <div class="flex items-center space-x-2">
            <input type="checkbox" v-model="form.normalize_title" />
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
import { ref, onMounted } from "vue"
import axios from "axios"

const emit = defineEmits(["close", "saved"])

const colors = ["white","black","gray","yellow","red","green","blue1","blue2","blue3","blue4","purple"]
const fonts = ref([])

const soundInput = ref(null)

const form = ref({
  station_conf: {
    network_name: "Guide",
    network_type: "guide",
    channel_number: 3,
    runtime_dir: "runtime/guide",
    play_sound: false
  },
  fullscreen: false,
  width: 720,
  height: 480,
  window_decorations: false,
  top_bg: "blue3",
  bottom_bg: "blue4",
  pad: 10,
  messages: [],
  message_rotation_rate: 10,
  message_fg: "white",
  message_font_family: "Arial",
  message_font_size: 25,
  images: [],
  network_font_family: "Arial",
  network_font_size: 12,
  schedule_font_family: "Arial",
  schedule_font_size: 12,
  schedule_highlight_fg: "yellow",
  schedule_fg: "white",
  schedule_border_width: 4,
  schedule_border_relief: "raised",
  footer_messages: [],
  footer_height: 50,
  schedule_row_count: 3,
  normalize_title: true,
  sound_to_play: "",
  message_rotation_rate: 10,
    pad: 10,
    message_font_size: 25,
    schedule_row_count: 3,
    schedule_border_width: 4,
    schedule_border_relief: "raised",
    normalize_title: true,
    })

onMounted(async () => {
  try {
    const res = await axios.get("http://127.0.0.1:4343/fonts")
    fonts.value = res.data.fonts || ["Arial","Courier","Times New Roman"]
  } catch {
    fonts.value = ["Arial","Courier","Times New Roman"]
  }
})

const triggerSoundUpload = () => soundInput.value.click()
const onSoundSelect = (e) => {
  const file = e.target.files[0]
  if (file) form.value.sound_to_play = file.name
}

const save = async () => {
  try {
    await axios.post("http://127.0.0.1:4343/channels/save", {
      name: form.value.station_conf.network_name,
      config: form.value,
    })
    emit("saved")
    emit("close")
  } catch (err) {
    alert("Save failed: " + err.message)
  }
}


const imageInput = ref(null)

const triggerImageUpload = () => {
  imageInput.value.click()
}

const onImageSelect = (e) => {
  const files = Array.from(e.target.files)
  files.forEach(file => {
    form.value.images.push(file.name)
  })
}

const removeImage = (index) => {
  form.value.images.splice(index, 1)
}

</script>
