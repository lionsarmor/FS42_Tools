<template>
  <div>
    <!-- Header row -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Channels</h2>
      <div class="flex space-x-2">
        <!-- Add Standard Channel -->
        <button
          @click="openForm()"
          class="flex items-center px-3 py-2 bg-green-900 text-white rounded hover:bg-green-800"
        >
          <Plus class="w-4 h-4 mr-1" />
          Add Channel
        </button>

        <!-- Add Weather Channel -->
        <button
          @click="openWeatherForm()"
          class="flex items-center px-3 py-2 bg-blue-900 text-white rounded hover:bg-blue-800"
        >
          <Cloud class="w-4 h-4 mr-1" />
          Add Weather
        </button>

        <!-- Add Guide Channel -->
        <button
          @click="openGuideForm()"
          class="flex items-center px-3 py-2 bg-brand-accent text-white rounded hover:bg-brand-accentHover"
        >
          <BookOpen class="w-4 h-4 mr-1" />
          Add Guide
        </button>

        <!-- Launch Scanner -->
        <button
          @click="launchScanner"
          class="flex items-center px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-500"
        >
          <PlayCircle class="w-4 h-4 mr-1" />
          Scanner
        </button>

        <!-- Hot Start -->
        <button
          @click="hotStart"
          class="flex items-center px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-500"
        >
          <Flame class="w-4 h-4 mr-1" />
          Hot Start
        </button>

        <!-- Kill -->
        <button
          @click="killAll"
          class="flex items-center px-3 py-2 bg-red-700 text-white rounded hover:bg-red-600"
        >
          <Skull class="w-4 h-4 mr-1" />
          Kill
        </button>

        <!-- Normalize -->
        <button
          @click="normalizeChannels"
          class="flex items-center px-3 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-500"
        >
          <RefreshCw class="w-4 h-4 mr-1" />
          Normalize
        </button>
      </div>
    </div>

    <!-- Channel list table -->
    <div class="overflow-x-auto">
      <table class="w-full border border-brand-muted rounded shadow-sm">
        <thead class="bg-brand-surface text-brand-text">
          <tr>
            <th class="px-3 py-2 text-left w-40">Name</th>
            <th class="px-3 py-2 text-left w-20">Number</th>
            <th class="px-3 py-2 w-28">Type</th>
            <th class="px-3 py-2 w-48">Tags</th>
            <th class="px-3 py-2 w-32">Commercial Free</th>
            <th class="px-3 py-2 w-40">Sign-Off / Off-Air</th>
            <th class="px-3 py-2 w-32">Empty Folders</th>
            <th class="px-3 py-2 text-center w-48">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="ch in sortedChannels"
            :key="ch.name"
            class="border-t border-brand-muted"
          >
            <!-- Channel name -->
            <td class="px-3 py-2 truncate">{{ ch.name }}</td>

            <!-- Channel number -->
            <td
              class="px-3 py-2"
              :class="{ 'text-red-600 font-bold': duplicateNumbers.has(ch.config?.channel_number) }"
            >
              {{ ch.config?.channel_number || "—" }}
            </td>

            <!-- Type -->
            <td class="px-3 py-2 capitalize">{{ ch.config?.network_type || "standard" }}</td>

            <!-- Tags -->
            <td class="px-3 py-2 text-xs text-gray-400 leading-tight">
              <span v-if="Array.isArray(ch.config?.tags) && ch.config.tags.length">
                {{ ch.config.tags.join(", ") }}
              </span>
              <span v-else>—</span>
            </td>

            <!-- Commercial free -->
            <td class="px-3 py-2 text-center">
              <span v-if="ch.config?.commercial_free">✅</span>
              <span v-else>❌</span>
            </td>

            <!-- Signoff / Off-air -->
            <td class="px-3 py-2 text-xs text-gray-400 leading-tight">
              <div v-if="ch.config?.sign_off_video">{{ filename(ch.config.sign_off_video) }}</div>
              <div v-if="ch.config?.off_air_video">{{ filename(ch.config.off_air_video) }}</div>
              <div v-if="!ch.config?.sign_off_video && !ch.config?.off_air_video" class="text-red-400">
                None
              </div>
            </td>

            <!-- Empty Folders -->
            <td class="px-3 py-2 text-xs text-gray-400 leading-tight">
              <template v-if="ch.emptyFolders && ch.emptyFolders.length > 0">
                <div v-for="f in ch.emptyFolders" :key="f">{{ f }}</div>
              </template>
              <template v-else>
                <span class="text-green-500">✔️</span>
              </template>
            </td>

            <!-- Actions -->
            <td class="px-3 py-2 whitespace-nowrap text-center">
              <div class="flex justify-center space-x-2">
                <!-- ▶️ Play -->
                <button
                  class="w-10 h-10 flex items-center justify-center bg-green-600 text-white rounded hover:bg-green-500"
                  @click="openPlayer(ch)"
                  title="Play Channel"
                >
                  <PlayCircle class="w-5 h-5" />
                </button>

                <!-- Edit Config -->
                <button
                  v-if="ch.config?.network_type !== 'web' && ch.config?.network_type !== 'weather'"
                  class="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded hover:bg-blue-500"
                  @click="openEdit(ch)"
                  title="Edit Config"
                >
                  <Pencil class="w-5 h-5" />
                </button>

                <!-- Disabled for Weather/Web -->
                <button
                  v-else
                  class="w-10 h-10 flex items-center justify-center bg-gray-600 text-gray-300 rounded cursor-not-allowed"
                  disabled
                  title="Edit Disabled for Weather/Web Channels"
                >
                  <Pencil class="w-5 h-5" />
                </button>

                <!-- Edit Schedule -->
                <router-link
                  :to="`/channel/${ch.name}/schedule`"
                  class="w-10 h-10 flex items-center justify-center bg-brand-accent text-white rounded hover:bg-brand-accentHover"
                  title="Edit Schedule"
                >
                  <Calendar class="w-5 h-5" />
                </router-link>

                <!-- Add Videos -->
                <button
                  class="w-10 h-10 flex items-center justify-center bg-purple-600 text-white rounded hover:bg-purple-500"
                  @click="openFileManager(ch)"
                  title="Add Videos"
                >
                  <FolderPlus class="w-5 h-5" />
                </button>

                <!-- Delete -->
                <button
                  class="w-10 h-10 flex items-center justify-center bg-brand-danger text-white rounded hover:bg-red-500"
                  @click="deleteChannel(ch.name)"
                  title="Delete"
                >
                  <Trash2 class="w-5 h-5" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modals -->
    <ChannelFormModal v-if="showForm" :channel="editingChannel" @close="closeForm" @saved="reload" />
    <WeatherChannelModal v-if="showWeatherForm" :channel="editingChannel" @close="closeWeatherForm" @saved="reload" />
    <GuideChannelModal v-if="showGuideForm" :channel="editingChannel" @close="closeGuideForm" @saved="reload" />
    <FileManagerModal v-if="showFileManager" :channel="fileManagerChannel" @close="closeFileManager" @imported="reload" />
    <PlayerModal v-if="playerChannel" :start-channel="playerChannel" @close="closePlayer" />
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from "vue"
import axios from "axios"
import { useChannelsStore } from "../store/channels"

// ✅ Modals must be imported
import ChannelFormModal from "./ChannelFormModal.vue"
import WeatherChannelModal from "./WeatherChannelModal.vue"
import GuideChannelModal from "./GuideChannelModal.vue"
import FileManagerModal from "./FileManagerModal.vue"
import PlayerModal from "./PlayerModal.vue"

import {
  Pencil, Calendar, Trash2, Plus, Cloud, BookOpen, FolderPlus, PlayCircle, Flame, Skull, RefreshCw
} from "lucide-vue-next"

const store = useChannelsStore()
const channels = ref([])
const editingChannel = ref(null)
const showForm = ref(false)
const showWeatherForm = ref(false)
const showGuideForm = ref(false)
const showFileManager = ref(false)
const fileManagerChannel = ref(null)
const playerChannel = ref(null)

const API = import.meta.env.VITE_API_URL

const filename = (path) => path?.split("/").pop() || ""

// Duplicate numbers
const duplicateNumbers = computed(() => {
  const counts = {}
  channels.value.forEach(ch => {
    const num = Number(ch.config.channel_number)
    if (!num) return
    counts[num] = (counts[num] || 0) + 1
  })
  return new Set(Object.keys(counts).map(n => Number(n)).filter(n => counts[n] > 1))
})

// Sorted list
const sortedChannels = computed(() => {
  return [...channels.value].sort((a, b) => (a.config.channel_number || Infinity) - (b.config.channel_number || Infinity))
})

const reload = async () => {
  await store.fetchChannels()
  channels.value = store.channels
}

// === Modals ===
const openForm = (ch = null) => { editingChannel.value = ch; showForm.value = true }
const closeForm = () => { showForm.value = false; editingChannel.value = null }

const openWeatherForm = (ch = null) => { editingChannel.value = ch; showWeatherForm.value = true }
const closeWeatherForm = () => { showWeatherForm.value = false; editingChannel.value = null }

const openGuideForm = (ch = null) => { editingChannel.value = ch; showGuideForm.value = true }
const closeGuideForm = () => { showGuideForm.value = false; editingChannel.value = null }

const openFileManager = (ch) => { fileManagerChannel.value = ch; showFileManager.value = true }
const closeFileManager = () => { showFileManager.value = false; fileManagerChannel.value = null }

const deleteChannel = async (name) => {
  if (!confirm(`Delete channel ${name}?`)) return
  try {
    await store.deleteChannel(name)
    reload()
    alert(`🗑️ Deleted channel: ${name}`)
  } catch (err) {
    console.error(`Delete failed for ${name}`, err)
    alert(`❌ Failed to delete ${name}: ${err.message}`)
  }
}


// === Player ===
const openPlayer = (ch) => { playerChannel.value = ch.config?.channel_number || 1 }
const closePlayer = () => { playerChannel.value = null }

// === Edit ===
const openEdit = (ch) => {
  editingChannel.value = ch
  const type = ch.config?.network_type || "standard"
  if (type === "guide") showGuideForm.value = true
  else if (type === "weather") showWeatherForm.value = true
  else showForm.value = true
}

// === Global backend actions ===
const launchScanner = async () => {
  // open a blank tab immediately (keeps popup blocker happy)
  const newTab = window.open("about:blank", "_blank")

  try {
    const res = await axios.post(`${API}/scanner`)
    const url = res.data.url || "http://127.0.0.1:4242/"
    const pid = res.data.pid || "?"

    alert(`📡 Scanner starting (PID ${pid})`)

    // small wait to let backend spin up
    setTimeout(() => {
      if (newTab) newTab.location.href = url
    }, 5000)
  } catch (err) {
    console.error("Scanner failed", err)
    if (newTab) newTab.close()
    alert("❌ Failed to start scanner")
  }
}

const hotStart = async () => {
  try {
    const res = await axios.post(`${API}/hot-start`)
    const pid = res.data?.pid || "?"
    alert(`🔥 Hot start triggered (PID ${pid})`)
  } catch (err) {
    console.error("Hot start failed", err)
    alert("❌ Failed to hot start")
  }
}


// === Kill ===
const killAll = async () => {
  try {
    const res = await axios.post(`${API}/kill`)
    console.log("Kill response:", res.data)

    // 💀 Skull added to popup message
    alert(
      `💀 Kill Triggered!\n\n` +
      `Status: ${res.data.status}\n\n` +
      `Output:\n${res.data.stdout || "(no stdout)"}\n\n` +
      `Errors:\n${res.data.stderr || "(no stderr)"}\n\n` +
      `Exit Code: ${res.data.returncode}`
    )
  } catch (err) {
    console.error("Kill failed:", err)
    alert("💀 Kill failed – check backend logs")
  }
}


const normalizeChannels = async () => {
  try {
    const res = await axios.post(`${API}/channels/normalize`)
    alert(`✅ Normalized channels: ${res.data.updated.join(", ")}`)
    reload()
  } catch (err) {
    console.error("Normalize failed", err)
    alert("❌ Failed to normalize channels")
  }
}

onMounted(reload)
</script>
