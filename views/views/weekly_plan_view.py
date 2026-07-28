# -*- coding: utf-8 -*-
"""
views/weekly_plan_view.py
-----------------------
📅 1週間献立計画 ＆ アイデアメモページ
"""

import datetime
import streamlit as st
import database as db

DAY_NAMES = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

def render_weekly_plan_page():
    # デザイン用CSS
    custom_css = """
    <style>
        .day-title {
            color: var(--gold-2);
            font-family: 'Shippori Mincho', serif;
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 6px;
        }
        .idea-box-title {
            color: var(--gold-2);
            font-family: 'Shippori Mincho', serif;
            font-weight: 700;
            font-size: 18px;
            margin-bottom: 8px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.markdown('<div class="brand"><h1 style="font-family: \'Shippori Mincho\', serif; color: var(--gold-2); text-shadow: 0 0 12px rgba(224, 196, 122, 0.5);">📅 週間献立メモ</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand sub-caption">週末のアイデア出しから1週間の献立計画まで、まとめて管理できますわ✨</div>', unsafe_allow_html=True)
    st.write("")

    # 週の基準日（今週の月曜日）を計算
    today = datetime.date.today()
    this_monday = today - datetime.timedelta(days=today.weekday())

    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    # 週切り替えナビゲーション
    col_prev, col_curr, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("◀ 前の週", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_curr:
        target_monday = this_monday + datetime.timedelta(weeks=st.session_state.week_offset)
        target_sunday = target_monday + datetime.timedelta(days=6)
        st.markdown(f"<h4 style='text-align: center; color: var(--ivory);'>{target_monday.strftime('%m/%d')} 〜 {target_sunday.strftime('%m/%d')}</h4>", unsafe_allow_html=True)
    with col_next:
        if st.button("次の週 ▶", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()

    start_date_str = target_monday.strftime("%Y-%m-%d")
    saved_plans = db.get_weekly_plan(start_date_str)

    st.write("")

    # 全体保存フォーム（アイデアメモ＋各曜日のメモを一括で保存）
    with st.form("weekly_plan_form"):
        # 💡 大きめのアシストメモ欄（週全体のメモ・アイデア一時保管）
        st.markdown('<div class="idea-box-title">💡 今週の献立アイデア・買出しメモ（一時保管）</div>', unsafe_allow_html=True)
        default_idea_val = saved_plans.get("idea", "")
        idea_memo_val = st.text_area(
            label="アイデアメモ",
            value=default_idea_val,
            height=140,
            key=f"idea_memo_{start_date_str}",
            label_visibility="collapsed",
            placeholder="【週末のアイデア箇条書き】\n・ハンバーグ（合挽き肉・玉ねぎ）\n・カレーライス\n・生姜焼き\n・鮭の塩焼き"
        )

        st.markdown("---")
        st.markdown('<div class="idea-box-title">🗓 曜日ごとの献立スケジュール</div>', unsafe_allow_html=True)

        updated_plans = {"idea": idea_memo_val}

        # 月曜日〜日曜日までの入力エリア
        for idx, day_name in enumerate(DAY_NAMES):
            current_day = target_monday + datetime.timedelta(days=idx)
            day_str = current_day.strftime("%m/%d")
            default_val = saved_plans.get(idx, "")

            st.markdown(f'<div class="day-title">✨ {day_name}（{day_str}）</div>', unsafe_allow_html=True)
            memo_val = st.text_area(
                label=f"{day_name}のメモ",
                value=default_val,
                height=70,
                key=f"memo_{start_date_str}_{idx}",
                label_visibility="collapsed",
                placeholder=f"{day_name}の予定・献立"
            )
            updated_plans[idx] = memo_val

        st.write("")
        submitted = st.form_submit_button("💾 計画メモを一括保存する", use_container_width=True)
        if submitted:
            db.save_weekly_plan(start_date_str, updated_plans)
            st.success("1週間の計画とアイデアメモを保存いたしましたわ🌸")