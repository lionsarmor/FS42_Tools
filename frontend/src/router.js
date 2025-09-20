import { createRouter, createWebHistory } from "vue-router"
import ChannelList from "./components/ChannelList.vue"
import SchedulePage from "./components/SchedulePage.vue"
import FullscreenTV from "./components/FullscreenTV.vue"

const routes = [
  { path: "/", component: ChannelList },
  { path: "/channel/:name/schedule", component: SchedulePage, props: true },
  { path: "/tv", component: FullscreenTV },
  { path: "/tv/:channel", component: FullscreenTV, props: true },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
