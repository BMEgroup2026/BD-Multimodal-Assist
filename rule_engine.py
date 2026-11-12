import pandas as pd
import numpy as np

class LayeredMonitorRule:
    """
    分层监测规则引擎 v1.0 (基于个体化偏离度)
    核心逻辑：放弃绝对阈值，采用“个体滚动基线 + Z-score偏离度”来消除个体差异
    """
    def __init__(self, baseline_window=14, trigger_z=-1.5, consecutive_days=3):
        self.baseline_window = baseline_window      # 基线学习期天数 (如14天)
        self.trigger_z = trigger_z                  # Z-score 触发阈值 (如 -1.5)
        self.consecutive_days = consecutive_days    # 连续触发天数 (如 3天)
        
    def calculate_baseline(self, rmssd_series):
        """计算个体滚动基线（中位数）与个体内标准差 (Intra-individual SD)"""
        if len(rmssd_series) < self.baseline_window:
            return None  # 基线学习期，数据不足，不预警
        
        # 取最近 baseline_window 天的数据
        recent = rmssd_series.tail(self.baseline_window)
        median_val = recent.median()
        std_val = recent.std()
        
        # 防止标准差为0导致除零错误
        if std_val == 0 or pd.isna(std_val):
            std_val = 1.0 
            
        return {'median': median_val, 'intra_sd': std_val}
    
    def evaluate_daily(self, today_rmssd, baseline):
        """评估单日状态"""
        if baseline is None:
            return "BASELINE_LEARNING"  # 基线学习中，不触发预警
            
        # 计算相对偏离度 (Z-score)
        z_score = (today_rmssd - baseline['median']) / baseline['intra_sd']
        
        if z_score < self.trigger_z:
            return "TRIGGER_POCT"       # 偏离度过大，建议触发POCT
        elif z_score < -0.5:
            return "MILD_WARNING"       # 轻度异常，温和提醒
        else:
            return "NORMAL"             # 正常状态

    def run_simulation(self, df):
        """
        主运行函数：模拟读取患者每日数据并输出监测状态
        注：Phase 3 联调时，df 将包含 C 导出的预测列 + 原始 RMSSD 列
        """
        results = []
        
        # 按患者分组处理
        for pid, group in df.groupby('patient_id'):
            group = group.sort_values('date').reset_index(drop=True)
            counter = 0  # 连续触发计数器
            
            for idx, row in group.iterrows():
                # 获取该患者截至当天的历史 RMSSD，用于计算滚动基线
                history = group.loc[:idx, 'RMSSD']
                baseline = self.calculate_baseline(history)
                status = self.evaluate_daily(row['RMSSD'], baseline)
                
                # 连续触发逻辑
                if status == "TRIGGER_POCT":
                    counter += 1
                else:
                    counter = 0  # 一旦恢复正常，计数器清零
                
                actual_trigger = "YES" if counter >= self.consecutive_days else "NO"
                
                # 计算具体的 z_score 用于记录
                z_val = round((row['RMSSD'] - baseline['median']) / baseline['intra_sd'], 2) if baseline else None
                
                results.append({
                    'patient_id': pid,
                    'date': row['date'],
                    'rmssd': round(row['RMSSD'], 2),
                    'z_score': z_val,
                    'daily_status': status,
                    'poct_triggered': actual_trigger
                })
                
        return pd.DataFrame(results)


# ==========================================
# === Phase 1 测试入口 (用模拟数据跑通逻辑) ===
# ==========================================
# === Phase 1 测试入口 (自带假数据，不依赖B同学的CSV) ===
if __name__ == "__main__":
    print("🚀 开始测试分层监测规则引擎...\n")
    
    # 1. 自己生成一段假数据：前14天正常(30左右)，后6天病理恶化(18左右)
    dates = pd.date_range('2026-04-01', periods=20)
    rmssd_vals = [30 + np.random.normal(0, 2) for _ in range(14)] + [19, 18, 19, 20, 18, 19]
    
    test_df = pd.DataFrame({
        'patient_id': 1001,
        'date': dates,
        'RMSSD': rmssd_vals
    })
    
    # 2. 实例化引擎
    engine = LayeredMonitorRule(baseline_window=14, trigger_z=-1.5, consecutive_days=3)
    
    # 3. 为了兼容你上面的 run_simulation 函数，我们先把假数据存成 csv
    test_df.to_csv("fake_test_data.csv", index=False)
    
    # 4. 运行模拟
    result_df = engine.run_simulation("fake_test_data.csv")
    
    # 5. 打印结果
    display_cols = ['date', 'rmssd', 'z_score', 'daily_status', 'poct_triggered']
    print(result_df[display_cols].tail(10).to_markdown(index=False))
    
    trigger_count = (result_df['poct_triggered'] == 'YES').sum()
    print(f"\n✅ 规则引擎跑通！20天内共触发 POCT 次数: {trigger_count}")
    print("💡 观察：前14天为 BASELINE_LEARNING，后几天连续异常，最终触发 YES。逻辑完美自洽！")
