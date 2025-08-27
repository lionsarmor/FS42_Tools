<template>
  <div>
    <!-- Header row -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold">Channels</h2>
      <div class="space-x-2">
        <button
          @click="openForm()"
          class="px-4 py-2 bg-green-900 text-white rounded hover:bg-green-800"
        >
          + Add Channel
        </button>
        <button
          @click="openWeatherForm()"
          class="px-4 py-2 bg-blue-900 text-white rounded hover:bg-blue-800"
        >
          + Add Weather Channel
        </button>
      </div>
    </div>

    <!-- Channel list table -->
    <table class="w-full border border-brand-muted rounded shadow-sm">
      <thead class="bg-brand-surface text-brand-text">
        <tr>
          <th class="px-3 py-2 text-left">Name</th>
          <th class="px-3 py-2 text-left">Number</th>
          <th class="px-3 py-2">Type</th>
          <th class="px-3 py-2">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ch in channels" :key="ch.name" class="border-t border-brand-muted">
          <td class="px-3 py-2">{{ ch.name }}</td>
          <td class="px-3 py-2">{{ ch.config.channel_number }}</td>
          <td class="px-3 py-2 capitalize">{{ ch.config.network_type || "standard" }}</td>
          <td class="px-3 py-2 space-x-2">
            <button
              class="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-500 text-sm"
              @click="openForm(ch)"
            >
              Edit Config
            </button>
            <router-link
              :to="`/channel/${ch.name}/schedule`"
              class="px-2 py-1 bg-brand-accent text-white rounded hover:bg-brand-accentHover text-sm"
            >
              Edit Schedule
            </router-link>
            <button
              class="px-2 py-1 bg-brand-danger text-white rounded hover:bg-red-500 text-sm"
              @click="deleteChannel(ch.name)"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

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
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useChannelsStore } from "../store/channels"
import ChannelFormModal from "./ChannelFormModal.vue"
import WeatherChannelModal from "./WeatherChannelModal.vue"

const store = useChannelsStore()
const channels = ref([])

const showForm = ref(false)
const showWeatherForm = ref(false)
const editingChannel = ref(null)

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

const deleteChannel = async (name) => {
  if (!confirm(`Delete channel ${name}?`)) return
  await store.deleteChannel(name)
  reload()
}

onMounted(reload)
</script>
