# agent.py
from __future__ import annotations
import json
from typing import Dict, Any, Optional

from openai import OpenAI
from prompts import SYSTEM_BASE, PLANNER_PROMPT, GENERATOR_PROMPT, REVIEWER_PROMPT

def _json_loads_safe(text: str) -> Dict[str, Any]:
    """
    盡量把模型輸出轉成 JSON。
    若模型外面包了多餘文字，嘗試擷取第一段 { ... }。
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        # 擷取第一個 JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise

class RecipeAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _chat(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
        )
        return resp.choices[0].message.content or ""

    def plan_menu(self, params: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = PLANNER_PROMPT.format(**params)
        out = self._chat(SYSTEM_BASE, user_prompt)
        return _json_loads_safe(out)

    def generate_recipes(self, params: Dict[str, Any], menu_json: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = GENERATOR_PROMPT.format(menu_json=json.dumps(menu_json, ensure_ascii=False), **params)
        out = self._chat(SYSTEM_BASE, user_prompt)
        return _json_loads_safe(out)

    def review_and_fix(self, params: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = REVIEWER_PROMPT.format(payload_json=json.dumps(payload, ensure_ascii=False), **params)
        out = self._chat(SYSTEM_BASE, user_prompt)
        return _json_loads_safe(out)

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        menu = self.plan_menu(params)
        recipes = self.generate_recipes(params, menu)
        payload = {"menu": menu.get("menu", []), "assumptions": menu.get("assumptions", []), "recipes": recipes.get("recipes", [])}
        reviewed = self.review_and_fix(params, payload)
        # 回傳 reviewer 的 payload
        return reviewed

