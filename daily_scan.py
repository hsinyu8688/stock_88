import datetime
import pandas as pd
import yfinance as yf
from FinMind.data import DataLoader
from tqdm import tqdm

def run_yahoo_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 抓取 FinMind 的股利與股票資訊 (這部分週末通常穩定)
        df_div = dl.taiwan_stock_dividend_result()
        df_info = dl.taiwan_stock_info()
        
        content = f"# 📈 Sharon 的 Yahoo Finance 投資儀表板\n\n"
        content += f"> 🕒 執行時間: `{now_str}`\n"
        content += f"> 📅 數據來源: `Yahoo Finance (週末不打烊)`\n\n"

        if not df_div.empty:
            # 取得最新的股利政策
            latest_div = df_div.sort_values('date').groupby('stock_id').last().reset_index()
            # 挑選股利前 60 名來抓價格 (避免 API 請求過多)
            top_div = latest_div.sort_values('cash_dividend_caption', ascending=False).head(60)
            
            results = []
            print("正在連線 Yahoo Finance 獲取票價...")
            
            for _, row in tqdm(top_div.iterrows(), total=len(top_div)):
                stock_id = row['stock_id']
                yf_id = f"{stock_id}.TW"
                
                try:
                    ticker = yf.Ticker(yf_id)
                    # 抓取最後一筆成交價
                    price = ticker.fast_info['last_price']
                    div = float(row['cash_dividend_caption'])
                    
                    if price and price > 0:
                        yield_pct = (div / price) * 100
                        name = df_info[df_info['stock_id'] == stock_id]['stock_name'].values[0] if stock_id in df_info['stock_id'].values else "未知"
                        
                        results.append({
                            "股票代號": stock_id,
                            "名稱": name,
                            "目前票價": round(price, 2),
                            "現金股利": div,
                            "殖利率 (%)": round(yield_pct, 2)
                        })
                except:
                    continue
            
            # 整理並排序
            final_df = pd.DataFrame(results).sort_values("殖利率 (%)", ascending=False).head(50)
            
            content += "## 💰 高殖利率精選前 50 名 (即時票價計算)\n"
            content += final_df.to_markdown(index=False)
            content += "\n\n--- \n✅ **成功對接 Yahoo Finance！** 週末也能看到最新的票價與分析。"
        else:
            content += "⚠️ 無法取得股利數據，請檢查 FinMind API 狀態。"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 儀表板更新成功！")
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 系統維護中\n\n> 執行時間: `{now_str}`\n\n錯誤訊息: `{str(e)}` \n\n**這代表 Yahoo Finance 暫時無法連線。請稍後再試。**")

if __name__ == "__main__":
    run_yahoo_scan()
