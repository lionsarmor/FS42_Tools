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
      const res = await axios.get(`${API}/channels`)
      this.channels = res.data
    },
    async addChannel(ch) {
      await axios.post(`${API}/channels`, ch)
      await this.fetchChannels()
    },
    async updateChannel(oldName, ch) {
      // ✅ use oldName in the URL
      await axios.put(`${API}/channels/${oldName}`, ch)
      await this.fetchChannels()
    },
    async deleteChannel(name) {
      await axios.delete(`${API}/channels/${name}`)
      await this.fetchChannels()
    },
    async fetchSchedule(name) {
      const res = await axios.get(`${API}/channels/${name}/schedule`)
      return res.data
    },
    async replaceSchedule(name, schedule) {
      await axios.put(`${API}/channels/${name}/schedule`, schedule)
      await this.fetchChannels()
    },
    async patchSlot(name, day, hour, slot) {
      await axios.patch(`${API}/channels/${name}/schedule/${day}/${hour}`, slot)
      await this.fetchChannels()
    }
  }
})
