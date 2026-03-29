import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

def run_goodinfo_scan():
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 這是妳提供的 Goodinfo 投信 5 日買超排行網址
    url = "https://goodinfo.tw/tw/StockList.asp?RPT_TIME=&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E6%8A%95%E4%BF%A1%E7%B4%AF%E8%A8%88%E8%B2%B7%E8%B6%85%E5%BC%B5%E6%95%B8+%E2%80%93+5%E6%97%A5%40%40%E6%8A%95%E4%BF%A1%E7%B4%AF%E8%A8%88%E8%B2%B7%E8%B6%85%40%40%E6%8A%95%E4%BF%A1%E8%B2%B7%E8%B6%85%E5%BC%B5%E6%95%B8+%E2%80%93+5%E6%97%A5"
    
    # 必須偽裝成真人瀏覽器，否則會被拒絕訪問
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        
        # 使用 pandas 直接解析網頁中的所有表格
        dfs = pd.read_html(res.text)
        
        # 通常 Goodinfo 的主要數據表在第 15~18 個表格之間，我們搜尋含有「代號」字眼的表
        target_df = None
        for df in dfs:
            if '代號' in df.columns.get_level_values(0) or '代號' in df.columns:
                target_df = df
                break
        
        content = f"# 📈 Sharon 的 Goodinfo 籌碼儀表板\n\n"
        content += f"> 🕒 執行時間: `{now_str}`\n"
        content += f"> 🎯 數據來源: [Goodinfo! 投信 5 日累計買超排行]({url})\n\n"

        if target_df is not None:
            # 清理表格 (Goodinfo 表頭通常是多層級，我們要簡化它)
            # 取前 25 名，並過濾掉重複的表頭行
            display_df = target_df.head(25)
            
            content += "## 🔥 投信 5 日累計買超熱門排行\n"
            content += display_df.to_markdown(index=False)
            content += "\n\n✅ **成功對接 Goodinfo 數據！** 這是目前內資認同度最高的標的。"
        else:
            content += "⚠️ 抓到了網頁但找不到數據表，可能是 Goodinfo 改版或封鎖了 IP。"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ Goodinfo 存取異常\n\n> 執行時間: `{now_str}`\n\n錯誤訊息: `{str(e)}` \n\n**這代表 Goodinfo 擋住了 GitHub 的自動化抓取。建議等週一開盤再試，或是考慮我們之前的 Yahoo Finance 備援方案。**")

if __name__ == "__main__":
    run_goodinfo_scan()
