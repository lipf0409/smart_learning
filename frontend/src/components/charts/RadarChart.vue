<template>
  <div ref="chartRef" class="chart-container" :style="{ width: width, height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  indicators: Array<{ name: string; max: number }>
  values: number[]
  title?: string
  width?: string
  height?: string
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '100%',
  height: '300px',
  color: '#4A90E2'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        color: '#303133',
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E4E7ED',
      textStyle: { color: '#303133' }
    },
    radar: {
      indicator: props.indicators,
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#606266',
        fontSize: 12
      },
      splitLine: {
        lineStyle: { color: '#E4E7ED' }
      },
      splitArea: {
        areaStyle: {
          color: ['#E8F4FD', '#F5F9FC', '#E8F4FD', '#F5F9FC', '#E8F4FD']
        }
      },
      axisLine: {
        lineStyle: { color: '#E4E7ED' }
      }
    },
    series: [{
      name: '知识掌握',
      type: 'radar',
      data: [{
        value: props.values,
        name: '掌握程度',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: props.color + '60' },
            { offset: 1, color: props.color + '20' }
          ])
        },
        lineStyle: {
          width: 2,
          color: props.color
        },
        itemStyle: {
          color: props.color
        }
      }]
    }]
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance?.resize()
}

watch(() => props.values, () => {
  initChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-container {
  min-height: 200px;
}
</style>