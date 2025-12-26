# 5114050004_DL
5114050004_Deep_Learning_Project
# 🍳 Fridge2Recipe Agent（Streamlit Cloud + OpenAI + 中文）

冰箱食材 → 多天菜單 → 每道菜食譜 → 購物清單  
Agent 工作流：Planner → Generator → Reviewer

## Demo
- Streamlit App：<把你的 Streamlit Cloud 連結貼在這裡>

## 功能
- 輸入冰箱食材、份量、人數、時間、忌口、器具
- 自動規劃多天晚餐菜單（避免重複、兼顧蛋白質/蔬菜）
- 為每道菜生成可執行食譜（份量、步驟、火候時間、替代方案）
- Reviewer 自動檢查是否違反忌口/器具/時間並修正
- 統整缺料購物清單（簡易分類）

## 本機執行
```bash
pip install -r requirements.txt
streamlit run app.py
