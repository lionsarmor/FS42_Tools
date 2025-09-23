<template>
  <!-- Box Selection Modal -->
  <div v-if="!selectedBox" class="fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center z-50 p-4">
    <div class="bg-slate-800 rounded-2xl p-4 w-full max-w-xs sm:max-w-sm">
      <h3 class="text-lg sm:text-xl font-bold text-purple-300 mb-4 text-center">Select Your Cable Box</h3>
      <div class="space-y-3">
        <button v-for="box in availableBoxes" :key="box.id"
                @click="selectBox(box)"
                :disabled="!box.online"
                class="w-full p-3 sm:p-4 rounded-lg text-white font-semibold text-sm sm:text-base transition-all"
                :class="box.online 
                  ? 'bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600'
                  : 'bg-gray-700 cursor-not-allowed opacity-50'">
          <div class="flex items-center justify-between">
            <span>{{ box.name }}</span>
            <div class="text-xs sm:text-sm" :class="box.online ? 'text-green-400' : 'text-red-400'">
              {{ box.online ? 'Online' : 'Offline' }}
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>

  <!-- Info Modal -->
  <div v-if="showInfoModal" class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4">
    <div class="bg-slate-800 rounded-2xl p-6 max-w-sm w-full text-center relative">
      <h3 class="text-lg font-bold text-green-300 mb-4">System Info</h3>
      <p class="text-sm text-slate-300 mb-3">Channel: {{ currentStatus.channel_number || '--' }}</p>
      <p class="text-sm text-slate-300 mb-3">Network: {{ currentStatus.network_name || 'N/A' }}</p>
      <p class="text-sm text-yellow-400 mb-3">Now Playing: {{ nowPlaying || 'N/A' }}</p>
      <button @click="showInfoModal=false"
              class="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg text-white font-bold shadow-lg">
        Close
      </button>
    </div>
  </div>

  <!-- PIN Modal -->
  <div v-if="showPinModal" class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-[80]">
    <div class="bg-slate-800 p-6 rounded-xl w-72 text-center">
      <h3 class="text-lg text-purple-300 font-bold mb-4">Enter PIN</h3>
      <input v-model="pinInput" type="password"
             class="w-full mb-4 px-3 py-2 rounded bg-slate-700 text-white text-center"
             placeholder="****" maxlength="4" />
      <div class="flex justify-center gap-3">
        <button @click="submitPin" class="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg">OK</button>
        <button @click="showPinModal=false" class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg">Cancel</button>
      </div>
    </div>
  </div>

  <!-- Main Remote -->
  <div v-else class="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-3">
    <div class="bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl w-full max-w-xs sm:max-w-sm mx-auto shadow-2xl border border-slate-600 flex flex-col overflow-hidden">
      
      <!-- Header -->
      <div class="flex justify-between items-center p-3 sm:p-4">
        <div class="text-center w-full">
          <h3 class="text-base sm:text-lg font-bold text-purple-300">FS42</h3>
          <p class="text-xs text-slate-400">{{ selectedBox.name }}</p>
        </div>
        <button @click="showBoxSelector" class="absolute top-3 left-3 text-slate-400 hover:text-blue-400 text-xs sm:text-sm">SWITCH</button>
        <button @click="$emit('close')" class="absolute top-3 right-3 text-slate-400 hover:text-red-400 text-lg sm:text-xl">×</button>
      </div>

      <!-- Status -->
      <div class="mx-3 sm:mx-4 mb-4 bg-black rounded-lg p-3 border-2 border-slate-700 shadow-inner">
        <div class="text-center">
          <div class="text-lg sm:text-xl font-mono text-green-400 mb-1">
            CH {{ currentStatus.channel_number || '--' }}
          </div>
          <div class="text-xs sm:text-sm text-blue-300 truncate">
            {{ currentStatus.network_name || 'NO SIGNAL' }}
          </div>
          <div class="text-[0.65rem] sm:text-xs text-yellow-400 mt-1 truncate">
            {{ nowPlaying || 'Fetching now playing...' }}
          </div>
          <div class="text-[0.65rem] sm:text-xs text-slate-400 mt-1">
            {{ currentStatus.status || 'OFFLINE' }}
          </div>
        </div>
      </div>

      <!-- Power -->
      <div class="flex justify-center mb-4">
        <button @click="restartPi" class="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-gradient-to-b from-red-500 to-red-700 hover:from-red-400 hover:to-red-600 text-white shadow-lg border-2 border-red-800 font-bold text-sm">
          PWR
        </button>
      </div>

      <!-- Volume + Channel -->
      <div class="grid grid-cols-3 gap-3 mb-4 px-4 text-xs sm:text-sm">
        <div class="flex flex-col gap-3">
          <button @click="volumeUp" class="py-3 bg-blue-700 hover:bg-blue-600 text-white rounded-lg border border-blue-500 font-semibold">VOL+</button>
          <button @click="volumeDown" class="py-3 bg-blue-700 hover:bg-blue-600 text-white rounded-lg border border-blue-500 font-semibold">VOL-</button>
        </div>
        <div class="flex flex-col justify-center items-center">
          <button @click="mute" class="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-slate-700 hover:bg-slate-600 text-white border-2 border-slate-500 text-sm font-bold">MUTE</button>
        </div>
        <div class="flex flex-col gap-3">
          <button @click="channelUp" class="py-3 bg-purple-700 hover:bg-purple-600 text-white rounded-lg border border-purple-500 font-semibold">CH+</button>
          <button @click="channelDown" class="py-3 bg-purple-700 hover:bg-purple-600 text-white rounded-lg border border-purple-500 font-semibold">CH-</button>
        </div>
      </div>

      <!-- PIN Pad -->
      <div class="grid grid-cols-3 gap-3 mb-4 px-4 text-lg sm:text-xl">
        <button v-for="num in [1,2,3,4,5,6,7,8,9]" :key="num" @click="inputDigit(num)"
                class="h-12 sm:h-14 bg-slate-700 hover:bg-slate-600 text-white rounded-lg border border-slate-500 font-bold shadow-lg">
          {{ num }}
        </button>
      </div>
      <div class="grid grid-cols-3 gap-3 mb-4 px-4 text-lg sm:text-xl">
        <button @click="inputFunction('*')" class="h-12 sm:h-14 bg-yellow-700 hover:bg-yellow-600 text-white rounded-lg border border-yellow-500 font-bold">*</button>
        <button @click="inputDigit(0)" class="h-12 sm:h-14 bg-slate-700 hover:bg-slate-600 text-white rounded-lg border border-slate-500 font-bold">0</button>
        <button @click="inputFunction('#')" class="h-12 sm:h-14 bg-yellow-700 hover:bg-yellow-600 text-white rounded-lg border border-yellow-500 font-bold">#</button>
      </div>

      <!-- Function Buttons -->
      <div class="grid grid-cols-3 gap-3 mb-4 px-4">
        <button @click="showGuide" class="py-3 bg-indigo-700 hover:bg-indigo-600 text-white rounded-lg border border-indigo-500 font-semibold text-xs sm:text-sm">GUIDE</button>
        <button @click="showInfoModal=true" class="py-3 bg-green-700 hover:bg-green-600 text-white rounded-lg border border-green-500 font-semibold text-xs sm:text-sm">INFO</button>
        <button @click="showPinModal=true" class="py-3 bg-orange-700 hover:bg-orange-600 text-white rounded-lg border border-orange-500 font-semibold text-xs sm:text-sm">REFRESH</button>
      </div>

      <!-- Footer -->
      <div class="text-center pb-4 text-[0.65rem] sm:text-xs text-slate-500">
        Model: FS42-RC-2025
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

const currentStatus = ref({})
const nowPlaying = ref('')
const channelInput = ref('')
const inputTimer = ref(null)
const selectedBox = ref(null)

const showInfoModal = ref(false)
const showPinModal = ref(false)
const pinInput = ref('')
const correctPin = '1234'

const availableBoxes = ref([
  { id: 'cable',  name: 'Cable Box',   ip: '100.117.143.10', online: false },
  { id: 'cable1', name: 'Cable Box 1', ip: '100.81.14.111',  online: false },
  { id: 'cable2', name: 'Cable Box 2', ip: '100.92.235.10',  online: false },
])

// Status
const fetchCurrentStatus = async () => {
  try {
    const r = await axios.get(`${API}/player/status`)
    currentStatus.value = r.data
    nowPlaying.value = r.data?.title || ''
  } catch {
    currentStatus.value = {}
    nowPlaying.value = ''
  }
}

// Submit PIN for refresh
const submitPin = async () => {
  if (pinInput.value === correctPin) {
    showPinModal.value = false
    pinInput.value = ''
    if (selectedBox.value) {
      await axios.post(`${API}/pi/${selectedBox.value.id}/reboot`).catch(() => {})
    }
    await axios.post(`${API}/hot-start`).catch(() => {})
    currentStatus.value = { status: 'REFRESHING' }
  } else {
    pinInput.value = ''
    alert('Incorrect PIN')
  }
}

// Pi only
const restartPi = async () => {
  if (!selectedBox.value) return
  await axios.post(`${API}/pi/${selectedBox.value.id}/reboot`).catch(() => {})
  currentStatus.value = { status: 'RESTARTING' }
}

// Channels
const tuneToChannel = (ch) => axios.post(`${API}/player/channels/${ch}`).then(fetchCurrentStatus)
const channelUp = () => axios.post(`${API}/player/channels/up`).then(fetchCurrentStatus)
const channelDown = () => axios.post(`${API}/player/channels/down`).then(fetchCurrentStatus)

// Volume
const volumeUp = () => axios.post(`${API}/pi/${selectedBox.value.id}/volume/up`).catch(() => {})
const volumeDown = () => axios.post(`${API}/pi/${selectedBox.value.id}/volume/down`).catch(() => {})
const mute = () => axios.post(`${API}/pi/${selectedBox.value.id}/volume/mute`).catch(() => {})

// Input
const inputDigit = (d) => {
  channelInput.value += d.toString()
  if (inputTimer.value) clearTimeout(inputTimer.value)
  inputTimer.value = setTimeout(() => {
    if (channelInput.value) {
      tuneToChannel(parseInt(channelInput.value))
      channelInput.value = ''
    }
  }, 1500)
}
const inputFunction = (f) => {
  if (f === '*') channelInput.value = ''
  if (f === '#' && channelInput.value) {
    tuneToChannel(parseInt(channelInput.value))
    channelInput.value = ''
  }
}

// Lifecycle
let statusInterval = null
onMounted(() => {
  const saved = localStorage.getItem('selectedCableBox')
  if (saved) selectedBox.value = JSON.parse(saved)
  fetchCurrentStatus()
  statusInterval = setInterval(fetchCurrentStatus, 3000)
})
onUnmounted(() => {
  if (statusInterval) clearInterval(statusInterval)
  if (inputTimer.value) clearTimeout(inputTimer.value)
})
</script>

<style>
input, button {
  font-size: 16px !important;
  touch-action: manipulation;
}
</style>
