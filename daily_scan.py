import datetime
import pandas as pd
from FinMind.data import DataLoader

def get_last_trading_date():
    """判斷今天是否為週末，如果是則回溯到週五"""
    today = datetime.datetime.now()
    # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    day_of_week = today.weekday()
    
    if day_of_week == 5: # 週六 -> 抓週五
        target_date = today - datetime.timedelta(days=1)
    elif day_of_week == 6: # 週日 -> 抓週五
        target_date = today - datetime.timedelta(days=2)
    else:
        # 平日如果還沒收盤(14:00前)，可能也要抓前一天，這裡我們先抓當天
        target_date = today
        
    return target_date.strftime('%Y-%m-%d')

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 取得最近一個交易日
    last_date = get_last_trading_date()
    # 為了投信連買，我們需要往前抓 20 天的區間
    start_date = (datetime.datetime.strptime(last_date, '%Y-%m-%d') - datetime.timedelta(days=20)).strftime('%Y-%m-%d')

    try:
        # 1. 抓取行情 (指定抓到最近交易日)
        df_daily = dl.taiwan_stock_daily(stock_id='', start_date=last_date, end_date=last_date)
        df_info = dl.taiwan_stock_info()
        df_dividend = dl.taiwan_stock_dividend_result()

        # 2. 組合內容
        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 執行時間: `{now_str}`\n"
        content += f"> 📅 數據基準日: `{last_date}` (週末自動回溯)\n\n"

        if df_daily is not None and not df_daily.empty:
            # 合併價格與基本資訊
            df_merged = pd.merge(df_info[['stock_id', 'stock_name', 'industry_category']], 
                                 df_daily[['stock_id', 'close']], on='stock_id')
            
            # 加上股利與殖利率計算
            latest_div = df_dividend.sort_values('date').groupby('stock_id').last()
            df_final = pd.merge(df_merged, latest_div[['stock_id', 'cash_dividend_caption']], on='stock_id')
            df_final['yield_pct'] = (df_final['cash_dividend_caption'].astype(float) / df_final['close']) * 100
            
            # 排序：取殖利率最高的前 50 名
            top_50 = df_final.sort_values('yield_pct', ascending=False).head(50)
            top_50.columns = ['股票代號', '名稱', '產業', '週五票價', '現金股利', '殖利率 (%)']
            
            content += "## 💰 高殖利率精選前 50 名 (基準日: 週五)\n"
            # 格式化殖利率顯示
            top_50['殖利率 (%)'] = top_50['殖利率 (%)'].map('{:,.2f}%'.format)
            content += top_50.to_markdown(index=False)
            
            content += "\n\n--- \n✅ **數據加載成功！** 週末期間將持續顯示週五收盤數據。"
        else:
            content += "⚠️ 暫時無法取得 `"+last_date+"` 的行情數據。API 可能正在維護，請稍後再試。"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 數據處理異常\n\n> 執行時間: `{now_str}`\n\n錯誤訊息: `{str(e)}` \n\n這通常是 API 傳回空值。請稍等五分鐘再 Run Workflow 一次。")

if __name__ == "__main__":
    run_pro_scan()
