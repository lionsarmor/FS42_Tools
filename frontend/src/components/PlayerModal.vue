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
    const res = await axios.get(`${API}/player/status`)
    if (res.data.channel_number >= 0) {
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
    console.error("Failed to tune channel:", err)
  }
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
