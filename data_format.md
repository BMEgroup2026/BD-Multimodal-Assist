# 数据接口契约 (v1.0 - Phase 1 冻结)
> **提示**：本文件为全组数据交互的唯一标准。Phase 1 结束前，任何新增/修改列都必须先在此文件更新并通知全员，禁止私自更改 CSV 结构！

## 1. 合成数据集格式 (B 产出, C 读取)
**文件名**: `bipolar_synthetic_data.csv`
| 列名 | 类型 | 说明 | 示例值 |
| :--- | :--- | :--- | :--- |
| `patient_id` | int | 虚拟患者唯一 ID | 1001 |
| `date` | str | 模拟日期 (YYYY-MM-DD) | 2026-04-01 |
| `SDNN` | float | HRV 时域特征 (ms) | 35.2 |
| `RMSSD` | float | HRV 时域特征 (ms) | 28.4 |
| `CRP` | float | C 反应蛋白 (mg/L) | 2.1 |
| `IL6` | float | 白介素-6 (pg/mL) | 3.5 |
| `label` | int | 类别标签 (0=健康, 1=单相, 2=双相) | 2 |
| `HRV_z` | float | 个体化 HRV 偏离度 (Z-score) | -1.8 |
| `Inflam_z` | float | 个体化炎症偏离度 (Z-score) | 1.5 |
| `Coupling_Index`| float | 耦合偏离指数 (HRV_z * Inflam_z) | -2.7 |

## 2. 模型输出格式 (C 产出, A 读取) ⚠️ 核心契约
**文件名**: `model_prediction_daily.csv`
> **说明**：C 的模型对每个患者每天输出一行预测结果，A 的规则引擎将读取此文件结合原始 RMSSD 做分层判定。
| 列名 | 类型 | 说明 | 示例值 |
| :--- | :--- | :--- | :--- |
| `patient_id` | int | 必须与输入数据一致 | 1001 |
| `date` | str | 预测日期 (YYYY-MM-DD) | 2026-04-01 |
| `prob_healthy` | float | 健康概率 (0.0 - 1.0) | 0.05 |
| `prob_unipolar`| float | 单相抑郁概率 (0.0 - 1.0) | 0.15 |
| `prob_bipolar` | float | 双相风险概率 (0.0 - 1.0) | 0.80 |
| `pred_label` | int | 模型预测类别 (0, 1, 或 2) | 2 |

## 3. 规则引擎内部状态 (A 内部维护，供参考)
- `user_baseline_rmssd`: float (个体滚动基线中位数)
- `intra_sd_rmssd`: float (个体内标准差)
- `consecutive_days_low`: int (连续偏离天数计数器)
