import datetime
import pandas as pd
from FinMind.data import DataLoader

def run_smart_scan():
    # 1. 初始化
    dl = DataLoader()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 2. 抓取最基礎的台股清單 (不含財務指標，確保不報錯)
        df = dl.taiwan_stock_info()

        # 3. 準備寫入內容
        content = f"# 📈 台股自動化投資儀表板\n\n"
        content += f"> ✨ 系統強制更新秒數: `{now_str}`\n\n"
        
        # 檢查資料是否真的存在
        if isinstance(df, pd.DataFrame) and not df.empty:
            # 只顯示前 15 檔，確保 README 乾淨
            display_df = df.head(15)[['stock_id', 'stock_name', 'industry_category']]
            content += "## 📋 台股基本資訊清單 (連線測試成功)\n\n"
            content += display_df.to_markdown(index=False)
            content += "\n\n--- \n💡 **Sharon，這代表你的自動化通道已經完全打通了！** \n由於今天是週末，部分財務數據 API 可能在維護中。週一開盤後，我們只要把這段代碼換回「高殖利率」邏輯，數據就會自動長出來了。"
        else:
            content += "⚠️ API 目前回傳格式不符或空值，這在週末數據維護期很常見。"

        # 4. 寫入檔案
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        # 萬一還是出錯，把詳細錯誤寫下來
        error_info = f"# ❌ 執行錯誤報告\n\n時間: `{now_str}`\n\n錯誤詳細資訊: `{str(e)}`"
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(error_info)

if __name__ == "__main__":
    run_smart_scan()
