<template>
  <div ref="chartRef" class="chart-container" :style="{ width: width, height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface BarDataItem {
  name: string
  value: number
}

interface Props {
  data: BarDataItem[]
  title?: string
  width?: string
  height?: string
  colors?: string[]
  horizontal?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  width: '100%',
  height: '300px',
  colors: ['#4A90E2', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
  horizontal: false
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
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#E4E7ED',
      textStyle: { color: '#303133' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: props.horizontal ? {
      type: 'value',
      axisLine: { lineStyle: { color: '#E4E7ED' } },
      axisLabel: { color: '#606266' }
    } : {
      type: 'category',
      data: props.data.map(item => item.name),
      axisLine: { lineStyle: { color: '#E4E7ED' } },
      axisLabel: { color: '#606266' }
    },
    yAxis: props.horizontal ? {
      type: 'category',
      data: props.data.map(item => item.name),
      axisLine: { lineStyle: { color: '#E4E7ED' } },
      axisLabel: { color: '#606266' }
    } : {
      type: 'value',
      axisLine: { lineStyle: { color: '#E4E7ED' } },
      axisLabel: { color: '#606266' },
      splitLine: { lineStyle: { color: '#E4E7ED', type: 'dashed' } }
    },
    series: [{
      name: '正确率',
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: props.colors[0] },
          { offset: 1, color: props.colors[0] + '80' }
        ])
      },
      data: props.data.map((item, index) => ({
        value: item.value,
        itemStyle: { color: props.colors[index % props.colors.length] }
      }))
    }]
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance?.resize()
}

watch(() => props.data, () => {
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