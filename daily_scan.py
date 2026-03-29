import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 抓取三種核心數據
        df_info = dl.taiwan_stock_info()
        df_price = dl.taiwan_stock_daily_last() # 抓取最後一個交易日(週五)的票價
        df_div = dl.taiwan_stock_dividend_result()

        # 2. 開始構建內容
        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 系統最後更新: `{now_str}`\n"
        content += f"> 📅 數據狀態: `週末模式 (顯示週五收盤數據)`\n\n"

        # 檢查數據是否存在並合併
        if df_info is not None and not df_info.empty:
            # 合併基本資訊與票價
            df_merged = pd.merge(df_info[['stock_id', 'stock_name', 'industry_category']], 
                                 df_price[['stock_id', 'close']], on='stock_id', how='left')
            
            # 合併股利數據
            latest_div = df_div.sort_values('date').groupby('stock_id').last().reset_index()
            df_final = pd.merge(df_merged, latest_div[['stock_id', 'cash_dividend_caption']], on='stock_id', how='left')
            
            # 計算殖利率 (處理空值，避免計算報錯)
            df_final['close'] = pd.to_numeric(df_final['close'], errors='coerce')
            df_final['cash_dividend_caption'] = pd.to_numeric(df_final['cash_dividend_caption'], errors='coerce')
            df_final['yield_pct'] = (df_final['cash_dividend_caption'] / df_final['close']) * 100
            
            # 排序：取殖利率最高前 50 名
            top_50 = df_final.dropna(subset=['yield_pct']).sort_values('yield_pct', ascending=False).head(50)
            
            # 整理欄位名稱
            top_50.columns = ['股票代號', '名稱', '產業', '週五票價', '現金股利', '殖利率 (%)']
            top_50['殖利率 (%)'] = top_50['殖利率 (%)'].map('{:,.2f}%'.format)
            
            content += "## 💰 高殖利率精選前 50 名 (週五結算)\n"
            content += top_50.to_markdown(index=False)
            content += "\n\n--- \n✅ **成功加載！** 如果部分股票票價為 NaN，代表 API 正在維護該標的數據。"
        else:
            content += "⚠️ API 目前回傳空值，這通常是週末伺服器端的問題。請放過機器人，明天開盤再試！"

        # 3. 強制寫入檔案
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        # 即使出錯，也要顯示「基本清單」，不准再噴紅叉叉
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 系統維護中\n\n> 時間: `{now_str}`\n\n目前 API 週末暫時離線。週一 16:30 數據就會自動長出來！")

if __name__ == "__main__":
    run_pro_scan()
