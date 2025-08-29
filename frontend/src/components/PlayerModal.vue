<!-- src/components/PlayerModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface rounded-lg p-4 w-full max-w-3xl shadow-lg">
      <!-- Header -->
      <div class="flex justify-between items-center mb-3">
        <h3 class="text-lg font-semibold">📺 FieldStation42 TV</h3>
        <button @click="$emit('close')" class="text-red-400 hover:text-red-600">✖</button>
      </div>

      <!-- Video -->
      <div class="aspect-video bg-black mb-4 flex items-center justify-center">
        <video
          id="webrtc-player"
          autoplay
          playsinline
          muted
          controls
          class="w-full h-full rounded"
        ></video>
      </div>

      <!-- Channel Controls -->
      <div class="flex justify-center items-center space-x-4">
        <button
          @click="channelDown"
          class="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
        >
          ⬅️ Down
        </button>

        <input
          v-model.number="directChannel"
          type="number"
          min="1"
          class="w-16 p-1 text-center rounded bg-brand-bg border border-brand-muted text-brand-text"
        />

        <button
          @click="tuneDirect"
          class="px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded"
        >
          Go
        </button>

        <button
          @click="channelUp"
          class="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
        >
          ➡️ Up
        </button>
      </div>

      <!-- Status -->
      <div class="mt-4 text-center text-sm text-brand-text">
        Current channel: {{ directChannel }}
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"

// Props
const props = defineProps({
  startChannel: { type: Number, default: 1 }
})

const directChannel = ref(props.startChannel)
const API = "http://127.0.0.1:4343"

// ✅ Correct WHEP URL with trailing slash
const STREAM_URL = "http://100.93.192.114:8889/whep/mystream/"

// Attach WebRTC to <video>
const attachWebRTC = async () => {
  const videoEl = document.getElementById("webrtc-player")
  if (!videoEl) return

  try {
    const pc = new RTCPeerConnection()
    pc.ontrack = (event) => {
      videoEl.srcObject = event.streams[0]
    }

    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    const res = await fetch(STREAM_URL, {
      method: "POST",
      body: offer.sdp,
      headers: { "Content-Type": "application/sdp" }
    })

    const answer = {
      type: "answer",
      sdp: await res.text()
    }
    await pc.setRemoteDescription(answer)
  } catch (err) {
    console.error("WebRTC attach failed:", err)
  }
}

// === API calls for channel control ===
const fetchCurrent = async () => {
  try {
    const res = await axios.get(`${API}/player/channels/current`)
    if (res.data.channel_number) {
      directChannel.value = res.data.channel_number
    }
  } catch (err) {
    console.error("Failed to fetch current channel:", err)
  }
}

const tuneChannel = async (num) => {
  try {
    await axios.get(`${API}/player/channels/${num}`)
    directChannel.value = num
  } catch (err) {
    console.error(`Failed to tune channel ${num}:`, err)
  }
}

const channelUp = async () => {
  try {
    await axios.get(`${API}/player/channels/up`)
    await fetchCurrent()
  } catch (err) {
    console.error("Channel Up failed:", err)
  }
}

const channelDown = async () => {
  try {
    await axios.get(`${API}/player/channels/down`)
    await fetchCurrent()
  } catch (err) {
    console.error("Channel Down failed:", err)
  }
}

const tuneDirect = async () => {
  if (directChannel.value > 0) {
    await tuneChannel(directChannel.value)
  }
}

// Auto-tune + attach WebRTC when modal opens
onMounted(async () => {
  if (props.startChannel > 0) {
    await tuneChannel(props.startChannel)
  } else {
    await fetchCurrent()
  }
  await attachWebRTC()
})
</script>
