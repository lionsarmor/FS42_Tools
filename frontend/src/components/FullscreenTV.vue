<template>
  <div class="fixed inset-0 bg-black overflow-hidden" @mousemove="showControls" @click="showControls">
    <!-- Video Element - WebRTC Stream -->
    <video
      ref="videoPlayer"
      class="w-full h-full object-contain"
      autoplay
      playsinline
      :controls="false"
      @loadeddata="onVideoReady"
      @error="onVideoError"
      @canplay="onCanPlay"
    >
      Your browser does not support the video tag.
    </video>

    <!-- Overlay Controls -->
    <div 
      v-show="showOverlay" 
      class="absolute inset-0 z-10 transition-opacity duration-500 pointer-events-none"
      :class="{ 'opacity-0': !overlayVisible, 'opacity-100': overlayVisible }"
    >
      <!-- Top Info Bar -->
      <div class="absolute top-6 left-6 right-6 flex justify-between items-start pointer-events-auto">
        <div class="bg-black/60 backdrop-blur-lg rounded-2xl px-6 py-4 border border-white/20">
          <div class="flex items-center space-x-4">
            <div class="text-white font-mono text-3xl font-bold">
              {{ String(currentChannel).padStart(2, '0') }}
            </div>
            <div>
              <div class="text-white text-lg font-semibold">Live Stream</div>
              <div class="text-white/70 text-sm">{{ streamStatus }}</div>
            </div>
          </div>
        </div>

        <!-- Volume & Exit Controls -->
        <div class="flex gap-4">
          <button
            @click="toggleMute"
            class="w-12 h-12 bg-white/20 hover:bg-white/30 text-white rounded-full transition-all duration-200 backdrop-blur-lg flex items-center justify-center text-xl"
          >
            {{ isMuted ? '🔇' : '🔊' }}
          </button>
          <button
            @click="exitFullscreen"
            class="w-12 h-12 bg-red-500/80 hover:bg-red-500 text-white rounded-full transition-all duration-200 backdrop-blur-lg flex items-center justify-center text-2xl"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Bottom Controls -->
      <div class="absolute bottom-6 left-1/2 transform -translate-x-1/2 pointer-events-auto">
        <div class="bg-black/60 backdrop-blur-lg rounded-3xl px-8 py-6 border border-white/20">
          <div class="flex items-center space-x-8">
            
            <!-- Channel Down -->
            <button 
              @click="channelDown" 
              class="w-14 h-14 bg-blue-500/80 hover:bg-blue-500 text-white rounded-xl transition-all duration-200 flex items-center justify-center text-2xl font-bold"
            >
              ←
            </button>

            <!-- Channel Input -->
            <div class="flex flex-col items-center space-y-2">
              <div class="text-white/70 text-xs uppercase tracking-wider">Channel</div>
              <input 
                v-model.number="directChannel" 
                type="number" 
                min="1"
                max="999"
                class="w-20 h-12 text-center text-xl font-mono bg-white/10 border border-white/30 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400 backdrop-blur-sm"
                @keyup.enter="tuneDirect"
              />
              <button 
                @click="tuneDirect" 
                class="px-4 py-1 bg-green-500/80 hover:bg-green-500 text-white rounded text-sm font-semibold transition-all duration-200"
              >
                GO
              </button>
            </div>

            <!-- Channel Up -->
            <button 
              @click="channelUp" 
              class="w-14 h-14 bg-blue-500/80 hover:bg-blue-500 text-white rounded-xl transition-all duration-200 flex items-center justify-center text-2xl font-bold"
            >
              →
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Indicator -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
      <div class="text-center">
        <div class="text-white text-xl mb-2">Connecting to stream...</div>
        <div class="text-white/60 text-sm">{{ connectionState }}</div>
      </div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
      <div class="text-center">
        <div class="text-red-400 text-xl mb-2">Stream Error</div>
        <div class="text-white/70">{{ error }}</div>
        <button @click="retryConnection" class="mt-4 px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg">
          Retry Connection
        </button>
      </div>
    </div>

    <!-- Click to Start (for browsers that require interaction) -->
    <div v-if="needsInteraction" class="absolute inset-0 flex items-center justify-center bg-black/90 z-30">
      <button 
        @click="startPlayback" 
        class="px-12 py-6 bg-blue-500 hover:bg-blue-600 text-white text-xl rounded-lg transition-all duration-200 transform hover:scale-105"
      >
        ▶️ Click to Start Stream with Sound
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Core refs
const videoPlayer = ref(null)
const currentChannel = ref(1)
const directChannel = ref(1)
const loading = ref(true)
const error = ref('')

// WebRTC refs
const peerConnection = ref(null)

// Overlay control
const showOverlay = ref(true)
const overlayVisible = ref(true)
const streamStatus = ref('Connecting...')
const connectionState = ref('Initializing...')
const isMuted = ref(false)
const needsInteraction = ref(false)

const API = "https://api.radroddy.com"
let hideTimer = null

// WebRTC connection with proper WHEP implementation and extensive logging
const connectWebRTC = async () => {
  try {
    console.log('🚀 Starting WebRTC connection...')
    loading.value = true
    error.value = ''
    connectionState.value = 'Creating connection...'
    
    // Clean up any existing connection
    if (peerConnection.value) {
      console.log('🧹 Cleaning up existing connection')
      peerConnection.value.close()
    }

    // Create peer connection with multiple STUN servers
    console.log('📡 Creating RTCPeerConnection with STUN servers')
    peerConnection.value = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ],
      iceCandidatePoolSize: 10
    })
    console.log('✅ RTCPeerConnection created')

    // Monitor connection states
    peerConnection.value.onconnectionstatechange = () => {
      console.log('🔄 Connection state changed:', peerConnection.value.connectionState)
      connectionState.value = `Connection: ${peerConnection.value.connectionState}`
      
      if (peerConnection.value.connectionState === 'connected') {
        console.log('✅ WebRTC Connected Successfully!')
        streamStatus.value = 'Connected'
        loading.value = false
      } else if (peerConnection.value.connectionState === 'failed') {
        console.error('❌ Connection failed')
        error.value = 'Connection failed'
        loading.value = false
      }
    }

    peerConnection.value.oniceconnectionstatechange = () => {
      console.log('🧊 ICE connection state:', peerConnection.value.iceConnectionState)
    }

    peerConnection.value.onicegatheringstatechange = () => {
      console.log('🧊 ICE gathering state:', peerConnection.value.iceGatheringState)
    }

    peerConnection.value.onsignalingstatechange = () => {
      console.log('📶 Signaling state:', peerConnection.value.signalingState)
    }

    peerConnection.value.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('🧊 New ICE candidate:', event.candidate.candidate)
      } else {
        console.log('🧊 All ICE candidates gathered')
      }
    }

    // Handle incoming stream - CRITICAL FOR SOUND
    peerConnection.value.ontrack = async (event) => {
      console.log('🎥 Track received:', event.track.kind)
      console.log('📺 Streams:', event.streams)
      console.log('Stream details:', {
        id: event.streams[0]?.id,
        active: event.streams[0]?.active,
        tracks: event.streams[0]?.getTracks().map(t => ({
          kind: t.kind,
          enabled: t.enabled,
          muted: t.muted,
          readyState: t.readyState
        }))
      })
      
      if (videoPlayer.value && event.streams[0]) {
        console.log('🔗 Attaching stream to video element')
        videoPlayer.value.srcObject = event.streams[0]
        
        // Immediately try to play with sound
        try {
          console.log('🔊 Attempting to play with sound...')
          videoPlayer.value.muted = false
          videoPlayer.value.volume = 1.0
          await videoPlayer.value.play()
          console.log('✅ Playing with sound enabled!')
          loading.value = false
          needsInteraction.value = false
          streamStatus.value = 'Live'
        } catch (e) {
          console.warn('⚠️ Autoplay blocked:', e.message)
          needsInteraction.value = true
          loading.value = false
        }
      } else {
        console.error('❌ No video element or stream available')
      }
    }

    // Add transceivers for receiving audio and video
    console.log('📻 Adding transceivers for audio and video')
    const videoTransceiver = peerConnection.value.addTransceiver('video', { direction: 'recvonly' })
    const audioTransceiver = peerConnection.value.addTransceiver('audio', { direction: 'recvonly' })
    console.log('✅ Transceivers added:', {
      video: videoTransceiver.direction,
      audio: audioTransceiver.direction
    })

    // Create offer
    connectionState.value = 'Creating offer...'
    console.log('📝 Creating SDP offer...')
    const offer = await peerConnection.value.createOffer()
    console.log('📋 Offer created, SDP length:', offer.sdp.length)
    console.log('SDP Offer (first 500 chars):', offer.sdp.substring(0, 500))
    
    await peerConnection.value.setLocalDescription(offer)
    console.log('✅ Local description set')

    // Wait for ICE gathering
    connectionState.value = 'Gathering ICE candidates...'
    console.log('🧊 Waiting for ICE gathering...')
    await waitForIceGathering()
    console.log('✅ ICE gathering complete or timed out')

    // Log final SDP with candidates
    console.log('📋 Final SDP with ICE candidates (first 800 chars):', 
                peerConnection.value.localDescription.sdp.substring(0, 800))

    // Send offer to WHEP endpoint
    connectionState.value = 'Connecting to server...'
    const whepUrl = 'https://cable.radroddy.com:8889/mystream/whep'
    console.log('🌐 Sending offer to WHEP endpoint:', whepUrl)
    console.log('📤 Request details:', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/sdp',
        'Accept': 'application/sdp'
      },
      bodyLength: peerConnection.value.localDescription.sdp.length
    })
    
    try {
      const response = await fetch(whepUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/sdp',
          'Accept': 'application/sdp'
        },
        body: peerConnection.value.localDescription.sdp,
        mode: 'cors',
        credentials: 'omit'
      })

      console.log('📨 WHEP Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('❌ WHEP Error Response body:', errorText)
        throw new Error(`Server responded with ${response.status}: ${errorText || response.statusText}`)
      }

      const answerSdp = await response.text()
      console.log('📋 Answer received, SDP length:', answerSdp.length)
      console.log('SDP Answer (first 500 chars):', answerSdp.substring(0, 500))
    } catch (fetchError) {
      console.error('❌ Fetch error:', fetchError)
      console.error('Fetch error type:', fetchError.name)
      console.error('Fetch error message:', fetchError.message)
      
      // Check if it's a network/CORS error
      if (fetchError.name === 'TypeError' && fetchError.message.includes('fetch')) {
        console.error('🔒 This might be a CORS issue. The server needs to allow cross-origin requests.')
        console.error('Alternative: Try using a proxy or running from the same origin as the server.')
      }
      
      throw fetchError
    }
    
    // Set remote description
    connectionState.value = 'Setting up stream...'
    console.log('📝 Setting remote description...')
    await peerConnection.value.setRemoteDescription({
      type: 'answer',
      sdp: answerSdp
    })
    console.log('✅ Remote description set')

    console.log('🎉 WebRTC setup complete!')
    console.log('Current states:', {
      connectionState: peerConnection.value.connectionState,
      iceConnectionState: peerConnection.value.iceConnectionState,
      iceGatheringState: peerConnection.value.iceGatheringState,
      signalingState: peerConnection.value.signalingState
    })
    streamStatus.value = 'Stream active'

  } catch (err) {
    console.error('💥 WebRTC error:', err)
    console.error('Error stack:', err.stack)
    error.value = `Connection failed: ${err.message}`
    loading.value = false
  }
}

// Wait for ICE gathering to complete with logging
const waitForIceGathering = () => {
  return new Promise((resolve) => {
    const startTime = Date.now()
    console.log('⏱️ Starting ICE gathering wait...')
    
    if (peerConnection.value.iceGatheringState === 'complete') {
      console.log('✅ ICE gathering already complete')
      resolve()
    } else {
      const checkState = () => {
        const elapsed = Date.now() - startTime
        console.log(`🧊 ICE gathering state check at ${elapsed}ms:`, peerConnection.value.iceGatheringState)
        
        if (peerConnection.value.iceGatheringState === 'complete') {
          console.log(`✅ ICE gathering complete after ${elapsed}ms`)
          resolve()
        }
      }
      peerConnection.value.onicegatheringstatechange = checkState
      
      // Timeout after 5 seconds
      setTimeout(() => {
        console.log('⏱️ ICE gathering timeout after 5000ms, proceeding anyway')
        console.log('Final ICE gathering state:', peerConnection.value.iceGatheringState)
        resolve()
      }, 5000)
    }
  })
}

// Start playback with user interaction
const startPlayback = async () => {
  if (videoPlayer.value) {
    try {
      videoPlayer.value.muted = false
      videoPlayer.value.volume = 1.0
      await videoPlayer.value.play()
      needsInteraction.value = false
      console.log('Playback started with user interaction')
    } catch (e) {
      console.error('Failed to start playback:', e)
      error.value = 'Failed to start playback'
    }
  }
}

// Toggle mute
const toggleMute = () => {
  if (videoPlayer.value) {
    isMuted.value = !isMuted.value
    videoPlayer.value.muted = isMuted.value
  }
}

// Show/hide overlay controls
const showControls = () => {
  showOverlay.value = true
  overlayVisible.value = true
  
  if (hideTimer) clearTimeout(hideTimer)
  
  hideTimer = setTimeout(() => {
    overlayVisible.value = false
    setTimeout(() => {
      showOverlay.value = false
    }, 500)
  }, 3000)
}

// Video event handlers with logging
const onCanPlay = async () => {
  console.log('🎬 Video can play event triggered')
  if (videoPlayer.value) {
    // Try unmuted autoplay
    console.log('🔊 Attempting unmuted autoplay...')
    videoPlayer.value.muted = false
    videoPlayer.value.volume = 1.0
    try {
      await videoPlayer.value.play()
      console.log('✅ Video playing successfully')
    } catch (e) {
      console.warn('⚠️ Autoplay failed:', e.message)
      // If it fails, show interaction button
      needsInteraction.value = true
    }
  }
}

const onVideoReady = () => {
  console.log('🎥 Video ready event - loadeddata')
  console.log('Video element state:', {
    readyState: videoPlayer.value?.readyState,
    networkState: videoPlayer.value?.networkState,
    paused: videoPlayer.value?.paused,
    muted: videoPlayer.value?.muted,
    volume: videoPlayer.value?.volume,
    srcObject: videoPlayer.value?.srcObject
  })
  loading.value = false
  error.value = ''
}

const onVideoError = (e) => {
  console.error('❌ Video error event:', e)
  if (videoPlayer.value) {
    console.error('Video error details:', {
      error: videoPlayer.value.error,
      errorCode: videoPlayer.value.error?.code,
      errorMessage: videoPlayer.value.error?.message
    })
  }
  error.value = 'Video playback error'
  loading.value = false
}

const retryConnection = () => {
  error.value = ''
  connectWebRTC()
}

// Channel controls
const channelUp = async () => {
  try {
    await axios.post(`${API}/player/channels/up`)
    await fetchCurrent()
    showControls()
  } catch (error) {
    console.error('Channel up failed:', error)
  }
}

const channelDown = async () => {
  try {
    await axios.post(`${API}/player/channels/down`)
    await fetchCurrent()
    showControls()
  } catch (error) {
    console.error('Channel down failed:', error)
  }
}

const fetchCurrent = async () => {
  try {
    const res = await axios.get(`${API}/player/channels/current`)
    if (res.data.channel_number >= 0) {
      currentChannel.value = res.data.channel_number
      directChannel.value = res.data.channel_number
    }
  } catch (error) {
    console.error('Failed to fetch current channel:', error)
  }
}

const tuneToChannel = async (channel) => {
  try {
    await axios.post(`${API}/player/channel`, {
      command: "direct",
      channel: channel
    })
    await fetchCurrent()
  } catch (error) {
    console.error('Failed to tune to channel:', error)
  }
}

const tuneDirect = () => {
  if (directChannel.value > 0) {
    tuneToChannel(directChannel.value)
    showControls()
  }
}

const exitFullscreen = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    window.close()
  }
}

// Keyboard controls
const handleKeypress = (event) => {
  switch(event.key) {
    case 'ArrowUp':
    case '+':
      channelUp()
      break
    case 'ArrowDown':
    case '-':
      channelDown()
      break
    case 'Escape':
      exitFullscreen()
      break
    case ' ':
      showControls()
      event.preventDefault()
      break
    case 'm':
      toggleMute()
      break
  }
}

onMounted(async () => {
  console.log('🚀 Component mounted, starting initialization...')
  
  // Enable audio context early (helps with autoplay)
  console.log('🔊 Creating AudioContext for autoplay support...')
  const audioContext = new (window.AudioContext || window.webkitAudioContext)()
  console.log('AudioContext state:', audioContext.state)
  if (audioContext.state === 'suspended') {
    console.log('📢 Resuming suspended AudioContext...')
    audioContext.resume()
  }

  // Connect to WebRTC stream
  console.log('🌐 Initiating WebRTC connection...')
  await connectWebRTC()
  
  // Get channel from URL if provided
  const channelParam = route.query.channel || route.params.channel
  console.log('📺 Channel parameter from URL:', channelParam)
  
  if (channelParam) {
    const channel = parseInt(channelParam)
    if (channel > 0) {
      console.log('🔄 Tuning to channel:', channel)
      await tuneToChannel(channel)
    }
  } else {
    console.log('📡 Fetching current channel...')
    await fetchCurrent()
  }
  
  // Setup keyboard controls
  console.log('⌨️ Setting up keyboard controls')
  window.addEventListener('keydown', handleKeypress)
  
  // Show controls initially
  showControls()
  console.log('✅ Component initialization complete')
})

onUnmounted(() => {
  if (peerConnection.value) {
    peerConnection.value.close()
  }
  window.removeEventListener('keydown', handleKeypress)
  if (hideTimer) clearTimeout(hideTimer)
})
</script>