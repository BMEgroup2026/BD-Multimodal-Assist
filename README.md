# BD-Multimodal-Assist
基于肠-脑轴的双相情感障碍多模态辅助诊断系统


## 🏗️ 系统架构与数据流图

```mermaid
graph TD
    %% 定义样式
    classDef sensor fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef edge fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef cloud fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef app fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;

    subgraph 感知层 [端: 感知与采集]
        direction LR
        A[AD8232 心电贴片]:::sensor
        C[POCT 手持仪]:::sensor
    end

    subgraph 边缘层 [边: 规则引擎与本地缓存]
        direction LR
        B(手机 APP / 边缘网关):::edge
        D{分层监测规则引擎}:::edge
        E[(本地缓存: user_baseline)]:::edge
    end

    subgraph 云端大脑 [云: 算法与模型]
        direction LR
        G[(云端多模态数据库)]:::cloud
        H[随机森林分类模型]:::cloud
        I[SHAP 可解释性分析]:::cloud
    end

    subgraph 应用层 [端: 交互与展示]
        direction LR
        J[医生端 Dashboard<br/>自然语言辅助报告]:::app
        K[患者端 APP<br/>健康趋势与预警弹窗]:::app
    end

    %% 连线与标注
    A -->|蓝牙 BLE<br/>⚠️边缘计算: 仅上传 RR 间期(RRi), 不传原始波形| B
    C -->|蓝牙同步| B
    B --> D
    D -->|日常状态: 仅记录| E
    D -->|偏离预警: 触发 POCT| K
    D -->|数据上传| G
    G --> H
    H --> I
    I --> J
```
