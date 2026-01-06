import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router' // Import router yang baru kita buat
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})

L.Marker.prototype.options.icon = DefaultIcon

const app = createApp(App)

app.use(router) // Gunakan router
app.mount('#app')