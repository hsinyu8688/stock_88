import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 往前抓 30 天，確保至少能抓到上週五的資料
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    try:
        # 1. 抓取數據
        df_daily = dl.taiwan_stock_daily_last()
        df_dividend = dl.taiwan_stock_dividend_result()
        
        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 系統更新時間: `{now_str}`\n\n"

        # --- 數據檢查與顯示邏輯 ---
        # 檢查 df_daily 是否有效
        if df_daily is not None and not df_daily.empty:
            # 2. 處理高殖利率邏輯
            latest_div = df_dividend.sort_values('date').groupby('stock_id').last()
            df_yield = pd.merge(df_daily[['stock_id', 'close']], latest_div[['stock_id', 'cash_dividend_caption']], on='stock_id')
            df_yield['yield_pct'] = (df_yield['cash_dividend_caption'].astype(float) / df_yield['close']) * 100
            yield_top_50 = df_yield.sort_values('yield_pct', ascending=False).head(50)

            content += "## 💰 高殖利率精選前 50 名 (Value)\n"
            content += "| 代號 | 現價 | 股利 | 殖利率 (%) |\n| :--- | :--- | :--- | :--- |\n"
            for _, row in yield_top_50.iterrows():
                content += f"| {row['stock_id']} | {row['close']} | {row['cash_dividend_caption']} | **{row['yield_pct']:.2f}%** |\n"
        else:
            content += "### 📭 數據休眠中\n"
            content += "目前 API 未回傳有效行情數據（通常發生在週末維護期）。\n"
            content += "請於 **週一 16:30** 開盤數據結算後再次查看，屆時將自動更新最新名單！"

        # 3. 寫入 README
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        # 即使報錯，也要把錯誤細節寫得很清楚，方便我們診斷
        error_type = type(e).__name__
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 系統偵測到小亂流\n\n執行時間: `{now_str}`\n\n錯誤類型: `{error_type}`\n內容: `{str(e)}`\n\n> **別擔心！這通常是週末 API 數據庫暫時離線。請等週一收盤後再來看看！**")

if __name__ == "__main__":
    run_pro_scan()
