```markdown
# 🏫 校园双预警决策支持系统 - Campus Dual-Warning Decision Dashboard

## 📋 项目概述

**校园双预警决策支持系统**是一个专门为高中校园设计的传染病早期预警和决策支持工具。系统基于学术研究《Designing a Dual-Warning Early Alert System to Support Campus Preparedness for Common Infectious Diseases in High Schools》开发，旨在帮助学校管理者在不确定条件下做出平衡健康保护和教育连续性的决策。

### 🎯 核心理念
- **支持讨论而非自动决策** - 系统提供结构化信息，促进团队讨论
- **透明化风险评估** - 所有计算逻辑可见，避免黑箱操作
- **双维度平衡** - 同时评估健康传播风险和教育连续性风险
- **趋势导向** - 关注持续变化模式而非单日异常

## 🏗️ 系统架构

系统采用四层模块化架构，确保透明性和可维护性：

```
数据输入层 → 特征构建层 → 风险映射层 → 双预警输出层
```

### 1. **数据输入层** (Data Input Layer)
- 接收校园级聚合数据（无个体信息）
- 输入指标：缺勤率、症状分布、出勤稳定性
- 设计特点：低数据依赖、隐私友好、易于实施

### 2. **特征构建层** (Feature Construction Layer)
- **趋势强度**：将原始缺勤率转化为多日变化趋势
- **信号多样性**：分析症状报告的类别多样性
- **运营压力**：评估教学连续性可能受到的干扰
- 设计理念：强调持续变化模式，避免对单日异常值过度反应

### 3. **风险映射层** (Risk Mapping Layer)
- 基于透明规则（非机器学习）的定性评估
- **双维度输出**：
  - 健康传播风险 (Health Transmission Risk)
  - 教育连续性风险 (Educational Continuity Risk)
- **风险等级**：低 (Low)、中 (Moderate)、高 (Elevated)
- 核心优势：明确呈现潜在权衡关系，避免压缩为单一分数

### 4. **双预警输出层** (Dual-Warning Output Layer)
- 并行展示健康与教育风险同步可视化
- 提供场景分类、讨论要点、决策指导
- 支持结构化讨论，不提供自动化建议

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Streamlit 1.28+
- Pandas 2.0+
- NumPy 1.24+

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/campus-dual-warning-dashboard.git
cd campus-dual-warning-dashboard
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行应用**
```bash
streamlit run D_version3.py
```

4. **访问应用**
打开浏览器，访问 `http://localhost:8501`

### 🐳 Docker 部署
```bash
# 构建镜像
docker build -t campus-dashboard .

# 运行容器
docker run -p 8501:8501 campus-dashboard
```

## 📁 项目结构

```
campus-dual-warning-dashboard/
├── D_version3.py              # 主应用程序文件
├── requirements.txt           # Python依赖包
├── README.md                  # 项目说明文档
├── Dockerfile                 # Docker容器配置
├── .gitignore                 # Git忽略文件
├── assets/                    # 静态资源
│   ├── architecture_diagram.png
│   └── dashboard_screenshot.png
├── docs/                      # 文档目录
│   ├── user_guide.md
│   └── technical_spec.md
└── examples/                  # 示例数据
    └── sample_dataset.csv
```

## 🎯 主要功能

### 🔍 实时风险评估
- **健康传播风险**：基于缺勤趋势和症状多样性
- **教育连续性风险**：基于课堂覆盖率和教师可用性
- **三级风险等级**：低 (Low)、中 (Moderate)、高 (Elevated)

### 🎭 场景模拟
- 内置5种预定义场景
- 支持自定义参数调整
- 敏感性分析和假设测试

### 📊 决策支持
- 自动生成讨论要点
- 场景分类和应对建议
- 决策日志记录和导出

### 🔧 系统配置
- 可调整分析周期（3-14天）
- 自定义风险映射规则
- 多种数据输入模式

## 📋 使用指南

### 1. 初始设置
1. 配置分析周期和系统灵敏度
2. 选择数据输入模式（手动/上传/示例）
3. 设置校园基本信息

### 2. 日常使用流程
1. **输入数据**：每日更新校园运营指标
2. **查看评估**：检查双风险等级和趋势
3. **团队讨论**：使用生成的讨论要点
4. **记录决策**：保存重要讨论和行动计划
5. **定期回顾**：根据风险等级调整监控频率

### 3. 决策支持会议
- **快速检查**（5-10分钟）：当前风险状态
- **完整评估**（30分钟）：详细数据分析和方案讨论
- **应急响应**（随时）：紧急情况下的快速决策

## 🔧 配置说明

### 系统参数
- `analysis_period`：分析周期（3-14天）
- `sensitivity`：系统灵敏度（0.5-2.0倍）
- `data_source`：数据源（手动/上传/示例）

### 风险映射规则
系统使用透明规则进行风险评估，所有规则可在界面中查看和验证：

**健康风险规则示例：**
- 趋势强度 < 1.0 且 信号多样性 < 1.0 → 低风险
- 趋势强度 ≥ 2.5 且 信号多样性 ≥ 2.0 → 高风险

**教育风险规则示例：**
- 运营压力 < 1.5 → 低风险
- 运营压力 ≥ 2.5 → 高风险

## 🌐 部署选项

### 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run D_version3.py
```

### Streamlit Cloud 部署
1. Fork 本仓库到您的GitHub账户
2. 登录 [Streamlit Cloud](https://streamlit.io/cloud)
3. 点击 "New app"，选择本仓库
4. 设置主文件为 `D_version3.py`
5. 点击 "Deploy"

### Docker 部署
```bash
# 构建镜像
docker build -t campus-dashboard .

# 运行容器（开发模式）
docker run -p 8501:8501 -v $(pwd):/app campus-dashboard

# 运行容器（生产模式）
docker run -d -p 8501:8501 --name dashboard campus-dashboard
```

## 📈 应用场景

### 典型使用场景
1. **日常监控**：每周检查校园健康运营状况
2. **早期预警**：识别潜在风险趋势
3. **应急响应**：突发情况下的决策支持
4. **培训演练**：团队应急响应能力训练
5. **决策回顾**：事后分析和改进

### 适用对象
- **学校管理人员**
- **校医和健康团队**
- **教学运营团队**
- **安全应急团队**
- **教师代表**

## 🔒 隐私与安全

### 数据保护
- ✅ 仅使用聚合数据，无个体信息
- ✅ 本地数据处理，不外传
- ✅ 符合教育机构隐私政策

### 安全特性
- 🔐 无需敏感数据输入
- 🔐 无外部API调用
- 🔐 可本地部署，数据可控

## 🛠️ 开发与贡献

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/yourusername/campus-dual-warning-dashboard.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 贡献指南
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发路线图
- [ ] 多语言支持
- [ ] 移动端优化
- [ ] 高级数据分析功能
- [ ] API接口开发
- [ ] 第三方数据集成

## 📚 相关文档

### 学术基础
- [系统架构说明](architecture.md)
- [用户测试报告](docs/user_testing.md)

### 技术文档
- [API文档](docs/api.md)
- [部署指南](docs/deployment.md)
- [故障排除](docs/troubleshooting.md)

### 用户文档
- [快速开始指南](docs/quick_start.md)
- [管理员手册](docs/admin_guide.md)
- [最佳实践](docs/best_practices.md)

## 📞 支持与联系

### 问题反馈
- 🐛 [提交Issue](https://github.com/yourusername/campus-dual-warning-dashboard/issues)
- 💬 [讨论区](https://github.com/yourusername/campus-dual-warning-dashboard/discussions)
- 📧 邮箱支持：support@campus-dashboard.edu

### 社区支持
- 👥 用户论坛：待建立
- 🎥 视频教程：待制作
- 📖 知识库：建设中

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

### 学术指导
- 参与测试的学校团队

### 技术贡献
- Streamlit 团队提供的优秀框架
- 开源社区的各种工具和库
- CTB Poise团队成员

### 特别感谢
感谢所有参与系统测试和反馈的教育工作者，你们的宝贵意见让这个工具更加实用和有效。

---

## ⭐ 如果你觉得这个项目有用

请给我们一个 Star！ ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/campus-dual-warning-dashboard&type=Date)](https://star-history.com/#yourusername/campus-dual-warning-dashboard&Date)

---

**重要提示**：本系统是决策支持工具，不提供医疗建议或预测疫情。所有决策应由合格的校园管理人员根据专业判断做出。

**版本**：v1.0 | **最后更新**：2025年1月26日 | **维护状态**：活跃开发中
```
