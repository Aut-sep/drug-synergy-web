<template>
  <section class="page-section">
    <div class="page-title">
      <div>
        <h2>系统说明 / 模型说明</h2>
        <p>这一页用于说明毕业设计的软件系统边界：模型集合、分层架构、任务链路、版本资产与结果资产如何被组织为统一交付系统。</p>
      </div>
    </div>

    <div class="metric-grid">
      <div class="info-card">
        <h4>整合模型数</h4>
        <p>4 个</p>
      </div>
      <div class="info-card">
        <h4>系统形态</h4>
        <p>前后端分离 Web 软件</p>
      </div>
      <div class="info-card">
        <h4>推理状态</h4>
        <p>可闭环运行</p>
      </div>
      <div class="info-card">
        <h4>训练状态</h4>
        <p>系统完整，执行允许受限</p>
      </div>
    </div>

    <el-alert
      class="inline-alert"
      title="当前系统定位"
      description="本项目不是重写四个模型算法，而是把 DualSyn、MFSynDCP、MVCASyn、MTLSynergy 组织成统一数据包、统一推理链路、统一训练组织和统一结果展示的软件系统。"
      type="info"
      show-icon
      :closable="false"
    />

    <el-row :gutter="16">
      <el-col :xs="24" :xl="14">
        <el-card class="panel-card" shadow="never">
          <template #header>模型整合说明</template>
          <el-table :data="modelRows" size="small">
            <el-table-column prop="name" label="模型" min-width="150" />
            <el-table-column prop="role" label="系统角色" min-width="180" />
            <el-table-column prop="systemScope" label="当前系统接入方式" min-width="260" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="10">
        <el-card class="panel-card" shadow="never">
          <template #header>当前交付边界</template>
          <div class="guide-stack">
            <div class="info-card">
              <h4>已完成</h4>
              <p>数据集管理、推理任务、结果查看、任务日志、版本资产、产物下载和状态分级提示已经形成完整系统闭环。</p>
            </div>
            <div class="info-card">
              <h4>受限说明</h4>
              <p>训练执行会受到本机运行条件影响，因此允许失败；但训练创建、调度、日志、版本资产和产物说明链路保持完整可见。</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card" shadow="never">
      <template #header>系统分层架构</template>
      <div class="architecture-grid">
        <div v-for="layer in architectureLayers" :key="layer.title" class="architecture-card">
          <div class="page-caption">{{ layer.tag }}</div>
          <h3>{{ layer.title }}</h3>
          <p>{{ layer.description }}</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :xl="12">
        <el-card class="panel-card" shadow="never">
          <template #header>统一任务链路</template>
          <el-steps direction="vertical" :active="4" finish-status="success">
            <el-step title="前端发起任务" description="Vue3 前端负责参数选择、状态提示、结果查看和统一交互入口。" />
            <el-step title="后端编排请求" description="FastAPI 后端负责任务实体、接口封装、详情序列化、状态分级和下载入口。" />
            <el-step title="调用模型执行组件" description="系统按统一接口组织推理网关、训练服务组件、样本校验、日志和模型资产。" />
            <el-step title="回收结果并统一展示" description="推理结果、训练日志、版本资产和产物下载被重新组织到统一 Web 界面中。" />
          </el-steps>
        </el-card>
      </el-col>

      <el-col :xs="24" :xl="12">
        <el-card class="panel-card" shadow="never">
          <template #header>答辩可讲清的结论</template>
          <el-timeline>
            <el-timeline-item timestamp="软件系统目标">把研究型原型组织成可运行、可验证、可展示、可维护的正式软件系统。</el-timeline-item>
            <el-timeline-item timestamp="模型层策略">保持既有模型算法不重写，只做统一接入与统一组织。</el-timeline-item>
            <el-timeline-item timestamp="系统层贡献">统一数据包、统一任务中心、统一版本中心、统一结果展示和统一状态说明。</el-timeline-item>
            <el-timeline-item timestamp="受限但完整">即使训练执行受运行条件限制，系统层仍能完整表达任务、日志、版本和产物能力。</el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup lang="ts">
const modelRows = [
  { name: 'DualSyn', role: '协同预测核心模型之一', systemScope: '已接入统一推理入口、训练任务编排、版本展示和结果查看' },
  { name: 'MFSynDCP', role: '协同预测候选模型', systemScope: '作为统一模型集合的一部分纳入任务选择与系统说明' },
  { name: 'MVCASyn', role: '协同预测候选模型', systemScope: '作为统一模型集合的一部分纳入任务选择与系统说明' },
  { name: 'MTLSynergy', role: '协同预测候选模型', systemScope: '作为统一模型集合的一部分纳入任务选择与系统说明' },
]

const architectureLayers = [
  {
    tag: 'Frontend',
    title: 'Vue3 + TypeScript + Pinia',
    description: '负责页面交互、状态展示、任务入口、结果工作台、版本中心和系统说明等答辩可见界面。',
  },
  {
    tag: 'Backend',
    title: 'FastAPI + SQLAlchemy',
    description: '负责任务管理、详情聚合、下载接口、版本资产整理、健康探测和统一接口组织。',
  },
  {
    tag: 'Execution',
    title: '模型执行组件与训练服务组件',
    description: '负责推理执行、训练调度、样本校验、运行日志和模型资产输出。',
  },
  {
    tag: 'Assets',
    title: '统一数据包与版本资产',
    description: '把数据集、训练产物、推理输出和历史版本重新组织成统一可管理的软件资产。',
  },
]
</script>

<style scoped>
.guide-stack {
  display: grid;
  gap: 16px;
}

.architecture-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.architecture-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(248, 251, 255, 0.88);
  border: 1px solid rgba(99, 125, 160, 0.14);
}

.architecture-card h3 {
  margin: 8px 0;
  color: #112240;
}

.architecture-card p {
  margin: 0;
  color: #52607a;
}
</style>
