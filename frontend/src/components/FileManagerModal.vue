<template>
  <div class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
    <div class="bg-brand-surface text-brand-text rounded-lg p-6 w-full max-w-4xl shadow-xl">
      <h3 class="text-lg font-semibold mb-4">Add Videos to Channel</h3>

      <div class="flex space-x-4">
        <!-- Left: File browser/search -->
        <div class="w-1/2 border border-brand-muted rounded p-2 flex flex-col">
          <input
            v-model="search"
            type="text"
            placeholder="Search files..."
            class="mb-2 p-2 w-full rounded bg-brand-bg border border-brand-muted text-brand-text text-sm"
          />
          <div class="flex-1 overflow-y-auto h-72">
            <div
              v-for="file in filteredFiles"
              :key="file"
              class="flex items-center justify-between px-2 py-1 hover:bg-brand-bg cursor-pointer rounded"
              :class="{ 'bg-brand-accent text-white': selectedFiles.includes(file) }"
              @click="toggleFile(file)"
            >
              <span class="truncate">{{ file }}</span>
              <span v-if="selectedFiles.includes(file)" class="text-xs">✅</span>
            </div>
          </div>
        </div>

        <!-- Right: Target folder -->
        <div class="w-1/2 border border-brand-muted rounded p-2 flex flex-col">
          <h4 class="text-sm font-semibold mb-2">Target Folder</h4>
          <div class="space-y-1">
            <label
              v-for="folder in tagFolders"
              :key="folder"
              class="flex items-center space-x-2 cursor-pointer"
            >
              <input
                type="radio"
                name="targetFolder"
                :value="folder"
                v-model="targetFolder"
              />
              <span class="capitalize">{{ folder }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-2">
        <button @click="$emit('close')" class="px-3 py-2 rounded bg-brand-muted hover:bg-gray-600">
          Cancel
        </button>
        <button
          :disabled="!canSubmit"
          @click="submit('copy')"
          class="px-3 py-2 rounded bg-brand-accent text-white hover:bg-brand-accentHover disabled:opacity-50"
        >
          Copy
        </button>
        <button
          :disabled="!canSubmit"
          @click="submit('move')"
          class="px-3 py-2 rounded bg-brand-success text-white hover:bg-green-600 disabled:opacity-50"
        >
          Move
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import axios from "axios"

const props = defineProps({
  channel: { type: Object, required: false } // Pass the current channel if needed
})
const emit = defineEmits(["close", "imported"])

const API = "http://127.0.0.1:4343"

// === State ===
const availableFiles = ref([])
const selectedFiles = ref([])
const search = ref("")
const targetFolder = ref("")

// Example tag folders, could be dynamic later
const tagFolders = ["movies", "shows", "late"]

// === Load files from backend ===
const loadFiles = async () => {
  try {
    const res = await axios.get(`${API}/runtime-files`)
    availableFiles.value = res.data.files || []
  } catch (err) {
    console.error("Failed to load runtime files:", err)
  }
}

onMounted(loadFiles)

// === Filtering files by search ===
const filteredFiles = computed(() => {
  if (!search.value) return availableFiles.value
  return availableFiles.value.filter(f =>
    f.toLowerCase().includes(search.value.toLowerCase())
  )
})

// === File selection ===
const toggleFile = (file) => {
  if (selectedFiles.value.includes(file)) {
    selectedFiles.value = selectedFiles.value.filter(f => f !== file)
  } else {
    selectedFiles.value.push(file)
  }
}

// === Validation ===
const canSubmit = computed(() => selectedFiles.value.length > 0 && targetFolder.value)

// === Submit to backend ===
const submit = async (action) => {
  if (!props.channel) {
    alert("No channel selected!")
    return
  }
  try {
    const payload = {
      files: selectedFiles.value.map(f => `${API}/runtime/${f}`), // adjust if absolute paths are needed
      target: targetFolder.value,
      action
    }
    await axios.post(`${API}/channels/${props.channel.name}/import-files`, payload)
    emit("imported")
    emit("close")
  } catch (err) {
    alert("Failed to import files: " + err.message)
  }
}
</script>
