import datetime
import pandas as pd
import yfinance as yf

def run_weekend_scan():
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 這是妳感興趣的熱門標的清單（妳也可以隨意增加代號）
    # 格式必須是：代號.TW (上市) 或 代號.TWO (上櫃)
    stock_list = [
        '2330.TW', '2317.TW', '2454.TW', '2303.TW', '2308.TW', 
        '2881.TW', '2882.TW', '2886.TW', '2002.TW', '2603.TW',
        '2382.TW', '3231.TW', '2357.TW', '6669.TW', '2376.TW'
    ]
    
    results = []
    print("🚀 啟動 Yahoo Finance 週末強力掃描...")

    for yf_id in stock_list:
        try:
            ticker = yf.Ticker(yf_id)
            # 抓取最近 5 天資料，確保能抓到週五收盤
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                # Yahoo Finance 也有提供股利資訊 (info 裡面的 yield)
                info = ticker.info
                # 取得年度股利 (或從 yield 換算)
                div = info.get('dividendRate', 0)
                if not div: # 如果沒直接提供，試著從殖利率回推
                    div_yield = info.get('dividendYield', 0)
                    div = price * div_yield if div_yield else 0
                
                yield_pct = (div / price) * 100 if price > 0 else 0
                name = info.get('shortName', yf_id)
                
                results.append({
                    "代號": yf_id.replace('.TW', '').replace('.TWO', ''),
                    "名稱": name,
                    "週五收盤價": round(float(price), 2),
                    "預估股利": round(float(div), 2),
                    "殖利率 (%)": round(float(yield_pct), 2)
                })
        except Exception as e:
            print(f"跳過 {yf_id}: {e}")
            continue

    # 寫入 README
    content = f"# 📈 Sharon 的週末不打烊儀表板\n\n"
    content += f"> 🕒 執行時間: `{now_str}`\n"
    content += f"> 📅 數據基準: `週五收盤 (Yahoo Finance 直連)`\n\n"
    
    if results:
        df = pd.DataFrame(results).sort_values("殖利率 (%)", ascending=False)
        content += "## 💰 熱門股殖利率監控 (週末即時版)\n"
        content += df.to_markdown(index=False)
        content += "\n\n✅ **Yahoo 數據連線成功！** 週末也能看到最新分析。"
    else:
        content += "⚠️ 暫時抓不到數據，請確認網路連線。"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 儀表板已更新！")

if __name__ == "__main__":
    run_weekend_scan()
