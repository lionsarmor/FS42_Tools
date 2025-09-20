<template>
  <div
    class="fixed inset-0 bg-black flex items-center justify-center"
    @mousemove="showOverlay"
    @keydown="showOverlay"
  >
    <!-- Video -->
    <video
      ref="videoRef"
      autoplay
      playsinline
      class="w-full h-full object-contain bg-black"
    ></video>

    <!-- Overlay -->
    <div
      v-show="overlayVisible"
      class="absolute inset-0 flex flex-col justify-between transition-opacity duration-500"
      :class="{ 'opacity-0': !overlayVisible, 'opacity-100': overlayVisible }"
    >
      <!-- Top -->
      <div class="flex justify-between items-center p-4 bg-gradient-to-b from-black/70 to-transparent">
        <div>
          <div class="text-white text-xl font-bold">
            Channel {{ String(currentChannel).padStart(2, "0") }}
          </div>
          <div class="text-white/70 text-sm">{{ streamStatus }}</div>
        </div>
        <button
          @click="exitPlayer"
          class="bg-red-600 hover:bg-red-700 text-white rounded-full px-4 py-2"
        >
          ✕ Exit
        </button>
      </div>

      <!-- Bottom -->
      <div class="flex justify-center items-center space-x-6 p-4 bg-gradient-to-t from-black/70 to-transparent">
        <button @click="channelDown" class="control-btn">⬅</button>

        <div class="flex flex-col items-center">
          <span class="text-white/70 text-xs uppercase">Channel</span>
          <input
            v-model.number="directChannel"
            type="number"
            class="w-20 text-center bg-black/40 border border-white/30 rounded text-white focus:ring-2 focus:ring-blue-500"
            @keyup.enter="tuneDirect"
          />
          <button
            @click="tuneDirect"
            class="mt-1 px-3 py-1 bg-green-500 hover:bg-green-600 text-white rounded text-sm"
          >
            Go
          </button>
        </div>

        <button @click="channelUp" class="control-btn">➡</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import axios from "axios"

const videoRef = ref(null)
const peerConnection = ref(null)

const overlayVisible = ref(true)
const streamStatus = ref("Connecting...")
const currentChannel = ref(1)
const directChannel = ref(1)
const isMuted = ref(true)

const API = "https://api.radroddy.com"
let hideTimer = null
let channelBuffer = ""

// Overlay fade logic
const showOverlay = () => {
  overlayVisible.value = true
  if (hideTimer) clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    overlayVisible.value = false
  }, 3000)
}

// WebRTC connect
const connectWebRTC = async () => {
  try {
    streamStatus.value = "Starting..."
    if (peerConnection.value) peerConnection.value.close()

    peerConnection.value = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
    })

    peerConnection.value.ontrack = (event) => {
      if (videoRef.value && event.streams[0]) {
        videoRef.value.srcObject = event.streams[0]
        videoRef.value.muted = true
        videoRef.value.play().then(() => {
          // Try delayed unmute
          setTimeout(() => {
            videoRef.value.muted = false
            videoRef.value.volume = 1.0
            isMuted.value = false
          }, 2000)
          streamStatus.value = "Live"
        }).catch(() => {
          streamStatus.value = "Click to Start"
        })
      }
    }

    peerConnection.value.addTransceiver("video", { direction: "recvonly" })
    peerConnection.value.addTransceiver("audio", { direction: "recvonly" })

    const offer = await peerConnection.value.createOffer()
    await peerConnection.value.setLocalDescription(offer)

    await new Promise((resolve) => {
      if (peerConnection.value.iceGatheringState === "complete") return resolve()
      peerConnection.value.onicegatheringstatechange = () => {
        if (peerConnection.value.iceGatheringState === "complete") resolve()
      }
      setTimeout(resolve, 2000)
    })

    const resp = await fetch("https://cable.radroddy.com/mystream/whep", {
      method: "POST",
      headers: {
        "Content-Type": "application/sdp",
        Accept: "application/sdp"
      },
      body: peerConnection.value.localDescription.sdp
    })
    const answer = await resp.text()
    await peerConnection.value.setRemoteDescription({ type: "answer", sdp: answer })

    streamStatus.value = "Connected"
  } catch (err) {
    console.error("WebRTC failed:", err)
    streamStatus.value = "Error"
  }
}

// Channel API
const fetchCurrent = async () => {
  const res = await axios.get(`${API}/player/channels/current`)
  currentChannel.value = res.data.channel_number
  directChannel.value = res.data.channel_number
}
const channelUp = async () => {
  await axios.post(`${API}/player/channels/up`)
  await fetchCurrent()
  showOverlay()
}
const channelDown = async () => {
  await axios.post(`${API}/player/channels/down`)
  await fetchCurrent()
  showOverlay()
}
const tuneDirect = async () => {
  await axios.post(`${API}/player/channel`, {
    command: "direct",
    channel: directChannel.value
  })
  await fetchCurrent()
  channelBuffer = ""
  showOverlay()
}

// Exit
const exitPlayer = () => {
  window.history.back()
}

// Key controls
const handleKeypress = (e) => {
  showOverlay()
  switch (e.key) {
    case "ArrowUp": case "+": channelUp(); break
    case "ArrowDown": case "-": channelDown(); break
    case "Escape": exitPlayer(); break
    case "Enter":
      if (channelBuffer.length > 0) {
        directChannel.value = parseInt(channelBuffer)
        tuneDirect()
      }
      break
    default:
      if (/^[0-9]$/.test(e.key)) {
        channelBuffer += e.key
        directChannel.value = parseInt(channelBuffer)
        setTimeout(() => (channelBuffer = ""), 2000)
      }
  }
}

onMounted(async () => {
  await connectWebRTC()
  await fetchCurrent()
  showOverlay()
  window.addEventListener("keydown", handleKeypress)
})
onUnmounted(() => {
  window.removeEventListener("keydown", handleKeypress)
})
</script>

<style>
.control-btn {
  @apply bg-white/20 hover:bg-white/30 text-white rounded-full w-12 h-12 flex items-center justify-center text-2xl;
}
</style>
