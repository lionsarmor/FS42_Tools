// src/store/channels.js
import { defineStore } from "pinia"
import axios from "axios"

const API = "http://127.0.0.1:4343"

export const useChannelsStore = defineStore("channels", {
  state: () => ({
    channels: []
  }),

  actions: {
    // === Channels ===
    async fetchChannels() {
      try {
        const res = await axios.get(`${API}/channels`)
        this.channels = res.data

        // also fetch empty folders
        const emptyRes = await axios.get(`${API}/channels-empty-folders`)
        const emptyMap = emptyRes.data

        this.channels = this.channels.map(ch => ({
          ...ch,
          emptyFolders: emptyMap[ch.name] || []
        }))
      } catch (err) {
        console.error("Failed to fetch channels", err)
        this.channels = []
      }
    },

    async addChannel(stationConf) {
      // stationConf = full station_conf object
      await axios.post(`${API}/channels`, { station_conf: stationConf })
      await this.fetchChannels()
    },

    async updateChannel(oldName, stationConf) {
      // oldName = string, stationConf = full station_conf object
      await axios.put(
        `${API}/channels/${encodeURIComponent(oldName)}`,
        { station_conf: stationConf }
      )
      await this.fetchChannels()
    },

    async deleteChannel(name) {
      await axios.delete(`${API}/channels/${encodeURIComponent(name)}`)
      await this.fetchChannels()
    },

    // === Schedules ===
    async fetchSchedule(name) {
      const res = await axios.get(`${API}/channels/${encodeURIComponent(name)}/schedule`)
      return res.data // { schedule, tags, tag_colors }
    },

    async replaceSchedule(name, schedule) {
      await axios.put(
        `${API}/channels/${encodeURIComponent(name)}/schedule`,
        schedule
      )
      await this.fetchChannels()
    },

    async patchSlot(name, day, hour, slot) {
      await axios.patch(
        `${API}/channels/${encodeURIComponent(name)}/schedule/${day}/${hour}`,
        slot
      )
      await this.fetchChannels()
    },

    // === Bumps ===
    async fetchBumpFiles(name) {
      const res = await axios.get(`${API}/channels/${encodeURIComponent(name)}/bump`)
      return res.data || []
    }
  }
})
