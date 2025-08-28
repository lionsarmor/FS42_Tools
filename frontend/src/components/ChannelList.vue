<template>
  <div>
    <!-- Header row -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Channels</h2>
      <div class="flex space-x-2">
        <!-- Add Channel -->
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

        <!-- Add Videos -->
        <button
          @click="openFileManager()"
          class="flex items-center px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-500"
        >
          <FolderPlus class="w-4 h-4 mr-1" />
          Add Videos
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
            <th class="px-3 py-2 text-center w-32">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="ch in channels"
            :key="ch.name"
            class="border-t border-brand-muted"
          >
            <td class="px-3 py-2 truncate">{{ ch.name }}</td>
            <td class="px-3 py-2">{{ ch.config.channel_number }}</td>
            <td class="px-3 py-2 capitalize">{{ ch.config.network_type || "standard" }}</td>

            <!-- Tags summary -->
            <td class="px-3 py-2 text-xs text-gray-400 leading-tight">
              <span v-if="Array.isArray(ch.config.tags) && ch.config.tags.length">
                {{ ch.config.tags.join(", ") }}
              </span>
              <span v-else>—</span>
            </td>

            <!-- Commercial free flag -->
            <td class="px-3 py-2 text-center">
              <span v-if="ch.config.commercial_free">✅</span>
              <span v-else>❌</span>
            </td>

            <!-- Signoff / Off-air -->
            <td class="px-3 py-2 text-xs text-gray-400 leading-tight">
              <div v-if="ch.config.signoff_path">
                {{ filename(ch.config.signoff_path) }}
              </div>
              <div v-if="ch.config.off_air_path">
                {{ filename(ch.config.off_air_path) }}
              </div>
              <div
                v-if="!ch.config.signoff_path && !ch.config.off_air_path"
                class="text-red-400"
              >
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
                <!-- Edit Config -->
                <button
                  class="w-10 h-10 flex items-center justify-center bg-blue-600 text-white rounded hover:bg-blue-500"
                  @click="openForm(ch)"
                  title="Edit Config"
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

    <!-- Channel form modal -->
    <ChannelFormModal
      v-if="showForm"
      :channel="editingChannel"
      @close="closeForm"
      @saved="reload"
    />

    <!-- Weather channel form modal -->
    <WeatherChannelModal
      v-if="showWeatherForm"
      @close="closeWeatherForm"
      @saved="reload"
    />

    <!-- File manager modal -->
    <FileManagerModal
      v-if="showFileManager"
      :channel="fileManagerChannel"
      @close="closeFileManager"
      @imported="reload"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { useChannelsStore } from "../store/channels"
import ChannelFormModal from "./ChannelFormModal.vue"
import WeatherChannelModal from "./WeatherChannelModal.vue"
import FileManagerModal from "./FileManagerModal.vue"

import { 
  Pencil, Calendar, Trash2, 
  Plus, Cloud, FolderPlus, PlayCircle, Flame 
} from "lucide-vue-next"

const store = useChannelsStore()
const channels = ref([])

const showForm = ref(false)
const showWeatherForm = ref(false)
const showFileManager = ref(false)
const editingChannel = ref(null)
const fileManagerChannel = ref(null)

const API = "http://127.0.0.1:4343"

const filename = (path) => {
  if (!path) return ""
  return path.split("/").pop()
}

const reload = async () => {
  await store.fetchChannels()
  channels.value = store.channels
}

const openForm = (ch = null) => {
  editingChannel.value = ch
  showForm.value = true
}
const closeForm = () => {
  showForm.value = false
  editingChannel.value = null
}

const openWeatherForm = () => {
  showWeatherForm.value = true
}
const closeWeatherForm = () => {
  showWeatherForm.value = false
}

const openFileManager = (ch) => {
  fileManagerChannel.value = ch
  showFileManager.value = true
}
const closeFileManager = () => {
  showFileManager.value = false
  fileManagerChannel.value = null
}

const deleteChannel = async (name) => {
  if (!confirm(`Delete channel ${name}?`)) return
  await store.deleteChannel(name)
  reload()
}

// === Global actions ===
const launchScanner = async () => {
  try {
    const res = await axios.post(`${API}/launch-scanner`)
    if (res.data.url) {
      window.open(res.data.url, "_blank")
    }
  } catch (err) {
    alert("Failed to launch scanner: " + err.message)
  }
}

const hotStart = async () => {
  try {
    await axios.post(`${API}/hot-start`)
    alert("Hot Start triggered!")
  } catch (err) {
    alert("Failed to run hot start: " + err.message)
  }
}

onMounted(reload)
</script>
