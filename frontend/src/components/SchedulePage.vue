<template>
  <div class="p-4 text-brand-text bg-brand-bg min-h-screen">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button
        @click="$router.push('/')"
        class="px-3 py-1 bg-brand-surface text-brand-text rounded hover:bg-brand-muted"
      >
        ← Back
      </button>
      <h2 class="text-2xl font-semibold">Schedule for {{ channelName }}</h2>
    </div>

    <!-- Tag Colors -->
    <div v-if="availableTags.length" class="mb-6">
      <h3 class="text-lg font-medium mb-2">Tag Colors</h3>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div
          v-for="tag in availableTags"
          :key="tag"
          class="flex items-center space-x-2"
        >
          <span class="capitalize">{{ tag }}</span>
          <input
            type="color"
            v-model="tagColors[tag]"
            @change="saveTagColors"
            class="w-12 h-8 border-0 rounded cursor-pointer"
          />
        </div>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="overflow-x-auto">
      <table class="min-w-full border border-brand-muted text-sm">
        <thead>
          <tr class="bg-brand-surface text-brand-text">
            <th class="p-2 border border-brand-muted">Hour</th>
            <th
              v-for="day in days"
              :key="day"
              class="p-2 border border-brand-muted capitalize"
            >
              {{ day }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hour in 24" :key="hour">
            <td class="p-2 border border-brand-muted text-center">
              {{ hour - 1 }}:00
            </td>
            <td
              v-for="day in days"
              :key="day"
              class="p-2 border border-brand-muted text-center cursor-pointer"
              :style="slotStyle(schedule[day]?.[hour-1])"
              @click="openSlotModal(day, hour-1)"
            >
              {{ displaySlot(schedule[day]?.[hour-1]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Slot Modal -->
    <div
      v-if="showSlotModal"
      class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50"
    >
      <div
        class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-sm shadow-xl"
      >
        <h3 class="text-lg font-semibold mb-4">
          Edit {{ activeDay }} @ {{ activeHour }}h
        </h3>

        <!-- Tags -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Tags</label>
          <select
            v-model="slotForm.tags"
            multiple
            class="mt-1 p-2 border border-brand-muted bg-brand-bg rounded w-full"
          >
            <option
              v-for="tag in availableTags"
              :key="tag"
              :value="tag"
              class="capitalize"
            >
              {{ tag }}
            </option>
            <option value="off_air">Off-Air</option>
            <option value="signoff">Sign-Off</option>
          </select>
          <p class="text-xs text-gray-400 mt-1">
            Hold CTRL/CMD to select multiple
          </p>
        </div>

        <!-- Start / End bump -->
        <div class="mb-3">
          <label class="block text-sm font-medium">Start Bump Path</label>
          <input
            v-model="slotForm.start_bump"
            type="text"
            class="mt-1 p-2 border border-brand-muted bg-brand-bg rounded w-full"
          />
        </div>
        <div class="mb-3">
          <label class="block text-sm font-medium">End Bump Path</label>
          <input
            v-model="slotForm.end_bump"
            type="text"
            class="mt-1 p-2 border border-brand-muted bg-brand-bg rounded w-full"
          />
        </div>

        <!-- Actions -->
        <div class="mt-6 flex justify-end space-x-2">
          <button
            @click="closeSlotModal"
            class="px-3 py-2 rounded bg-gray-600 hover:bg-gray-500"
          >
            Cancel
          </button>
          <button
            @click="saveSlot"
            class="px-3 py-2 rounded bg-blue-700 text-white hover:bg-blue-600"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useChannelsStore } from "../store/channels"

const route = useRoute()
const store = useChannelsStore()
const channelName = route.params.name

const days = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
]
const schedule = ref({})
const availableTags = ref([])
const tagColors = ref({})

// Modal state
const showSlotModal = ref(false)
const activeDay = ref(null)
const activeHour = ref(null)
const slotForm = ref({ tags: [], start_bump: "", end_bump: "" })

// Load schedule + tags
const loadSchedule = async () => {
  schedule.value = await store.fetchSchedule(channelName)
  const ch = store.channels.find((c) => c.name === channelName)
  availableTags.value = ch?.config?.tags || []
  tagColors.value = ch?.config?.tag_colors || {}
  // Ensure all tags have a default color
  for (const tag of availableTags.value) {
    if (!tagColors.value[tag]) tagColors.value[tag] = "#5b21b6" // fallback purple
  }
}

const displaySlot = (slot) => {
  if (!slot) return "off-air"
  if (slot.event === "signoff") return "sign-off"
  if (slot.tags) return Array.isArray(slot.tags) ? slot.tags.join(", ") : slot.tags
  return "off-air"
}

const slotStyle = (slot) => {
  if (!slot) return { background: "#111827", color: "#9CA3AF" } // gray off-air
  if (slot.event === "signoff") return { background: "#991b1b", color: "white" } // red
  if (slot.tags) {
    const tag = Array.isArray(slot.tags) ? slot.tags[0] : slot.tags
    const color = tagColors.value[tag] || "#5b21b6"
    return { background: color, color: "white" }
  }
  return { background: "#111827", color: "#9CA3AF" }
}

const openSlotModal = (day, hour) => {
  activeDay.value = day
  activeHour.value = hour
  const slot = schedule.value[day]?.[hour] || {}
  slotForm.value = {
    tags: slot.tags ? (Array.isArray(slot.tags) ? slot.tags : [slot.tags]) : [],
    start_bump: slot.start_bump || "",
    end_bump: slot.end_bump || "",
  }
  showSlotModal.value = true
}

const closeSlotModal = () => {
  showSlotModal.value = false
}

const saveSlot = async () => {
  let slotData = {}
  if (slotForm.value.tags.includes("off_air")) {
    slotData = {}
  } else if (slotForm.value.tags.includes("signoff")) {
    slotData = { event: "signoff" }
  } else {
    slotData = { tags: slotForm.value.tags }
    if (slotForm.value.start_bump) slotData.start_bump = slotForm.value.start_bump
    if (slotForm.value.end_bump) slotData.end_bump = slotForm.value.end_bump
  }

  await store.patchSlot(channelName, activeDay.value, activeHour.value, slotData)
  await loadSchedule()
  closeSlotModal()
}

// Save tag colors back into channel config
const saveTagColors = async () => {
  const ch = store.channels.find(c => c.name === channelName)
  if (ch && ch.name) {
    ch.config.tag_colors = tagColors.value
    await store.updateChannel(ch)
  } else {
    console.warn("No valid channel found when saving tag colors")
  }
}

onMounted(loadSchedule)
</script>
