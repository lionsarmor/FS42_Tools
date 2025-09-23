import { createRouter, createWebHistory } from "vue-router"
import ChannelList from "./components/ChannelList.vue"
import SchedulePage from "./components/SchedulePage.vue"
import FullscreenTV from "./components/FullscreenTV.vue"
import Remote from "./components/Remote.vue"

const routes = [
  { path: "/", component: ChannelList },
  { path: "/channel/:name/schedule", component: SchedulePage, props: true },
  { path: "/tv", component: FullscreenTV },
  { path: "/tv/:channel", component: FullscreenTV, props: true },
  { path: "/remote", component: Remote },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Redirect remote.radroddy.com to tools.radroddy.com/remote
router.beforeEach((to, from, next) => {
  const hostname = window.location.hostname
  
  if (hostname === 'remote.radroddy.com') {
    // Redirect to tools.radroddy.com/remote
    window.location.href = 'https://tools.radroddy.com/remote'
    return
  }
  
  next()
})