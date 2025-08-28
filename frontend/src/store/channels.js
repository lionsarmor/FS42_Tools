// src/store/channels.js
import { defineStore } from "pinia"
import axios from "axios"

const API = "http://127.0.0.1:4343"

export const useChannelsStore = defineStore("channels", {
  state: () => ({
    channels: []
  }),
  actions: {
    async fetchChannels() {
      // load channels
      const res = await axios.get(`${API}/channels`)
      this.channels = res.data

      // load empty folders (bulk)
      try {
        const emptyRes = await axios.get(`${API}/channels-empty-folders`)
        const emptyMap = emptyRes.data
        this.channels = this.channels.map(ch => ({
          ...ch,
          emptyFolders: emptyMap[ch.name] || []
        }))
      } catch (err) {
        console.warn("Failed to fetch empty folders", err)
        this.channels = this.channels.map(ch => ({
          ...ch,
          emptyFolders: []
        }))
      }
    },

    async addChannel(ch) {
      await axios.post(`${API}/channels`, ch)
      await this.fetchChannels()
    },

    async updateChannel(oldName, ch) {
      // oldName MUST be a string, not an object
      await axios.put(`${API}/channels/${encodeURIComponent(oldName)}`, ch)
      await this.fetchChannels()
    },

    async deleteChannel(name) {
      await axios.delete(`${API}/channels/${encodeURIComponent(name)}`)
      await this.fetchChannels()
    },

    async fetchSchedule(name) {
      const res = await axios.get(`${API}/channels/${encodeURIComponent(name)}/schedule`)
      return res.data
    },

    async replaceSchedule(name, schedule) {
      await axios.put(`${API}/channels/${encodeURIComponent(name)}/schedule`, schedule)
      await this.fetchChannels()
    },

    async patchSlot(name, day, hour, slot) {
      await axios.patch(`${API}/channels/${encodeURIComponent(name)}/schedule/${day}/${hour}`, slot)
      await this.fetchChannels()
    }
  }
})
