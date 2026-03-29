import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_pro_scan():
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. 直接抓最穩定的「台灣股票基本資訊」
        df = dl.taiwan_stock_info()

        # 2. 準備 Markdown 內容
        content = f"# 📈 Sharon 的雲端選股儀表板\n\n"
        content += f"> 🕒 系統最後更新: `{now_str}`\n\n"
        content += "## 📋 台股基本資訊清單 (週日穩定連線測試)\n"
        content += "> 💡 **連線已完全打通！** 這是從 API 抓到的即時清單：\n\n"
        
        if df is not None and not df.empty:
            # 取前 30 檔，只顯示代號、名稱、產業
            test_df = df.head(30)[['stock_id', 'stock_name', 'industry_category']]
            # 改成中文欄位名稱比較好讀
            test_df.columns = ['股票代號', '股票名稱', '產業類別']
            content += test_df.to_markdown(index=False)
            content += "\n\n--- \n✅ **成功！** 只要妳看到這個表格，就代表機器人大腦已經可以正常說話了。"
        else:
            content += "⚠️ 糟了，API 雖然沒報錯，但回傳了空清單。請再試一次 Run Workflow。"

        # 3. 寫入檔案
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        # 萬一還是出錯，就把錯誤寫下來
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(f"# ⚠️ 數據對接中\n\n執行時間: `{now_str}`\n\n錯誤訊息: `{str(e)}`")

if __name__ == "__main__":
    run_pro_scan()
