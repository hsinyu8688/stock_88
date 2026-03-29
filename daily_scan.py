import datetime
import pandas as pd
from FinMind.data import DataLoader

def get_latest_workday():
    """自動取得最近一個有數據的交易日"""
    now = datetime.datetime.now()
    # 如果是週六(5)，回溯到週五；如果是週日(6)，回溯到週五
    if now.weekday() == 5:
        target = now - datetime.timedelta(days=1)
    elif now.weekday() == 6:
        target = now - datetime.timedelta(days=2)
    else:
        target = now
    return target.strftime('%Y-%m-%d')

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 關鍵：自動判定數據日期
    trade_date = get_latest_workday()
    # 為了投信連買，抓取過去 30 天的資料確保涵蓋範圍
    start_date = (datetime.datetime.strptime(trade_date, '%Y-%m-%d') - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    try:
        # 1. 抓取核心數據
        df_inst = dl.taiwan_stock_institutional_investors(start_date=start_date, end_date=trade_date)
        df_daily = dl.taiwan_stock_daily_last()
        df_dividend = dl.taiwan_stock_dividend_result()
        df_info = dl.taiwan_stock_info()

        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 系統執行時間: `{now_str}`\n"
        content += f"> 📅 數據基準日: `{trade_date}` (已自動跳過週末)\n\n"

        # --- 區塊 A：投信連買 (動能區) ---
        sitc_df = df_inst[df_inst['name'] == 'Investment_Trust'].sort_values(['stock_id', 'date'], ascending=[True, False])
        active_stocks = df_daily[df_daily['trading_volume'] > 1000]['stock_id'].tolist()
        
        momentum_list = []
        for stock_id, group in sitc_df.groupby('stock_id'):
            if stock_id not in active_stocks: continue
            buys = group['buy'].values
            count = 0
            for b in buys:
                if b > 0: count += 1
                else: break
            if count >= 3: # 週末放寬一點到 3 天，確保有標的可以觀察
                ind = df_info[df_info['stock_id'] == stock_id]['industry_category'].values[0] if stock_id in df_info['stock_id'].values else "其他"
                momentum_list.append({"代號": stock_id, "產業": ind, "連買天數": count, "最後買超": int(buys[0])})

        content += "## 🔥 投信連續買超 (Momentum)\n"
        if momentum_list:
            content += pd.DataFrame(momentum_list).to_markdown(index=False) + "\n\n"
        else:
            content += "📭 目前市場動能較弱，暫無符合連買標的。\n\n"

        # --- 區塊 B：高殖利率前 50 名 (價值區) ---
        latest_div = df_dividend.sort_values('date').groupby('stock_id').last()
        df_yield = pd.merge(df_daily[['stock_id', 'close']], latest_div[['stock_id', 'cash_dividend_caption']], on='stock_id')
        df_yield['yield_pct'] = (df_yield['cash_dividend_caption'].astype(float) / df_yield['close']) * 100
        yield_top_50 = df_yield.sort_values('yield_pct', ascending=False).head(50)

        content += "## 💰 高殖利率精選前 50 名 (Value)\n"
        content += "| 代號 | 現價 | 股利 | 殖利率 (%) |\n| :--- | :--- | :--- | :--- |\n"
        for _, row in yield_top_50.iterrows():
            content += f"| {row['stock_id']} | {row['close']} | {row['cash_dividend_caption']} | **{row['yield_pct']:.2f}%** |\n"

        # 3. 寫入 README
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 週末不打烊版更新成功！數據基準日: {trade_date}")

    except Exception as e:
        error_msg = f"# ❌ 數據更新異常\n\n> 執行時間: `{now_str}`\n\n錯誤訊息: `{str(e)}`"
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(error_msg)

if __name__ == "__main__":
    run_pro_scan()
