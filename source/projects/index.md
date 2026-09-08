<!DOCTYPE html>
<html>
<head>
<style>
.proj-page { max-width: 900px; margin: 0 auto; padding: 20px 0; }
.proj-intro { color: #666; font-style: italic; margin-bottom: 30px; padding-left: 12px; border-left: 3px solid #49b1f5; }
.proj-card { background: #fff; border-radius: 8px; padding: 24px 28px; margin: 0 0 28px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #eee; transition: box-shadow 0.2s, transform 0.2s; }
.proj-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.1); transform: translateY(-2px); }
.proj-card h2 { margin-top: 0; color: #2c3e50; font-size: 1.35em; border-bottom: 2px solid #49b1f5; padding-bottom: 10px; }
.proj-meta { color: #888; font-size: 0.9em; margin: 6px 0 16px 0; }
.proj-meta a { color: #49b1f5; text-decoration: none; }
.proj-meta a:hover { text-decoration: underline; }
.proj-section { margin: 16px 0; }
.proj-section-title { font-weight: 600; color: #49b1f5; margin-bottom: 6px; font-size: 0.95em; }
.proj-section ul { margin: 4px 0; padding-left: 22px; }
.proj-section li { margin: 3px 0; line-height: 1.65; }
.proj-stack { display: inline-block; background: #ecf5ff; color: #2c5282; padding: 3px 10px; border-radius: 4px; font-size: 0.82em; margin: 2px 4px 2px 0; }
.proj-note { background: #fff8e6; border-left: 3px solid #f6b73c; padding: 10px 14px; margin: 14px 0; color: #6b5b1f; font-size: 0.92em; border-radius: 0 4px 4px 0; }
.proj-think { background: #f0f9eb; border-left: 3px solid #67c23a; padding: 12px 14px; margin: 14px 0; color: #3c5a1f; font-size: 0.92em; border-radius: 0 4px 4px 0; }
.proj-think-title { font-weight: 600; color: #3c5a1f; margin-bottom: 4px; }
.proj-think-body { line-height: 1.7; }
.proj-think-body p { margin: 6px 0; }
@media (prefers-color-scheme: dark) {
  .proj-card { background: #2d2d2d; border-color: #3a3a3a; box-shadow: 0 2px 12px rgba(0,0,0,0.3); }
  .proj-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
  .proj-card h2 { color: #e0e0e0; }
  .proj-section-title { color: #5cb6ff; }
  .proj-section { color: #c0c0c0; }
  .proj-stack { background: #1a3a5c; color: #b0d4f1; }
  .proj-think { background: #1e2d1a; color: #b8d8a0; border-left-color: #67c23a; }
  .proj-think-title { color: #b8d8a0; }
  .proj-note { background: #3a3320; color: #e6c870; border-left-color: #f6b73c; }
}
</style>
</head>
<body>
<div class="proj-page">

<div class="proj-intro">
下面是我过去几年实际参与过的项目，按时间倒序排列。每个项目都尽量写清楚「我做了什么」而不是「项目有多牛」——后者的数字往往是营销话术，对面试和复盘都没什么价值。
</div>

<!-- ========== Aone 统一集成平台 ========== -->
<div class="proj-card">
<h2>1. Aone 统一集成平台</h2>
<div class="proj-meta">沈阳金建数字城市软件有限公司 · 基础研发部（2023.06 - 2026.07）· 负责人</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
公司原有二十多个业务系统（巡检、安全、应急、设备、GIS、气量、ERP、客服、营收等）跑在 .NET 单体上，各系统之间数据不通、能力不共享，每个新项目都要重复造轮子。我入职时被安排负责「把这些东西统一起来」——说白了是从零开始搭一个企业级技术中台。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>整体架构设计：选型、模块拆分、接口规范、部署拓扑</li>
<li>统一开发框架和基础中间件（认证 / RBAC / 多租户 / 菜单 / 主数据）</li>
<li>容器化和云原生部署体系搭建（Docker + K8s/K3s）</li>
<li>国产化适配：信创环境、Kingbase 数据库、国产化操作系统</li>
<li>通用能力建设：轨迹数据上传、消息通信、文件管理、定时任务</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Java</span>
<span class="proj-stack">Spring Boot</span>
<span class="proj-stack">Spring Cloud Alibaba</span>
<span class="proj-stack">MyBatis Plus</span>
<span class="proj-stack">Redis</span>
<span class="proj-stack">RabbitMQ</span>
<span class="proj-stack">XXL-JOB</span>
<span class="proj-stack">MinIO</span>
<span class="proj-stack">Docker</span>
<span class="proj-stack">Kubernetes / K3s</span>
<span class="proj-stack">MySQL</span>
<span class="proj-stack">PostgreSQL</span>
<span class="proj-stack">Kingbase</span>
</div>

<div class="proj-section">
<div class="proj-section-title">踩过的坑</div>
<ul>
<li><b>国产化适配</b>：同样的 SQL 在 Kingbase 上能跑、在 MySQL 上能跑、但 JOIN 顺序不同导致性能差几十倍；很多 ORM 生成的 SQL 都不通用，最后抽象了一层方言层</li>
<li><b>多租户数据隔离</b>：一开始用共享数据库 + 租户字段，后来发现某些查询性能扛不住，改成按租户分库 + 共享元数据，复杂度翻倍但性能稳定了</li>
<li><b>.NET 老系统的接入</b>：老的 .NET WebService 没法直接用 Spring Cloud 调，写了一堆适配层，有些老接口的字段命名能让人崩溃</li>
</ul>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这个项目做了三年，最大的体会是：<b>企业级平台最难的不是技术选型，而是「老系统怎么和平共处」</b>。你用再新的技术栈，碰到二十多个跑了好几年的老系统，也得乖乖写适配器。</p>
<p>另一个体会是「统一」这件事要克制。我前期想做「大而全」，结果第一个版本做了 80+ 模块，60% 没人用。后来砍到 30+ 核心模块，反而每个都做得更扎实。这点我后来在技术文章里专门写过：<a href="/2026/02/19/bc3de5af/">《企业级微服务基础平台怎么设计》</a>。</p>
</div>
</div>

<div class="proj-section">
<div class="proj-section-title">实际成果（简历里写过的真实数据）</div>
<ul>
<li>累计支撑 <b>30+ 项目、200+ 系统集成</b>（这是简历原文里的真实数字，不是估算）</li>
<li>完成公司从 .NET 单体到 Java 微服务 + 云原生的整体转型</li>
<li>把多个项目的重复开发成本降下来（具体比例我没统计过，不编）</li>
</ul>
</div>
</div>

<!-- ========== 设备目标识别 ========== -->
<div class="proj-card">
<h2>2. 设备目标识别（YOLOv5 落地）</h2>
<div class="proj-meta">沈阳金建数字城市软件有限公司 · 基础研发部（2023.06 - 2026.07）· 指导参与</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
巡检人员去现场拍调压箱、井盖这些设备，回来人工检查拍照是否符合规范。但人工检查不靠谱——拍糊了、角度不对、漏拍的情况太常见。客户希望自动识别出来。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>指导数据团队完成图片筛选、清洗、标注流程</li>
<li>参与模型选型、训练、评估、持续优化</li>
<li>负责服务端推理服务搭建（Flask / FastAPI）</li>
<li>设计 CPU / GPU / NPU 三种部署方案，应对不同项目现场环境</li>
<li>协助 Android 端离线模型集成</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Python</span>
<span class="proj-stack">YOLOv5</span>
<span class="proj-stack">PyTorch</span>
<span class="proj-stack">Flask</span>
<span class="proj-stack">FastAPI</span>
<span class="proj-stack">OpenCV</span>
<span class="proj-stack">CPU/GPU/NPU</span>
<span class="proj-stack">Android</span>
</div>

<div class="proj-section">
<div class="proj-section-title">踩过的坑</div>
<ul>
<li><b>数据标注质量</b>：2 万张图听起来不多，但设备种类多、场景复杂，第一版标注质量差到模型根本训不出来。后来重新制定了标注规范、加了质检流程</li>
<li><b>现场环境</b>：实验室 GPU 跑得好好的模型，到现场推理延迟 1.2 秒+，客户无法接受。最后做了蒸馏 + INT8 量化 + 动态分辨率适配</li>
<li><b>离线场景</b>：有些项目现场没网络，必须本地推理，Android 端做了 TFLite 转换，遇到了 NMS 不兼容的问题</li>
</ul>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这是我第一次完整跑通「数据 → 训练 → 部署 → 业务落地」的链路。最大的教训是：<b>AI 项目的 80% 工作量在数据和场景适配，不在模型本身</b>。YOLOv5 网上教程一大堆，但真正让你加班到凌晨 3 点的是「现场网络抖动怎么 fallback」「客户给的图片和训练集分布不一致怎么办」这些破事。</p>
<p>另外「CPU / GPU / NPU 三套部署方案」这个设计一开始我也觉得过度设计，后来发现不同项目现场的基础设施差异巨大（有的现场有 GPU 服务器、有的只有边缘盒子、有的连工控机都算奢侈品），不做适配就根本无法推广。这块的经验我专门写过一篇：<a href="/2026/06/22/6193652a/">《YOLOv5 目标识别实践》</a>。</p>
</div>
</div>

<div class="proj-section">
<div class="proj-section-title">实际成果（简历里写过的真实数据）</div>
<ul>
<li>筛选、清洗、标注 <b>约 2 万张真实巡检设备图片</b>（简历原文数据）</li>
<li>在多个巡检项目中实际落地</li>
<li>具体的「准确率提升 X%」「延迟降到 Y ms」我没有现场严格统计过，不写</li>
</ul>
</div>
</div>

<!-- ========== 气量智能问数 ========== -->
<div class="proj-card">
<h2>3. 气量智能问数（Dify + LangChain / Text-to-SQL）</h2>
<div class="proj-meta">沈阳金建数字城市软件有限公司 · 基础研发部（2023.06 - 2026.07）· 主要设计者</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
气量系统（燃气行业的抄表 / 营收系统）客户经常提新的数据统计需求，但每个需求都要定制开发。后来客户开始问「能不能直接用自然语言问？」——这就是这个项目的起因。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>整体方案设计：Dify 编排 + LangChain 工具调用 + 业务数据动态 Schema 接入</li>
<li>业务表关系抽取、字段注释、同义词库建设（这块是质量上限的关键）</li>
<li>SQL 校验、执行、错误反馈、自动重试机制</li>
<li>权限控制：AI 只能查到当前用户有权限的表和行</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Dify</span>
<span class="proj-stack">LangChain</span>
<span class="proj-stack">LLM</span>
<span class="proj-stack">Prompt Engineering</span>
<span class="proj-stack">Agent</span>
<span class="proj-stack">Tool Calling</span>
<span class="proj-stack">MySQL</span>
<span class="proj-stack">PostgreSQL</span>
</div>

<div class="proj-section">
<div class="proj-section-title">踩过的坑</div>
<ul>
<li><b>Schema 注入不能一次给完</b>：几百张业务表一次性塞给模型，token 爆了、效果也差。改成按用户问题动态检索相关表 + 字段，效果显著提升</li>
<li><b>SQL 安全</b>：必须做严格的 SQL 解析 + 白名单校验，曾经测试时发现模型生成的 SQL 把 DROP TABLE 都能编出来……吓出一身冷汗</li>
<li><b>复杂 JOIN</b>：超过 3 张表 JOIN 时，模型经常搞错关联字段，必须把表关系图 + 业务术语库都注入</li>
<li><b>同义词</b>：客户说「用户数」和业务表里的「客户数」「账号数」是同一个东西，这些必须建同义词库，否则模型抓瞎</li>
</ul>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这个项目让我真正理解了「企业级 AI 应用」和「Demo 级 AI 应用」的区别。Demo 里一句话问、模型答、看起来很美好；真实场景里要面对<b>数据权限、业务语义、SQL 安全、错误重试、性能稳定性</b>这一堆工程化问题。</p>
<p>另外 Dify 这种 Workflow 工具很好用，但不能解决所有问题。复杂业务逻辑必须用 LangChain / Python 写代码。我后来专门写过：<a href="/2026/06/30/76163760/">《气量智能问数：Dify + LangChain / Text-to-SQL 实战》</a>，里面有更详细的踩坑记录。</p>
<p>还有一点：<b>「AI 让业务人员不用懂技术」是宣传话术</b>，真实情况是「业务人员还是要懂业务、还是要能描述清楚问题」。我们的项目能做到的是「让 80% 的常规问数需求不用再提单」，剩下 20% 还是要人介入。这个预期管理对项目成败很关键。</p>
</div>
</div>
</div>

<!-- ========== 品高云 Stack ========== -->
<div class="proj-card">
<h2>4. 品高云 Stack 超融合私有云平台</h2>
<div class="proj-meta">广州市品高软件股份有限公司 · 云架构产品部（2022.06 - 2023.06）· 核心模块负责人</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
品高云是公司已有的产品，我入职时正处于从「能用」到「生产可用」的迭代期。我被分到计算虚拟化组，负责核心模块的设计和实现。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>计算虚拟化核心模块：基于 KVM / QEMU / Libvirt 实现虚拟机全生命周期管理（创建 / 启动 / 停止 / 资源配置）</li>
<li>MySQL 高可靠：针对断电、弱网、异常重启等极端场景设计恢复方案</li>
<li>第三方存储厂商对接：不同存储产品的资源管理适配</li>
<li>SDN 网络能力对接：理解计算、存储、网络三类基础资源的协同关系</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Golang (Gin)</span>
<span class="proj-stack">Erlang</span>
<span class="proj-stack">MySQL</span>
<span class="proj-stack">etcd</span>
<span class="proj-stack">KVM</span>
<span class="proj-stack">QEMU</span>
<span class="proj-stack">Libvirt</span>
<span class="proj-stack">Ceph</span>
</div>

<div class="proj-section">
<div class="proj-section-title">踩过的坑</div>
<ul>
<li><b>虚拟化没有「软删除」</b>：一个 vm destroy 命令下去是真的不可逆的，UI 上要做大量二次确认 + 操作审计</li>
<li><b>Libvirt 的 Python 和 Go 绑定坑多</b>：版本兼容性、事件回调、连接池管理都是血泪教训</li>
<li><b>极端场景测试</b>：断电测试我们搭了一个能随机断电的测试机柜，连续跑了两周才敢上线</li>
</ul>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这段经历对我影响很大。云计算底层不像业务系统那样「试错成本低」——你写错一个 libvirt 调用，可能直接把客户生产环境里的虚拟机搞挂。</p>
<p>所以这一年里我最大的成长是<b>对「破坏性操作」的敬畏</b>。每个 API 都要考虑幂等性、回滚路径、操作审计。这习惯后来在所有后端项目里都帮了我大忙。</p>
<p>这块的细节我后来在 <a href="/2026/05/21/2e1728e8/">《Go + KVM / libvirt 虚拟机管理实践》</a> 里专门写过一篇文章。</p>
</div>
</div>
</div>

<!-- ========== 优测 ========== -->
<div class="proj-card">
<h2>5. 优测自动化测试平台</h2>
<div class="proj-meta">腾讯无线大连研发中心 · 安全中心（2020.12 - 2022.06）· 参与开发</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
面向企业内部的研发和测试场景的自动化测试平台，覆盖接口、UI、性能、Mock、监控等能力。我参与时平台已经在迭代中，主要做功能开发和部署优化。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>参与 Web 自动化测试能力开发（Selenium / uiautomator）</li>
<li>接口管理、Mock 服务、接口监控等模块</li>
<li>负责部署流程优化</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Golang (Beego)</span>
<span class="proj-stack">Java (Spring Boot)</span>
<span class="proj-stack">Python (uiautomator/Selenium)</span>
<span class="proj-stack">MySQL</span>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这是我职业生涯里第一段「正经」的后端开发经历。当时对 Go、Java、Python 三种语言混用在同一个项目里感觉很神奇，后来才慢慢习惯多语言协作。</p>
<p>最大的收获是学会了<b>「在大型互联网企业研发体系里写代码」</b>——code review、规范流程、文档要求都比我之前做的小项目严格得多。这段经历让我养成了工程化习惯。</p>
</div>
</div>
</div>

<!-- ========== 腾讯 SOC ========== -->
<div class="proj-card">
<h2>6. 腾讯安全运营中心 SOC</h2>
<div class="proj-meta">腾讯无线大连研发中心 · 安全中心（2020.12 - 2022.06）· 工单模块独立开发</div>

<div class="proj-section">
<div class="proj-section-title">项目背景</div>
面向政企客户的云上安全运营平台，采集多源日志做风险检测、流量入侵检测、敏感信息监测等。我负责工单模块的后台开发。
</div>

<div class="proj-section">
<div class="proj-section-title">我的职责</div>
<ul>
<li>独立负责工单模块：需求分析、接口设计、数据库设计、核心实现</li>
<li>基于 Golang (Gin) 完成高并发接口开发</li>
<li>参与 Elasticsearch 海量日志检索相关业务</li>
<li>为大屏 / 前端提供数据聚合 API</li>
</ul>
</div>

<div class="proj-section">
<div class="proj-section-title">技术栈</div>
<span class="proj-stack">Golang (Gin)</span>
<span class="proj-stack">Python (Flask)</span>
<span class="proj-stack">Elasticsearch</span>
<span class="proj-stack">MySQL</span>
</div>

<div class="proj-think">
<div class="proj-think-title">一些个人反思</div>
<div class="proj-think-body">
<p>这是我第一次真正接触<b>「高并发 / 分布式」</b>概念。工单模块在客户现场每天处理几万条工单，之前没优化的接口在高负载下直接 OOM。</p>
<p>这段经历让我明白：<b>书上的「高并发」和真实业务的「高并发」是两回事</b>。真实场景里你要考虑的边界条件（脏数据、并发重试、用户操作冲突）比任何教科书都多。</p>
</div>
</div>
</div>

<div class="proj-note">
<b>说明</b>：项目页面只列了主要负责的项目。其他涉及政府 / 能源 / 运营商行业的项目受保密协议约束不便公开，更多细节在简历 PDF 中（<a href="/downloads/gaoxiaozhuang-resume.pdf">下载 PDF</a>）。<br>
本文涉及的所有量化数据（如「30+ 项目」「2 万张图」「部署效率提升约 80%」）均来自简历原文，<b>不来自估算或营销话术</b>。文中没有写出的数字（比如「准确率」「延迟」「QPS」），是因为我<b>没有严格的现场数据，不编</b>。
</div>

</div>
</body>
</html>
