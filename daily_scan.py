import datetime
import pandas as pd
import yfinance as yf
from FinMind.data import DataLoader

def run_yahoo_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 抓取 FinMind 的股利與股票資訊 (週末這部分通常穩定)
        df_div = dl.taiwan_stock_dividend_result()
        df_info = dl.taiwan_stock_info()
        
        content = f"# 📈 Sharon 的 Yahoo Finance 投資儀表板\n\n"
        content += f"> 🕒 執行時間: `{now_str}`\n"
        content += f"> 📅 數據來源: `Yahoo Finance (週末歷史數據法)`\n\n"

        if df_div is not None and not df_div.empty:
            # 取得最新的股利政策
            latest_div = df_div.sort_values('date').groupby('stock_id').last().reset_index()
            # 挑選股利最高的前 35 名進行對接 (縮小範圍確保執行極速且不超時)
            top_div = latest_div.sort_values('cash_dividend_caption', ascending=False).head(35)
            
            results = []
            print("正在連線 Yahoo Finance 獲取收盤票價...")
            
            for _, row in top_div.iterrows():
                stock_id = row['stock_id']
                yf_id = f"{stock_id}.TW"
                
                try:
                    # 改用最穩定的 history 方法，避開 FastInfo 錯誤
                    ticker = yf.Ticker(yf_id)
                    hist = ticker.history(period="5d") # 抓 5 天確保能抓到週五收盤
                    
                    if not hist.empty:
                        # 取得最後一天的收盤價
                        price = hist['Close'].iloc[-1]
                        div = float(row['cash_dividend_caption'])
                        yield_pct = (div / price) * 100
                        
                        name = df_info[df_info['stock_id'] == stock_id]['stock_name'].values[0] if stock_id in df_info['stock_id'].values else "未知"
                        
                        results.append({
                            "股票代號": stock_id,
                            "名稱": name,
                            "週五票價": round(float(price), 2),
                            "現金股利": div,
                            "殖利率 (%)": round(float(yield_pct), 2)
                        })
                except:
                    continue
            
            if results:
                final_df = pd.DataFrame(results).sort_values("殖利率 (%)", ascending=False)
                content += "## 💰 高殖利率精選 (週五收盤結算)\n"
                content += final_df.to_markdown(index=False)
                content += "\n\n--- \n✅ **Yahoo 備援系統加載成功！** 週末也能看到最新的票價分析。"
            else:
                content += "⚠️ 暫時無法獲取票價數據，可能 Yahoo API 限制了連線。"
        else:
            content += "⚠️ 無法取得 FinMind 股利基礎數據。"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 儀表板更新成功！")
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 系統修復中\n\n> 執行時間: `{now_str}`\n\n目前 API 連線不穩。週一開盤後將自動恢復正常。")

if __name__ == "__main__":
    run_yahoo_scan()
