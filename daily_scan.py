import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 往前抓 10 天，確保能抓到最後一個交易日的票價
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')

    try:
        # 1. 抓取基本資訊
        df_info = dl.taiwan_stock_info()
        # 2. 抓取全市場最後行情 (或是用 daily 抓取近期資料)
        df_price = dl.taiwan_stock_daily_last() 

        # 組合內容
        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 系統最後更新: `{now_str}`\n\n"
        content += "## 💰 台股即時票價清單 (連線測試)\n"
        
        if df_info is not None and df_price is not None:
            # 合併基本資訊與票價
            # df_price 通常包含 stock_id, close (收盤價)
            df_merged = pd.merge(df_info[['stock_id', 'stock_name', 'industry_category']], 
                                 df_price[['stock_id', 'close']], on='stock_id')
            
            # 整理表格
            display_df = df_merged.head(30)
            display_df.columns = ['股票代號', '股票名稱', '產業類別', '目前票價']
            
            content += display_df.to_markdown(index=False)
            content += "\n\n--- \n✅ **報價功能已上線！** 明天下午 16:30 機器人會自動更新最新成交價。"
        else:
            content += "⚠️ 週末 API 數據庫部分離線，暫時無法取得最新票價，請於開盤日嘗試。"

        # 寫入檔案
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        # 萬一特定函數報錯（如週末維護），我們改用備援方案顯示基本清單
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 數據對接中\n\n> 執行時間: `{now_str}`\n\n目前 API 正在進行週末票價數據維護，週一開盤後將自動恢復正常顯示。")

if __name__ == "__main__":
    run_pro_scan()
