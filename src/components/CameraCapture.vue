<template>
  <div class="camera-container">
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

const video = ref(null)
const canvas = ref(null)
const showResult = ref(false)
const detections = ref([])

onMounted(async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true })
  video.value.srcObject = stream

  video.value.onloadedmetadata = () => {
    canvas.value.width = video.value.videoWidth
    canvas.value.height = video.value.videoHeight
  }
})

const captureAndDetect = async () => {
  const vid = video.value
  const can = canvas.value
  const ctx = can.getContext('2d')

  ctx.drawImage(vid, 0, 0, can.width, can.height)
  const blob = await new Promise((resolve) => can.toBlob(resolve, 'image/jpeg', 0.95))

  const formData = new FormData()
  formData.append('file', blob, 'frame.jpg')

  const response = await fetch('http://127.0.0.1:8000/detect', {
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
  width: 90vw;
  max-width: 600px;
  aspect-ratio: 4 / 3;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.button-group {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 90vw;
  max-width: 600px;
}

button {
  font-size: 1.2rem;
  padding: 0.8rem 1.2rem;
  border-radius: 10px;
  border: none;
  background-color: #2e7d32;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #1b5e20;
}

/* 📱 Extra Mobile Responsiveness */
@media (max-width: 600px) {
  button {
    font-size: 1rem;
    padding: 0.7rem;
  }

  .camera-video,
  .camera-canvas {
    width: 95vw;
  }
}

/* 💻 Desktop Optimizations */
@media (min-width: 1000px) {
  .camera-container {
    padding: 2rem;
  }

  button {
    font-size: 1.3rem;
    padding: 1rem 2rem;
  }
}
</style>
