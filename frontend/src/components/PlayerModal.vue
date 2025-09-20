<template>
  <div class="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
    <div class="relative bg-black rounded-2xl shadow-2xl border border-gray-700/50 w-[900px] max-w-[95%] h-[600px] max-h-[90%] overflow-hidden">
      
      <!-- Header -->
      <div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/90 via-black/50 to-transparent p-3 flex justify-between items-center">
        <div class="flex items-center space-x-3 text-white">
          <span class="bg-black/70 px-3 py-1 rounded border border-cyan-400/30 text-cyan-400 font-mono text-lg">
            {{ String(directChannel).padStart(2, '0') }}
          </span>
          <h2 class="text-lg font-bold">📺 Tsar TV</h2>
        </div>
        <button @click="$emit('close')" class="w-8 h-8 flex items-center justify-center bg-red-600 hover:bg-red-500 rounded-full text-white">
          ✕
        </button>
      </div>

      <!-- Main Video -->
      <div class="w-full h-full flex items-center justify-center bg-black">
        <video
          ref="tvVideo"
          class="w-full h-full object-contain"
          autoplay
          muted
          playsinline
          controls
        ></video>
      </div>

      <!-- Controls -->
      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/70 to-transparent p-4">
        <div class="flex justify-center space-x-4">
          <button @click="channelDown" class="px-3 py-2 bg-blue-600 text-white rounded">⬅</button>
          <input v-model.number="directChannel" type="number" min="1" max="999" class="w-16 text-center bg-gray-800 text-cyan-400 rounded" />
          <button @click="tuneDirect" class="px-3 py-2 bg-green-600 text-white rounded">TUNE</button>
          <button @click="channelUp" class="px-3 py-2 bg-blue-600 text-white rounded">➡</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted, nextTick } from "vue"

const props = defineProps({
  startChannel: { type: Number, default: 1 },
  streamUrl: { type: String, default: "https://cable.radroddy.com/mystream" }
})

const API = "https://api.radroddy.com"

const directChannel = ref(props.startChannel)
const tvVideo = ref(null)

const fetchCurrent = async () => {
  try {
    const res = await axios.get(`${API}/player/channels/current`)
    if (res.data.channel_number >= 0) {
      directChannel.value = res.data.channel_number
    }
  } catch {}
}

const tuneChannel = async (num) => {
  try {
    await axios.post(`${API}/player/channel`, { command: "direct", channel: num })
    await fetchCurrent()
  } catch {}
}

const channelUp = () => tuneChannel(directChannel.value + 1)
const channelDown = () => tuneChannel(directChannel.value - 1)
const tuneDirect = () => { if (directChannel.value > 0) tuneChannel(directChannel.value) }

onMounted(async () => {
  await nextTick()

  const vid = tvVideo.value

  // WebRTC pull (WHEP)
  const pc = new RTCPeerConnection()
  pc.ontrack = (event) => {
    vid.srcObject = event.streams[0]
  }

  pc.addTransceiver("video", { direction: "recvonly" })
  pc.addTransceiver("audio", { direction: "recvonly" })

  const offer = await pc.createOffer()
  await pc.setLocalDescription(offer)

  const res = await fetch(props.streamUrl + "/whep", {
    method: "POST",
    body: offer.sdp,
    headers: { "Content-Type": "application/sdp" }
  })
  const answer = await res.text()
  await pc.setRemoteDescription({ type: "answer", sdp: answer })

  // autoplay hack: unmute after 1 second
  setTimeout(() => {
    vid.muted = false
    vid.volume = 1.0
    vid.play().catch(() => {})
  }, 1000)

  if (props.startChannel > 0) {
    await tuneChannel(props.startChannel)
  } else {
    await fetchCurrent()
  }
})
</script>

