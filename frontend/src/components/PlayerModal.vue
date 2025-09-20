<template>
  <div class="fixed inset-0 bg-black flex items-center justify-center z-50">
    <div class="w-full h-full flex flex-col relative">
      
      <!-- TV-Style Header Overlay -->
      <div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/90 via-black/50 to-transparent p-6">
        <div class="flex justify-between items-start">
          <div class="flex items-center space-x-6">
            <!-- Digital Channel Display -->
            <div class="bg-black/70 backdrop-blur-md rounded-xl px-6 py-3 border border-cyan-500/30 shadow-lg">
              <div class="text-cyan-400 font-mono text-4xl font-bold tracking-wider glow-text">
                {{ String(directChannel).padStart(2, '0') }}
              </div>
              <div class="text-cyan-300 text-xs uppercase tracking-widest mt-1">
                CHANNEL
              </div>
            </div>
            
            <!-- Station Info -->
            <div class="text-white">
              <h2 class="text-3xl font-bold text-white mb-1 drop-shadow-lg">📺 Tsar TV</h2>
              <div class="flex items-center space-x-3 text-gray-300">
                <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <p class="text-sm">LIVE BROADCAST</p>
                <span class="text-gray-500">•</span>
                <p class="text-sm">{{ new Date().toLocaleTimeString() }}</p>
              </div>
              <p class="text-gray-400 text-xs mt-1">HD Digital Signal</p>
            </div>
          </div>

          <!-- Close Button -->
          <button
            @click="$emit('close')"
            class="w-12 h-12 flex items-center justify-center bg-red-600/80 hover:bg-red-500 text-white rounded-full transition-all duration-200 backdrop-blur-md border border-red-400/50 shadow-lg hover:scale-105"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Main Video Display -->
      <div class="flex-1 relative bg-black">
        <iframe
          :src="streamUrl"
          class="w-full h-full"
          allow="autoplay; fullscreen"
          frameborder="0"
        ></iframe>
        
        <!-- Signal Indicator -->
        <div class="absolute top-4 right-4 bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1 border border-green-500/30">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-green-400 text-xs font-mono">SIGNAL</span>
          </div>
        </div>
      </div>

      <!-- Bottom Control Panel -->
      <div class="absolute bottom-0 left-0 right-0 z-10 bg-gradient-to-t from-black/90 via-black/70 to-transparent p-6">
        <div class="max-w-2xl mx-auto">
          
          <!-- Channel Control Bar -->
          <div class="bg-black/70 backdrop-blur-md rounded-2xl p-6 border border-gray-600/30 shadow-2xl">
            <div class="flex items-center justify-center space-x-6">
              
              <!-- Channel Down -->
              <button 
                @click="channelDown" 
                class="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-xl transition-all duration-200 shadow-lg hover:scale-105 border border-blue-400/30"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
              </button>

              <!-- Direct Channel Input -->
              <div class="flex items-center space-x-3">
                <div class="text-white text-sm font-medium">CH</div>
                <input 
                  v-model.number="directChannel" 
                  type="number" 
                  min="1"
                  max="999"
                  class="w-20 h-12 text-center text-xl font-mono bg-gray-900/80 border border-gray-600 rounded-lg text-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent backdrop-blur-sm"
                />
                <button 
                  @click="tuneDirect" 
                  class="px-6 h-12 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white rounded-lg font-semibold transition-all duration-200 shadow-lg hover:scale-105 border border-green-400/30"
                >
                  TUNE
                </button>
              </div>

              <!-- Channel Up -->
              <button 
                @click="channelUp" 
                class="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white rounded-xl transition-all duration-200 shadow-lg hover:scale-105 border border-blue-400/30"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
            </div>

            <!-- Volume Control Row (Visual Only) -->
            <div class="flex items-center justify-center space-x-4 mt-4 pt-4 border-t border-gray-700/50">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M6 10H4a1 1 0 00-1 1v2a1 1 0 001 1h2l4 4V6L6 10z"></path>
              </svg>
              <div class="flex-1 max-w-48">
                <div class="relative">
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value="65"
                    class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                    readonly
                  >
                  <div class="absolute inset-0 bg-gradient-to-r from-green-500 to-yellow-500 rounded-lg opacity-80" style="width: 65%"></div>
                </div>
              </div>
              <span class="text-gray-400 text-sm font-mono w-8 text-right">65</span>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="errorMsg" class="mt-4 p-3 bg-red-900/80 border border-red-500/30 rounded-lg backdrop-blur-sm">
            <div class="text-red-200 text-center text-sm font-medium">
              {{ errorMsg }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"

const props = defineProps({
  startChannel: { type: Number, default: 1 },
  streamUrl: { type: String, default: "https://cable.radroddy.com/mystream" }
})

const API = "https://api.radroddy.com"

const directChannel = ref(props.startChannel)
const errorMsg = ref("")

// === Fetch current channel ===
const fetchCurrent = async () => {
  try {
    const res = await axios.get(`${API}/player/channels/current`)
    if (res.data.channel_number >= 0) {
      directChannel.value = res.data.channel_number
      errorMsg.value = ""
    }
  } catch {
    errorMsg.value = "⚠️ FS42 player not responding"
  }
}

// === Direct tune ===
const tuneChannel = async (num) => {
  try {
    await axios.post(`${API}/player/channel`, {
      command: "direct",
      channel: num
    })
    await fetchCurrent()
  } catch {
    errorMsg.value = "⚠️ Tune failed"
  }
}

// === Channel stepping ===
const channelUp = async () => {
  try {
    await axios.post(`${API}/player/channels/up`)
    await fetchCurrent()
  } catch {
    errorMsg.value = "⚠️ Up failed"
  }
}

const channelDown = async () => {
  try {
    await axios.post(`${API}/player/channels/down`)
    await fetchCurrent()
  } catch {
    errorMsg.value = "⚠️ Down failed"
  }
}

// === Button action ===
const tuneDirect = () => {
  if (directChannel.value > 0) tuneChannel(directChannel.value)
}

// === Init ===
onMounted(async () => {
  if (props.startChannel > 0) {
    await tuneChannel(props.startChannel)
  } else {
    await fetchCurrent()
  }
})
</script>

<style scoped>
.glow-text {
  text-shadow: 0 0 10px currentColor;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #10b981;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.slider::-moz-range-thumb {
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #10b981;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}
</style>