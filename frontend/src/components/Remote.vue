<template>
  <div class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
    <div class="bg-gradient-to-b from-slate-800 to-slate-900 rounded-3xl p-8 w-full max-w-sm shadow-2xl border border-slate-600">
      <!-- Header with FS42 Branding -->
      <div class="flex justify-between items-center mb-6">
        <div class="text-center w-full">
          <h3 class="text-xl font-bold text-purple-300">FS42</h3>
          <p class="text-xs text-slate-400">REMOTE CONTROL</p>
        </div>
        <button @click="$emit('close')" class="absolute top-4 right-4 text-slate-400 hover:text-red-400 text-xl">×</button>
      </div>

      <!-- Status Display Screen -->
      <div class="bg-black rounded-lg p-4 mb-6 border-2 border-slate-700 shadow-inner">
        <div class="text-center">
          <div class="text-2xl font-mono text-green-400 mb-1">
            CH {{ currentStatus.channel_number || '--' }}
          </div>
          <div class="text-sm text-blue-300 truncate">
            {{ currentStatus.network_name || 'NO SIGNAL' }}
          </div>
          <div class="text-xs text-slate-400 mt-1">
            {{ currentStatus.status || 'OFFLINE' }}
          </div>
        </div>
      </div>

      <!-- Power Button -->
      <div class="flex justify-center mb-6">
        <button @click="rebootPi" 
                class="w-16 h-16 rounded-full bg-gradient-to-b from-red-500 to-red-700 hover:from-red-400 hover:to-red-600 text-white shadow-lg border-2 border-red-800 font-bold">
          PWR
        </button>
      </div>

      <!-- Volume and Channel Controls -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="flex flex-col gap-2">
          <button @click="volumeUp" 
                  class="py-3 bg-gradient-to-b from-blue-600 to-blue-800 hover:from-blue-500 hover:to-blue-700 text-white rounded-lg border border-blue-500 font-semibold">
            VOL+
          </button>
          <button @click="volumeDown" 
                  class="py-3 bg-gradient-to-b from-blue-600 to-blue-800 hover:from-blue-500 hover:to-blue-700 text-white rounded-lg border border-blue-500 font-semibold">
            VOL-
          </button>
        </div>
        
        <div class="flex flex-col justify-center items-center">
          <button @click="mute" 
                  class="w-16 h-16 rounded-full bg-gradient-to-b from-slate-600 to-slate-800 hover:from-slate-500 hover:to-slate-700 text-white border-2 border-slate-500 text-sm font-bold">
            MUTE
          </button>
        </div>
        
        <div class="flex flex-col gap-2">
          <button @click="channelUp" 
                  class="py-3 bg-gradient-to-b from-purple-600 to-purple-800 hover:from-purple-500 hover:to-purple-700 text-white rounded-lg border border-purple-500 font-semibold">
            CH+
          </button>
          <button @click="channelDown" 
                  class="py-3 bg-gradient-to-b from-purple-600 to-purple-800 hover:from-purple-500 hover:to-purple-700 text-white rounded-lg border border-purple-500 font-semibold">
            CH-
          </button>
        </div>
      </div>

      <!-- Number Pad -->
      <div class="grid grid-cols-3 gap-3 mb-6">
        <button v-for="num in [1,2,3,4,5,6,7,8,9]" 
                :key="num"
                @click="inputDigit(num)" 
                class="h-12 bg-gradient-to-b from-slate-600 to-slate-800 hover:from-slate-500 hover:to-slate-700 text-white rounded-lg border border-slate-500 font-bold text-lg shadow-lg">
          {{ num }}
        </button>
      </div>

      <!-- Bottom Number Row -->
      <div class="grid grid-cols-3 gap-3 mb-6">
        <button @click="inputFunction('*')" 
                class="h-12 bg-gradient-to-b from-yellow-600 to-yellow-800 hover:from-yellow-500 hover:to-yellow-700 text-white rounded-lg border border-yellow-500 font-bold text-lg shadow-lg">
          *
        </button>
        <button @click="inputDigit(0)" 
                class="h-12 bg-gradient-to-b from-slate-600 to-slate-800 hover:from-slate-500 hover:to-slate-700 text-white rounded-lg border border-slate-500 font-bold text-lg shadow-lg">
          0
        </button>
        <button @click="inputFunction('#')" 
                class="h-12 bg-gradient-to-b from-yellow-600 to-yellow-800 hover:from-yellow-500 hover:to-yellow-700 text-white rounded-lg border border-yellow-500 font-bold text-lg shadow-lg">
          #
        </button>
      </div>

      <!-- Channel Input Display -->
      <div v-if="channelInput" class="text-center mb-4 p-2 bg-blue-900 rounded-lg border border-blue-700">
        <div class="text-blue-200 text-sm">ENTERING CHANNEL</div>
        <div class="text-white text-xl font-mono">{{ channelInput }}</div>
      </div>

      <!-- Function Buttons -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <button @click="showGuide" 
                class="py-3 bg-gradient-to-b from-indigo-600 to-indigo-800 hover:from-indigo-500 hover:to-indigo-700 text-white rounded-lg border border-indigo-500 font-semibold">
          GUIDE
        </button>
        <button @click="toggleInfo" 
                class="py-3 bg-gradient-to-b from-green-600 to-green-800 hover:from-green-500 hover:to-green-700 text-white rounded-lg border border-green-500 font-semibold">
          INFO
        </button>
      </div>

      <!-- Error Display -->
      <div v-if="errorMsg" class="mt-4 p-3 bg-red-900 border border-red-700 rounded-lg">
        <div class="text-red-200 text-center text-sm">
          {{ errorMsg }}
        </div>
      </div>

      <!-- Remote Model Info -->
      <div class="text-center mt-6 text-xs text-slate-500">
        Model: FS42-RC-2025
      </div>

      <!-- Info Overlay - Takes up half the screen as test -->
      <div v-if="showInfoOverlay" 
           class="fixed top-1/4 left-1/4 w-1/2 h-1/2 bg-black bg-opacity-95 flex items-center justify-center z-[60] border-2 border-purple-500 rounded-lg">
        <div class="text-center text-white p-8">
          <h3 class="text-2xl font-bold mb-4">INFO OVERLAY TEST</h3>
          <p class="text-lg mb-4">Half-screen black box</p>
          <p class="text-sm text-gray-400">IMDB integration coming soon...</p>
          <button @click="showInfoOverlay = false" 
                  class="mt-6 px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg">
            CLOSE
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL

const currentStatus = ref({})
const errorMsg = ref('')
const channelInput = ref('')
const inputTimer = ref(null)
const showInfoOverlay = ref(false)

// Channel input handling
const inputDigit = (digit) => {
  channelInput.value += digit.toString()
  
  // Clear existing timer
  if (inputTimer.value) {
    clearTimeout(inputTimer.value)
  }
  
  // Set new timer to tune after 1.5 seconds of no input
  inputTimer.value = setTimeout(() => {
    if (channelInput.value) {
      tuneToChannel(parseInt(channelInput.value))
      channelInput.value = ''
    }
  }, 1500)
}

const inputFunction = (func) => {
  if (func === '*') {
    // Star - clear input
    channelInput.value = ''
    if (inputTimer.value) {
      clearTimeout(inputTimer.value)
    }
  } else if (func === '#') {
    // Pound - confirm channel input immediately
    if (channelInput.value) {
      tuneToChannel(parseInt(channelInput.value))
      channelInput.value = ''
      if (inputTimer.value) {
        clearTimeout(inputTimer.value)
      }
    }
  }
}

// API calls using your existing backend endpoints
const fetchCurrentStatus = async () => {
  try {
    const response = await axios.get(`${API}/player/channels/current`)
    currentStatus.value = response.data
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'FAILED TO GET STATUS'
    console.error('Status fetch error:', error)
  }
}

const tuneToChannel = async (channel) => {
  try {
    await axios.post(`${API}/player/channels/${channel}`)
    await fetchCurrentStatus()
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = `TUNE FAILED: CH ${channel}`
    console.error('Tune error:', error)
  }
}

const channelUp = async () => {
  try {
    await axios.post(`${API}/player/channels/up`)
    await fetchCurrentStatus()
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'CHANNEL UP FAILED'
    console.error('Channel up error:', error)
  }
}

const channelDown = async () => {
  try {
    await axios.post(`${API}/player/channels/down`)
    await fetchCurrentStatus()
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'CHANNEL DOWN FAILED'
    console.error('Channel down error:', error)
  }
}

// Volume controls - send to Pi machine
const volumeUp = async () => {
  try {
    await axios.post(`${API}/pi/volume/up`)
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'VOLUME CONTROL FAILED'
    console.error('Volume up error:', error)
  }
}

const volumeDown = async () => {
  try {
    await axios.post(`${API}/pi/volume/down`)
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'VOLUME CONTROL FAILED'
    console.error('Volume down error:', error)
  }
}

const mute = async () => {
  try {
    await axios.post(`${API}/pi/volume/mute`)
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'MUTE FAILED'
    console.error('Mute error:', error)
  }
}

// Guide function - tune to channel 3
const showGuide = async () => {
  try {
    await axios.post(`${API}/player/channels/3`)
    await fetchCurrentStatus()
    errorMsg.value = ''
  } catch (error) {
    errorMsg.value = 'GUIDE UNAVAILABLE'
    console.error('Guide error:', error)
  }
}

// Info overlay toggle
const toggleInfo = async () => {
  showInfoOverlay.value = !showInfoOverlay.value
  
  // Auto-hide after 5 seconds
  if (showInfoOverlay.value) {
    setTimeout(() => {
      showInfoOverlay.value = false
    }, 5000)
  }
}

// Power button - reboot the Pi
const rebootPi = async () => {
  if (!confirm('Are you sure you want to reboot this Pi?')) return
  
  try {
    await axios.post(`${API}/pi/reboot`)
    currentStatus.value = { status: 'REBOOTING PI', network_name: '', channel_number: null }
    errorMsg.value = 'PI REBOOTING...'
  } catch (error) {
    errorMsg.value = 'PI REBOOT FAILED'
    console.error('Reboot error:', error)
  }
}

// Status polling
let statusInterval = null

onMounted(() => {
  fetchCurrentStatus()
  // Poll status every 3 seconds
  statusInterval = setInterval(fetchCurrentStatus, 3000)
})

onUnmounted(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
  if (inputTimer.value) {
    clearTimeout(inputTimer.value)
  }
})

defineEmits(['close'])
</script>