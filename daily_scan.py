import datetime
import pandas as pd
import yfinance as yf
from FinMind.data import DataLoader

def run_yahoo_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 抓取 FinMind 的股利與股票資訊 (靜態資料週末穩定)
        df_div = dl.taiwan_stock_dividend_result()
        df_info = dl.taiwan_stock_info()
        
        content = f"# 📈 Sharon 的 Yahoo Finance 投資儀表板\n\n"
        content += f"> 🕒 執行時間: `{now_str}`\n"
        content += f"> 📅 數據來源: `Yahoo Finance (週末歷史數據模式)`\n\n"

        if df_div is not None and not df_div.empty:
            # 取得最新股利政策
            latest_div = df_div.sort_values('date').groupby('stock_id').last().reset_index()
            # 挑選股利前 35 名進行對接，確保穩定
            top_div = latest_div.sort_values('cash_dividend_caption', ascending=False).head(35)
            
            results = []
            print("正在連線 Yahoo Finance 獲取週五收盤價...")
            
            for _, row in top_div.iterrows():
                stock_id = row['stock_id']
                yf_id = f"{stock_id}.TW"
                
                try:
                    ticker = yf.Ticker(yf_id)
                    # 抓取最近 5 天資料，確保能抓到最後一個交易日
                    hist = ticker.history(period="5d")
                    
                    if not hist.empty:
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
                content += "\n\n--- \n✅ **Yahoo 備援系統已成功產出內容！** 週末也能看到最新的票價分析。"
            else:
                content += "⚠️ 暫時無法獲取票價數據，請檢查 Yahoo API 狀態。"
        else:
            content += "⚠️ 無法取得 FinMind 股利基礎數據。"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 儀表板更新成功！")
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 系統修復中\n\n> 執行時間: `{now_str}`\n\n目前 API 連線有小問題。週一開盤後數據將自動恢復。")

if __name__ == "__main__":
    run_yahoo_scan()
