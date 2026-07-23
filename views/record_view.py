# -*- coding: utf-8 -*-
"""
views/record_view.py
---------------------
📅 記録モード（カレンダー＆食事ログ入力）の画面描画
"""

import datetime
import calendar
import re
import streamlit as st
import database as db

def render_record_page():
    st.title("📅 記録モード：今日のごはんを記録しよう")

    col_cal, col_log = st.columns([1, 1.3])

    # ---- 左カラム：日付選択（カレンダー風） ----
    with col_cal:
        st.subheader("日付を選択")
        selected_date = st.date_input("記録する日付", value=datetime.date.today())

        year, month = selected_date.year, selected_date.month
        recorded_dates = db.get_meal_log_dates_in_month(year, month)

        st.markdown(f"**{year}年{month}月の記録状況**")
        cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
        month_days = cal.monthdatescalendar(year, month)

        header = "| 日 | 月 | 火 | 水 | 木 | 金 | 土 |\n|---|---|---|---|---|---|---|\n"
        rows = ""
        for week in month_days:
            row_cells = []
            for d in week:
                mark = "🍙" if d.strftime("%Y-%m-%d") in recorded_dates else ""
                if d.month == month:
                    row_cells.append(f"{d.day}{mark}")
                else:
                    row_cells.append("")
            rows += "| " + " | ".join(row_cells) + " |\n"
        st.markdown(header + rows)

    # ---- 右カラム：選択日の食事記録一覧＋新規追加フォーム ----
    with col_log:
        date_str = selected_date.strftime("%Y-%m-%d")
        st.subheader(f"{date_str} の食事記録")

        logs = db.get_meal_logs_by_date(date_str)
        if not logs:
            st.info("この日の記録はまだありません。下のフォームから追加してください。")
        else:
            for log in logs:
                meal_display = log.get("recipe_name") or log.get("free_text") or "（名称なし）"
                
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{log['meal_time']}**：{meal_display}")
                        if log.get("cuisine_category"):
                            st.caption(f"{log['cuisine_category']} / {log.get('meal_category', '')}")
                    with c2:
                        if st.button("削除", key=f"del_log_{log['id']}"):
                            db.delete_meal_log(log["id"])
                            st.rerun()

        st.markdown("---")
        st.markdown("**新しい食事を記録する**")

        meal_time = st.selectbox("食事区分", db.MEAL_TIME_CATEGORIES)

        input_type = st.radio(
            "記録方法",
            ["登録済みレシピから選ぶ", "自由に直接入力する（図鑑にない料理）"],
            horizontal=True
        )

        selected_recipe_id = None
        free_text = ""

        if input_type == "登録済みレシピから選ぶ":
            recipes = db.get_all_recipes()
            recipe_options = {r["name"]: r["id"] for r in recipes}
            
            if recipe_options:
                recipe_choice = st.selectbox("レシピを選択", list(recipe_options.keys()))
                selected_recipe_id = recipe_options[recipe_choice]
            else:
                st.info("登録済みのレシピがまだありません。『自由に直接入力する』をお選びください。")
        else:
            free_text = st.text_input("料理名を入力してください", "")

        save_as_recipe = False
        if input_type == "自由に直接入力する（図鑑にない料理）":
            save_as_recipe = st.checkbox("✨ この内容をレシピ図鑑にも同時に登録する")

        if save_as_recipe:
            with st.container(border=True):
                st.caption("レシピ図鑑への登録情報")
                col_a, col_b = st.columns(2)
                with col_a:
                    new_cuisine = st.selectbox("料理ジャンル", db.CUISINE_CATEGORIES, key="sim_cuisine")
                with col_b:
                    new_meal = st.selectbox("種別", db.MEAL_TYPE_CATEGORIES, key="sim_meal")
                new_ingredients = st.text_input("材料（読点やカンマで区切り。例: 豚肉、キャベツ）", key="sim_ing")
                new_notes = st.text_area("作り方・メモ", key="sim_notes")

        if st.button("記録する", type="primary"):
            if input_type == "自由に直接入力する（図鑑にない料理）" and not free_text.strip():
                st.error("料理名を入力してください。")
            elif input_type == "登録済みレシピから選ぶ" and selected_recipe_id is None:
                st.error("レシピを選択してください。")
            else:
                if save_as_recipe and free_text.strip():
                    ing_list = [i.strip() for i in re.split(r'[,，、\s]+', new_ingredients) if i.strip()]
                    new_id = db.add_recipe(
                        name=free_text.strip(),
                        ingredients=ing_list,
                        cuisine_category=new_cuisine,
                        meal_category=new_meal,
                        notes=new_notes.strip()
                    )
                    if new_id != -1:
                        selected_recipe_id = new_id
                        free_text_to_save = ""
                    else:
                        free_text_to_save = free_text.strip()
                else:
                    free_text_to_save = free_text.strip() if input_type == "自由に直接入力する（図鑑にない料理）" else ""

                db.add_meal_log(date_str, meal_time, selected_recipe_id, free_text_to_save)
                st.success("記録しました！")
                st.rerun()