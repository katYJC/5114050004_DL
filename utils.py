# utils.py
from __future__ import annotations
import re
from typing import List, Dict, Any

def normalize_ingredients(text: str) -> List[str]:
    """把多行/逗號分隔的食材整理成去重清單。"""
    if not text:
        return []
    items = re.split(r"[\n,，;；]+", text)
    cleaned = []
    for it in items:
        it = it.strip()
        if not it:
            continue
        it = re.sub(r"\s+", " ", it)
        cleaned.append(it)
    # 去重但保留順序
    seen = set()
    out = []
    for it in cleaned:
        key = it.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out

def build_shopping_list(payload: Dict[str, Any]) -> Dict[str, List[str]]:
    """從 menu 的 missing_items 統整購物清單（簡易版）。"""
    buckets = {"蔬菜/水果": [], "肉/蛋/豆": [], "調味/乾貨": [], "其他": []}

    def add_item(item: str):
        s = item.strip()
        if not s:
            return
        # 很粗略分類（夠作業用）
        veg_kw = ["菜", "蔥", "蒜", "薑", "洋蔥", "番茄", "椒", "菇", "高麗", "小黃瓜", "檸檬", "青江"]
        protein_kw = ["雞", "豬", "牛", "魚", "蝦", "蛋", "豆腐", "豆", "絞肉"]
        seasoning_kw = ["醬油", "鹽", "糖", "胡椒", "米酒", "醋", "香油", "辣椒", "咖哩", "味噌", "魚露", "蠔油"]

        if any(k in s for k in veg_kw):
            buckets["蔬菜/水果"].append(s)
        elif any(k in s for k in protein_kw):
            buckets["肉/蛋/豆"].append(s)
        elif any(k in s for k in seasoning_kw):
            buckets["調味/乾貨"].append(s)
        else:
            buckets["其他"].append(s)

    # 從 payload["menu"] 取缺料
    menu = payload.get("menu", [])
    for d in menu:
        for meal in d.get("meals", []):
            for dish in meal.get("dishes", []):
                for miss in dish.get("missing_items", []) or []:
                    add_item(str(miss))

    # 去重
    for k, arr in buckets.items():
        seen = set()
        uniq = []
        for x in arr:
            if x in seen:
                continue
            seen.add(x)
            uniq.append(x)
        buckets[k] = uniq

    return buckets

