# -*- coding: utf-8 -*-
"""
database.py
-----------
Supabase (PostgreSQL) を利用したデータアクセスモジュール。
レシピ情報（recipes）および食事記録（meal_logs）の CRUD 操作を提供する。
"""

import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# ------------------------------------------------------------------
# 🌸 カテゴリ定義（app.py 側で参照される定数）
# ------------------------------------------------------------------
CUISINE_CATEGORIES = ["和食", "洋食", "中華", "その他"]
MEAL_TYPE_CATEGORIES = ["主菜", "副菜", "主食", "その他"]
MEAL_TIME_CATEGORIES = ["朝食", "昼食", "夕食"]

# ------------------------------------------------------------------
# 🌸 Supabase 接続設定
# ------------------------------------------------------------------
SUPABASE_URL = "https://eodygidrvxfqkbxatfyk.supabase.co"
SUPABASE_KEY = "sb_publishable_3NdqBAvajtFZtpCuqjdDNA_mgAnY6_M"

# Supabase クライアントの初期化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db() -> None:
    """
    データベースの初期化チェック。
    テーブル作成は Supabase 側の SQL Editor で事前に行っているため、
    ここでは接続確認のみを行います。
    """
    try:
        supabase.table("recipes").select("id", count="exact").limit(1).execute()
    except Exception as e:
        print(f"Supabase 接続確認時にエラーが発生しました: {e}")


# ------------------------------------------------------------------
# レシピ（recipes）関連 CRUD
# ------------------------------------------------------------------
def add_recipe(
    name: str,
    ingredients: List[str],
    cuisine_category: str = "その他",
    meal_category: str = "その他",
    notes: str = "",
) -> int:
    """新規レシピを登録する"""
    data = {
        "name": name,
        "ingredients": ingredients,
        "cuisine_category": cuisine_category,
        "meal_category": meal_category,
        "notes": notes,
    }
    response = supabase.table("recipes").insert(data).execute()
    if response.data:
        return response.data[0]["id"]
    return -1


def update_recipe(
    recipe_id: int,
    name: str,
    ingredients: List[str],
    cuisine_category: str = "その他",
    meal_category: str = "その他",
    notes: str = "",
) -> bool:
    """既存レシピを更新する"""
    data = {
        "name": name,
        "ingredients": ingredients,
        "cuisine_category": cuisine_category,
        "meal_category": meal_category,
        "notes": notes,
    }
    response = supabase.table("recipes").update(data).eq("id", recipe_id).execute()
    return bool(response.data)


def delete_recipe(recipe_id: int) -> bool:
    """レシピを削除する"""
    response = supabase.table("recipes").delete().eq("id", recipe_id).execute()
    return bool(response.data)


def get_all_recipes() -> List[Dict[str, Any]]:
    """全レシピを取得する"""
    response = supabase.table("recipes").select("*").order("created_at", desc=True).execute()
    return response.data or []


def get_recipe(recipe_id: int) -> Optional[Dict[str, Any]]:
    """IDを指定して単一レシピを取得する"""
    response = supabase.table("recipes").select("*").eq("id", recipe_id).execute()
    if response.data:
        return response.data[0]
    return None


def search_recipes(
    ingredient_query: Optional[List[str]] = None,
    cuisine_category: Optional[str] = None,
    meal_category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """条件に応じてレシピを絞り込む"""
    query = supabase.table("recipes").select("*")

    if cuisine_category and cuisine_category != "すべて":
        query = query.eq("cuisine_category", cuisine_category)

    if meal_category and meal_category != "すべて":
        query = query.eq("meal_category", meal_category)

    response = query.order("id").execute()
    recipes = response.data or []

    if ingredient_query:
        filtered = []
        for r in recipes:
            ing_list = r.get("ingredients", [])
            joined = " ".join(ing_list).lower()
            if any(ing.lower() in joined for ing in ingredient_query):
                filtered.append(r)
        return filtered

    return recipes


def get_all_ingredient_tags() -> List[str]:
    """既存レシピから使われている材料タグを収集する"""
    tags = set()
    for r in get_all_recipes():
        tags.update(r.get("ingredients", []))
    return sorted(list(tags))


# ------------------------------------------------------------------
# 食事記録（meal_logs）関連 CRUD
# ------------------------------------------------------------------
def add_meal_log(
    log_date: str,
    meal_time: str,
    recipe_id: Optional[int] = None,
    free_text: str = "",
) -> int:
    """指定日の食事記録を追加する"""
    data = {
        "log_date": log_date,
        "meal_time": meal_time,
        "recipe_id": recipe_id,
        "free_text": free_text, 
    }
    response = supabase.table("meal_logs").insert(data).execute()
    if response.data:
        return response.data[0]["id"]
    return -1


def delete_meal_log(log_id: int) -> bool:
    """食事記録を削除する"""
    response = supabase.table("meal_logs").delete().eq("id", log_id).execute()
    return bool(response.data)


def get_meal_logs_by_date(log_date: str) -> List[Dict[str, Any]]:
    """指定日の食事記録を取得する（レシピ名等も結合）"""
    response = (
        supabase.table("meal_logs")
        .select("*, recipes(*)")
        .eq("log_date", log_date)
        .execute()
    )
    logs = response.data or []
    
    # 並び順の整列用マップ（朝食->昼食->夕食）
    order_map = {"朝食": 1, "昼食": 2, "夕食": 3}

    result = []
    for log in logs:
        log_dict = dict(log)
        recipe_data = log_dict.pop("recipes", None)
        if recipe_data:
            log_dict["recipe_name"] = recipe_data.get("name")
            log_dict["cuisine_category"] = recipe_data.get("cuisine_category")
            log_dict["meal_category"] = recipe_data.get("meal_category")
        else:
            log_dict["recipe_name"] = None
            log_dict["cuisine_category"] = None
            log_dict["meal_category"] = None
        result.append(log_dict)

    # 時間帯順にソート
    result.sort(key=lambda x: order_map.get(x.get("meal_time"), 4))
    return result


def get_meal_log_dates_in_month(year: int, month: int) -> set:
    """指定した年月に記録が存在する日付一覧を取得する"""
    prefix = f"{year:04d}-{month:02d}-"
    response = (
        supabase.table("meal_logs")
        .select("log_date")
        .like("log_date", f"{prefix}%")
        .execute()
    )
    logs = response.data or []
    return {r["log_date"] for r in logs}

# ------------------------------------------------------------------
# 🌸 週間メモ（weekly_plans）関連 CRUD
# ------------------------------------------------------------------
def get_weekly_plan(start_date_str: str) -> Dict[Any, str]:
    """指定された週（月曜日開始）のメモを取得する"""
    try:
        response = (
            supabase.table("weekly_plans")
            .select("day_index, memo")
            .eq("start_date", start_date_str)
            .execute()
        )
        rows = response.data or []

        plan_dict = {}
        for row in rows:
            day_idx = row.get("day_index", "")
            # day_index が数字（0~6）の場合は整数キーに変換して格納
            key = int(day_idx) if day_idx.isdigit() else day_idx
            plan_dict[key] = row.get("memo", "")
        return plan_dict
    except Exception as e:
        print(f"週間メモ取得時にエラーが発生しました: {e}")
        return {}


def save_weekly_plan(start_date_str: str, plan_dict: Dict[Any, str]) -> bool:
    """指定された週（月曜日開始）のメモを保存する"""
    try:
        data_list = []
        for day_idx, memo in plan_dict.items():
            data_list.append(
                {
                    "start_date": start_date_str,
                    "day_index": str(day_idx),
                    "memo": memo,
                }
            )

        if data_list:
            # upsert（存在すれば更新、なければ新規挿入）を実行
            supabase.table("weekly_plans").upsert(data_list).execute()
        return True
    except Exception as e:
        print(f"週間メモ保存時にエラーが発生しました: {e}")
        return False