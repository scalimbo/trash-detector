<template>
  <div class="camera-container">
    <select v-model="selectedDeviceId" @change="startCamera">
      <option v-for="device in videoDevices" :key="device.deviceId" :value="device.deviceId">
        {{ device.label || 'Camera ' + device.deviceId }}
      </option>
    </select>

    <video ref="video" v-show="!showResult" autoplay playsinline muted class="camera-video"></video>
    <canvas ref="canvas" v-show="showResult" class="camera-canvas"></canvas>

    <div class="button-group">
      <button v-if="!showResult" @click="captureAndDetect">📷 Detect Trash</button>
      <button v-if="showResult" @click="resetView">🔄 Capture Again</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// ✅ Load backend API URL from .env file
const apiURL = import.meta.env.VITE_API_URL

const video = ref(null)
const canvas = ref(null)
const showResult = ref(false)
const detections = ref([])

const videoDevices = ref([])
const selectedDeviceId = ref('')

const getVideoDevices = async () => {
  const devices = await navigator.mediaDevices.enumerateDevices()
  videoDevices.value = devices.filter((device) => device.kind === 'videoinput')

  // Prefer back camera if available
  const backCam = videoDevices.value.find((d) => /back|rear|environment/i.test(d.label))
  selectedDeviceId.value = backCam?.deviceId || videoDevices.value[0]?.deviceId || ''
}

const startCamera = async () => {
  if (!selectedDeviceId.value) return
  if (video.value?.srcObject) {
    video.value.srcObject.getTracks().forEach((track) => track.stop())
  }

  const stream = await navigator.mediaDevices.getUserMedia({
    video: { deviceId: { exact: selectedDeviceId.value } },
  })

  video.value.srcObject = stream

  video.value.onloadedmetadata = () => {
    canvas.value.width = video.value.videoWidth
    canvas.value.height = video.value.videoHeight
  }
}

onMounted(async () => {
  await getVideoDevices()
  await startCamera()
})

const captureAndDetect = async () => {
  const vid = video.value
  const can = canvas.value
  const ctx = can.getContext('2d')

  ctx.drawImage(vid, 0, 0, can.width, can.height)
  const blob = await new Promise((resolve) => can.toBlob(resolve, 'image/jpeg', 0.95))

  const formData = new FormData()
  formData.append('file', blob, 'frame.jpg')

  try {
    const response = await fetch(`${apiURL}/detect`, {
      method: 'POST',
      body: formData,
    })

    const result = await response.json()
    detections.value = result.detections || []

    ctx.clearRect(0, 0, can.width, can.height)
    ctx.drawImage(vid, 0, 0, can.width, can.height)

    ctx.lineWidth = 2
    ctx.font = '16px Arial'
    ctx.strokeStyle = 'lime'
    ctx.fillStyle = 'lime'

    detections.value.forEach((det) => {
      const [x1, y1, x2, y2] = det.bbox
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
      ctx.fillText(
        `${det.class} (${(det.confidence * 100).toFixed(1)}%)`,
        x1,
        y1 > 20 ? y1 - 5 : y1 + 15,
      )
    })

    showResult.value = true
  } catch (error) {
    console.error('Detection error:', error)
  }
}

const resetView = () => {
  showResult.value = false
}
</script>

<style scoped>
.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
}

.camera-video,
.camera-canvas {
  width: 100%;
  max-width: 480px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.button-group {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 6px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>
