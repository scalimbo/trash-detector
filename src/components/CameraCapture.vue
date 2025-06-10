<template>
  <div>
    <video
      ref="video"
      autoplay
      playsinline
      width="400"
      height="300"
      style="position: absolute; z-index: 1"
    ></video>
    <canvas ref="canvas" width="400" height="300" style="position: absolute; z-index: 2"></canvas>
    <button @click="capture" style="position: relative; z-index: 3; margin-top: 320px">
      Detect Trash
    </button>
    <ul v-if="detections.length" style="margin-top: 360px">
      <li v-for="(d, i) in detections" :key="i">{{ d.class }} - Confidence: {{ d.confidence }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      detections: [],
    }
  },
  mounted() {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
      this.$refs.video.srcObject = stream
    })
  },
  methods: {
    capture() {
      const video = this.$refs.video
      const canvas = this.$refs.canvas
      const ctx = canvas.getContext('2d')

      // Draw video frame on canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      // Send image blob to backend
      canvas.toBlob((blob) => {
        const formData = new FormData()
        formData.append('file', blob, 'frame.jpg')

        fetch('http://localhost:8000/detect/', {
          method: 'POST',
          body: formData,
        })
          .then((res) => res.json())
          .then((data) => {
            this.detections = data.detections
            this.drawBoxes(data.detections)
          })
      }, 'image/jpeg')
    },

    drawBoxes(detections) {
      const canvas = this.$refs.canvas
      const ctx = canvas.getContext('2d')

      // Clear canvas before drawing
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(this.$refs.video, 0, 0, canvas.width, canvas.height)

      // Draw each box
      detections.forEach((d) => {
        const [x1, y1, x2, y2] = d.box

        ctx.beginPath()
        ctx.rect(x1, y1, x2 - x1, y2 - y1)
        ctx.lineWidth = 2
        ctx.strokeStyle = '#00FF00'
        ctx.stroke()

        ctx.fillStyle = 'rgba(0,0,0,0.6)'
        ctx.fillRect(x1, y1 - 20, ctx.measureText(d.class).width + 10, 20)
        ctx.fillStyle = '#FFFFFF'
        ctx.font = '14px Arial'
        ctx.fillText(`${d.class} (${d.confidence})`, x1 + 5, y1 - 5)
      })
    },
  },
}
</script>

<style scoped>
/* Optional: container style */
video,
canvas {
  border-radius: 8px;
}
</style>
