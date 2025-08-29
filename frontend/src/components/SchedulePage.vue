<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold">Schedule: {{ channelName }}</h2>
      <button
        @click="$router.push('/')"
        class="px-3 py-1 bg-brand-accent text-white rounded hover:bg-brand-accentHover"
      >
        ← Back
      </button>
    </div>

    <!-- Tag colors -->
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-2">Tag Colors</h3>
      <div class="flex flex-wrap gap-4">
        <div v-for="tag in tags" :key="tag" class="flex items-center gap-2">
          <span class="text-sm">{{ tag }}</span>
          <input
            type="color"
            :value="validColor(tagColors[tag])"
            @input="tagColors[tag] = $event.target.value"
            class="w-8 h-8 rounded border"
          />
        </div>
      </div>
    </div>

    <!-- Schedule grid -->
    <div class="grid grid-cols-8 gap-2 text-sm">
      <div></div>
      <div v-for="d in days" :key="d" class="font-bold capitalize">{{ d }}</div>

      <template v-for="hour in 24">
        <div class="font-bold">{{ hour }}h</div>
        <div
          v-for="day in days"
          :key="day + '-' + hour"
          class="p-2 border rounded cursor-pointer"
          :style="{ background: getSlotColor(day, hour) }"
          @click="openSlot(day, hour)"
        >
          <span>{{ getSlotTags(day, hour).join(', ') || 'off_air' }}</span>
        </div>
      </template>
    </div>

    <!-- Modal -->
    <ScheduleSlotModal
      v-if="slotModal && schedule[slotModal.day]"
      :day="slotModal.day"
      :hour="slotModal.hour"
      :channel="channelName"
      :tags="tags"
      :tag-colors="tagColors"
      :slot="schedule[slotModal.day]?.[slotModal.hour] || {}"
      @close="slotModal = null"
      @saved="fetchSchedule"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { useChannelsStore } from "../store/channels"
import ScheduleSlotModal from "../components/ScheduleSlotModal.vue"

const route = useRoute()
const store = useChannelsStore()
const channelName = route.params.name

const days = [
  "monday","tuesday","wednesday","thursday","friday","saturday","sunday"
]
const schedule = ref({})
const tags = ref([])
const tagColors = ref({})
const slotModal = ref(null)

const fetchSchedule = async () => {
  try {
    const res = await store.fetchSchedule(channelName)
    schedule.value = res.schedule || {}
    tags.value = res.tags || []
    tagColors.value = {
      off_air: "#ff0000",   // 🔴 red default
      signoff: "#ff7f00",   // 🟠 orange default
      ...res.tag_colors
    }
  } catch (err) {
    console.error("Failed to fetch schedule", err)
  }
}

const getSlotTags = (day, hour) =>
  schedule.value[day]?.[hour]?.tags || []

const getSlotColor = (day, hour) => {
  const tagsHere = getSlotTags(day, hour)
  if (!tagsHere.length) return "#1e2a8a" // 🔵 default for empty
  const tag = tagsHere[0]
  return validColor(tagColors.value[tag]) || "#3b52f6" // 🔵 fallback
}

function validColor(color) {
  return typeof color === "string" && /^#[0-9A-Fa-f]{6}$/.test(color)
    ? color
    : "#3b52f6"
}

const openSlot = (day, hour) => {
  if (!schedule.value[day]) return
  slotModal.value = { day, hour }
}

onMounted(fetchSchedule)
</script>
