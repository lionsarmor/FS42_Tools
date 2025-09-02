<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface rounded-lg p-4 w-full max-w-4xl shadow-lg">
      <!-- Header -->
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-semibold">📺 FieldStation42 TV</h3>
        <button @click="$emit('close')" class="text-red-400 hover:text-red-600">✖</button>
      </div>

      <!-- MediaMTX Player -->
      <div class="aspect-video bg-black mb-4">
        <iframe
          src="http://100.93.192.114:8889/mystream"
          class="w-full h-full rounded"
          allow="autoplay; fullscreen"
        ></iframe>
      </div>

      <!-- Channel Controls -->
      <div class="flex justify-center items-center space-x-4 mt-4">
        <button @click="channelDown" class="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded">⬅️ Down</button>
        <input v-model.number="directChannel" type="number" min="1"
               class="w-16 p-1 text-center rounded bg-brand-bg border border-brand-muted text-brand-text"/>
        <button @click="tuneDirect" class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded">Go</button>
        <button @click="channelUp" class="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded">➡️ Up</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"

const props = defineProps({
  startChannel: { type: Number, default: 1 }
})

const directChannel = ref(props.startChannel)

const API = "http://127.0.0.1:4343"

const fetchCurrent = async () => {
  try {
    const res = await axios.get(`${API}/player/channels/current`)
    if (res.data.channel_number) {
      directChannel.value = res.data.channel_number
    }
  } catch {}
}

const tuneChannel = async (num) => {
  try {
    await axios.get(`${API}/player/channels/${num}`)
    directChannel.value = num
  } catch {}
}

const channelUp = async () => { await axios.get(`${API}/player/channels/up`); await fetchCurrent() }
const channelDown = async () => { await axios.get(`${API}/player/channels/down`); await fetchCurrent() }
const tuneDirect = async () => { if (directChannel.value > 0) await tuneChannel(directChannel.value) }

onMounted(async () => {
  if (props.startChannel > 0) await tuneChannel(props.startChannel)
  else await fetchCurrent()
})
</script>
