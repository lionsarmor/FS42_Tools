// src/store/channels.js
import { defineStore } from "pinia"
import axios from "axios"

const API = import.meta.env.VITE_API_URL


export const useChannelsStore = defineStore("channels", {
  state: () => ({
    channels: []
  }),

  actions: {
    async fetchChannels() {
      try {
        const res = await axios.get(`${API}/channels`)
        this.channels = res.data
      } catch (err) {
        console.error("Failed to fetch channels", err)
        this.channels = []
      }
    },

    async addChannel(stationConf) {
      try {
        await axios.post(`${API}/channels`, { station_conf: stationConf })
        await this.fetchChannels()
      } catch (err) {
        console.error("Failed to add channel", err)
      }
    },

    async updateChannel(oldName, stationConf) {
      try {
        await axios.put(
          `${API}/channels/${encodeURIComponent(oldName)}`,
          { station_conf: stationConf }
        )
        await this.fetchChannels()
      } catch (err) {
        console.error(`Failed to update channel ${oldName}`, err)
      }
    },

    async deleteChannel(name) {
      try {
        await axios.delete(`${API}/channels/${encodeURIComponent(name)}`)
        await this.fetchChannels()
      } catch (err) {
        console.error(`Failed to delete channel ${name}`, err)
      }
    },

    async normalizeChannels() {
      try {
        await axios.post(`${API}/channels/normalize`)
        await this.fetchChannels()
      } catch (err) {
        console.error("Failed to normalize channels", err)
      }
    },

    async getBaseline(type) {
      try {
        const res = await axios.get(`${API}/channels/baseline/${encodeURIComponent(type)}`)
        return res.data.station_conf
      } catch (err) {
        console.error("Failed to fetch baseline", err)
        return null
      }
    },

    async fetchSchedule(name) {
      try {
        const res = await axios.get(`${API}/channels/${encodeURIComponent(name)}/schedule`)
        return res.data
      } catch (err) {
        console.error(`Failed to fetch schedule for ${name}`, err)
        return { schedule: {}, tags: [], tag_colors: {} }
      }
    },

    async patchSlot(name, day, hour, slot) {
      try {
        const res = await axios.patch(
          `${API}/channels/${encodeURIComponent(name)}/schedule/${day}/${hour}`,
          slot
        )
        return res.data
      } catch (err) {
        console.error(`Failed to patch slot for ${name}`, err)
        throw err
      }
    }
  }
})
