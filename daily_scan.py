import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_smart_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 抓取股利數據 (這個數據最穩定)
        df_dividend = dl.taiwan_stock_dividend_result()
        # 2. 抓取基本資訊 (為了拿現價)
        df_daily = dl.taiwan_stock_daily_last()

        # 組合標題
        content = f"# 📈 台股自動化投資儀表板\n\n"
        content += f"> ✨ 系統強制更新秒數: `{now_str}`\n\n"

        if not df_dividend.empty and not df_daily.empty:
            # 計算殖利率邏輯
            latest_div = df_dividend.sort_values('date').groupby('stock_id').last()
            df_yield = pd.merge(df_daily[['stock_id', 'close']], latest_div[['stock_id', 'cash_dividend_caption']], on='stock_id')
            df_yield['yield_pct'] = (df_yield['cash_dividend_caption'].astype(float) / df_yield['close']) * 100
            
            # 篩選前 50 名
            yield_top_50 = df_yield.sort_values('yield_pct', ascending=False).head(50)
            
            content += "## 💰 高殖利率精選前 50 名\n"
            content += "| 股票代號 | 現價 | 殖利率 (%) |\n| :--- | :--- | :--- |\n"
            for _, row in yield_top_50.iterrows():
                content += f"| {row['stock_id']} | {row['close']} | **{row['yield_pct']:.2f}%** |\n"
        else:
            # 備援計畫：如果 API 真的掛了，我們至少顯示一條鼓勵訊息和目前時間
            content += "⚠️ API 目前正處於數據維護時段 (通常在週末發生)，請於下個交易日確認。"

        # 強制寫入檔案
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 寫入完成")
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ❌ 執行錯誤報告\n\n最後嘗試時間: `{now_str}`\n\n錯誤內容: {str(e)}")

if __name__ == "__main__":
    run_smart_scan()
