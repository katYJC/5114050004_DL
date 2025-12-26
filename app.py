# app.py
import json
import streamlit as st

from agent import RecipeAgent
from utils import normalize_ingredients, build_shopping_list

st.set_page_config(page_title="Fridge2Recipe Agent", page_icon="🍳", layout="wide")

st.title("🍳 Fridge2Recipe Agent（冰箱食材 → 菜單＋食譜＋購物清單）")
st.caption("Streamlit Cloud + OpenAI｜中文｜Agent：Planner → Generator → Reviewer")

with st.sidebar:
    st.header("設定")
    servings = st.slider("人數", 1, 8, 3)
    time_limit = st.selectbox("每餐可用時間上限（分鐘）", [15, 20, 30, 45, 60], index=2)
    days = st.selectbox("規劃天數", [1, 2, 3, 5, 7], index=2)
    meals_per_day = 1
    dishes_per_meal = st.selectbox("每餐幾道菜", [2, 3, 4], index=1)

    spice_level = st.selectbox("辣度", ["不辣", "微辣", "小辣", "中辣", "大辣"], index=1)
    taste = st.multiselect("口味偏好（可複選）", ["清淡", "家常", "重口味", "日式", "韓式", "泰式", "台式", "中式"], default=["家常", "台式"])
    dietary = st.multiselect("忌口/過敏（可複選）", ["不吃牛", "不吃豬", "不吃海鮮", "不吃蛋", "奶類不適", "全素", "蛋奶素"], default=[])
    equipment = st.multiselect("可用器具（可複選）", ["平底鍋/炒鍋", "電鍋", "氣炸鍋", "烤箱", "微波爐"], default=["平底鍋/炒鍋"])

    st.divider()
    model = st.selectbox("OpenAI 模型", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)

st.subheader("1) 請輸入你冰箱現有食材")
ingredients_text = st.text_area(
    "一行一樣或用逗號分隔（例：雞胸肉、蛋、空心菜、馬鈴薯）",
    height=140,
    placeholder="雞胸肉\n蛋\n空心菜\n馬鈴薯\n蒜頭\n醬油",
)

colA, colB = st.columns([1, 1])
with colA:
    run_btn = st.button("🚀 生成菜單與食譜", type="primary")
with colB:
    st.write("")

api_key = st.secrets.get("OPENAI_API_KEY", "")

if run_btn:
    if not api_key:
        st.error("找不到 OPENAI_API_KEY。請到 Streamlit Cloud → App settings → Secrets 設定。")
        st.stop()

    ingredients = normalize_ingredients(ingredients_text)
    if not ingredients:
        st.warning("請先輸入至少 2-3 種食材。")
        st.stop()

    params = {
        "ingredients": "、".join(ingredients),
        "servings": servings,
        "time_limit": time_limit,
        "days": days,
        "meals_per_day": meals_per_day,
        "dishes_per_meal": dishes_per_meal,
        "spice_level": spice_level,
        "taste": "、".join(taste) if taste else "家常",
        "dietary": "、".join(dietary) if dietary else "無",
        "equipment": "、".join(equipment) if equipment else "平底鍋/炒鍋",
    }

    with st.spinner("Agent 工作中：規劃菜單 → 生成食譜 → 檢查修正 ..."):
        agent = RecipeAgent(api_key=api_key, model=model)
        result = agent.run(params)

    st.success("完成！")

    fixed = result.get("fixed", False)
    status = result.get("status", "unknown")
    payload = result.get("payload", {})

    st.info(f"Reviewer 狀態：{status}｜是否修正：{fixed}")

    tab1, tab2, tab3, tab4 = st.tabs(["📅 菜單", "📖 食譜", "🛒 購物清單", "🧾 原始 JSON"])

    with tab1:
        menu = payload.get("menu", [])
        assumptions = payload.get("assumptions", [])
        for day in menu:
            st.markdown(f"### 第 {day.get('day')} 天")
            for meal in day.get("meals", []):
                st.markdown(f"**{meal.get('title','晚餐')}**")
                for dish in meal.get("dishes", []):
                    st.markdown(f"- **{dish.get('name')}**：{dish.get('brief_reason','')}")
                    st.caption(f"用到：{', '.join(dish.get('use_ingredients', []) or [])}")
                    miss = dish.get("missing_items", []) or []
                    if miss:
                        st.caption(f"可能缺：{', '.join(miss)}")
        if assumptions:
            st.markdown("#### 假設清單")
            st.write(assumptions)

    with tab2:
        recipes = payload.get("recipes", [])
        for day in recipes:
            st.markdown(f"### 第 {day.get('day')} 天")
            for meal in day.get("meals", []):
                st.markdown(f"**{meal.get('title','晚餐')}**")
                parallel = meal.get("meal_parallel_plan", []) or []
                if parallel:
                    st.caption("同時進行安排：")
                    st.write(parallel)
                for dish in meal.get("dishes", []):
                    st.markdown(f"#### 🍽️ {dish.get('name')}")
                    st.write(f"預估時間：{dish.get('estimated_minutes', 'N/A')} 分鐘")

                    st.markdown("**食材**")
                    st.table(dish.get("ingredients", []))

                    st.markdown("**調味**")
                    st.table(dish.get("seasoning", []))

                    st.markdown("**步驟**")
                    for i, s in enumerate(dish.get("steps", []), 1):
                        st.write(f"{i}. {s}")

                    tips = dish.get("tips", []) or []
                    subs = dish.get("substitutions", []) or []
                    if tips:
                        st.markdown("**小技巧**")
                        st.write(tips)
                    if subs:
                        st.markdown("**替代方案**")
                        st.write(subs)

                    st.divider()

    with tab3:
        shopping = build_shopping_list(payload)
        for k, items in shopping.items():
            st.markdown(f"### {k}")
            if items:
                st.write(items)
            else:
                st.caption("（無）")

    with tab4:
        st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")

