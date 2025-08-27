import { createRouter, createWebHistory } from "vue-router"

import ChannelList from "./components/ChannelList.vue"
import SchedulePage from "./components/SchedulePage.vue"

const routes = [
  { path: "/", component: ChannelList },
  { path: "/channel/:name/schedule", component: SchedulePage, props: true },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
