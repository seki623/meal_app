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

        # 【設計変更】1つの meal_log（器）に複数の meal_log_item（品目）が
        # ぶら下がる構造になったため、表示側も「食事区分ごとに品目を列挙する」形にする
        logs = db.get_meal_logs_by_date(date_str)
        if not logs:
            st.info("この日の記録はまだありません。下のフォームから追加してください。")
        else:
            for log in logs:
                with st.container(border=True):
                    st.markdown(f"**{log['meal_time']}**")
                    items = log.get("items", [])
                    if not items:
                        st.caption("（品目未登録）")
                    for item in items:
                        item_display = item.get("recipe_name") or "（名称なし）"
                        role = item.get("role", "その他")
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.write(f"[{role}] {item_display}")
                        with c2:
                            if st.button("削除", key=f"del_item_{item['id']}"):
                                db.delete_meal_log_item(item["id"])
                                st.rerun()

        st.markdown("---")
        st.markdown("**新しい食事を記録する**")

        meal_time = st.selectbox("食事区分", db.MEAL_TIME_CATEGORIES, key="record_meal_time")

        # 【カート方式】品目は「追加ボタン」を押すたびに一時リストに積み、
        # 最後にまとめて保存する。こうすることで「ごはん・おかず・みそ汁」のように
        # 1回の記録操作で複数レシピを登録できるようにする。
        cart_key = f"item_cart_{date_str}_{meal_time}"
        if cart_key not in st.session_state:
            st.session_state[cart_key] = []

        st.caption("この食事に含める品目を1つずつ追加してください（ごはん・おかず・みそ汁など）")

        input_type = st.radio(
            "品目の入力方法",
            ["登録済みレシピから選ぶ", "自由に直接入力する（図鑑にない料理）"],
            horizontal=True,
            key="item_input_type",
        )

        role_choice = st.selectbox("この品目の役割", db.MEAL_ROLE_CATEGORIES, key="item_role_choice")

        selected_recipe_id = None
        free_text = ""

        if input_type == "登録済みレシピから選ぶ":
            recipes = db.get_all_recipes()
            recipe_options = {r["name"]: r["id"] for r in recipes}
            if recipe_options:
                recipe_choice = st.selectbox("レシピを選択", list(recipe_options.keys()), key="item_recipe_choice")
                selected_recipe_id = recipe_options[recipe_choice]
            else:
                st.info("登録済みのレシピがまだありません。『自由に直接入力する』をお選びください。")
        else:
            free_text = st.text_input("料理名を入力してください", "", key="item_free_text")

        if st.button("＋ この品目をカートに追加", key="add_item_to_cart"):
            if input_type == "自由に直接入力する（図鑑にない料理）" and not free_text.strip():
                st.error("料理名を入力してください。")
            elif input_type == "登録済みレシピから選ぶ" and selected_recipe_id is None:
                st.error("レシピを選択してください。")
            else:
                st.session_state[cart_key].append({
                    "recipe_id": selected_recipe_id,
                    "free_text": free_text.strip(),
                    "role": role_choice,
                })
                st.rerun()

        # カートの中身を表示（保存前に確認・削除できるようにする）
        if st.session_state[cart_key]:
            st.markdown(f"**{meal_time}に追加する品目（{len(st.session_state[cart_key])}件）**")
            for idx, cart_item in enumerate(st.session_state[cart_key]):
                label = cart_item["free_text"] if cart_item["free_text"] else f"レシピID:{cart_item['recipe_id']}"
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"[{cart_item['role']}] {label}")
                with c2:
                    if st.button("取消", key=f"remove_cart_{idx}"):
                        st.session_state[cart_key].pop(idx)
                        st.rerun()

            if st.button(f"この{len(st.session_state[cart_key])}品目をまとめて記録する", type="primary", key="save_cart"):
                # 器（meal_log）を作成 or 再利用し、カート内の品目をすべて紐づけて保存する
                meal_log_id = db.add_meal_log(date_str, meal_time)
                for sort_order, cart_item in enumerate(st.session_state[cart_key]):
                    db.add_meal_log_item(
                        meal_log_id=meal_log_id,
                        recipe_id=cart_item["recipe_id"],
                        free_text=cart_item["free_text"],
                        role=cart_item["role"],
                        sort_order=sort_order,
                    )
                st.session_state[cart_key] = []
                st.success("記録しました！")
                st.rerun()