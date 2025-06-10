<template>
  <div>
    <video ref="video" autoplay></video>
    <button @click="captureAndDetect">Detect Trash</button>
    <div v-if="result">Detected: {{ result }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const video = ref(null)
const result = ref(null)

onMounted(() => {
  navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.value.srcObject = stream
  })
})

const captureAndDetect = async () => {
  const canvas = document.createElement('canvas')
  canvas.width = video.value.videoWidth
  canvas.height = video.value.videoHeight
  canvas.getContext('2d').drawImage(video.value, 0, 0)

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg'))

  const formData = new FormData()
  formData.append('file', blob, 'frame.jpg')

  const res = await fetch('http://127.0.0.1:8000/detect', {
    method: 'POST',
    body: formData,
  })
  const json = await res.json()
  result.value = json.result || 'No trash detected'
}
</script>
