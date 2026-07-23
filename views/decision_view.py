# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（ルーレット＆あみだくじ）の画面描画
"""

import datetime
import time
import streamlit as st
import database as db
from recommend import pick_roulette, build_amidakuji, assign_amidakuji_results
from amidakuji_svg import render_amidakuji_svg

def render_decision_page():
    st.title("🎯 決定モード：今日の献立を決めよう")

    st.markdown("条件を絞り込んでから、ルーレットまたはあみだくじで決定します。")

    col1, col2, col3 = st.columns(3)
    with col1:
        cuisine_filter = st.selectbox("料理ジャンル", ["すべて"] + db.CUISINE_CATEGORIES, key="dec_cuisine")
    with col2:
        meal_filter = st.selectbox("種別", ["すべて"] + db.MEAL_TYPE_CATEGORIES, key="dec_meal")
    with col3:
        all_tags = db.get_all_ingredient_tags()
        ingredient_filter = st.multiselect("含まれる材料で絞り込み", all_tags, key="dec_ingredients")

    candidates = db.search_recipes(
        ingredient_query=ingredient_filter if ingredient_filter else None,
        cuisine_category=cuisine_filter,
        meal_category=meal_filter,
    )
    st.info(f"現在の候補：{len(candidates)} 件")

    if not candidates:
        st.warning("条件に合うレシピがありません。検索モードでレシピを登録するか、条件を緩めてください。")
    else:
        with st.expander("候補レシピの一覧を見る"):
            for c in candidates:
                st.write(f"- {c['name']}（{c.get('cuisine_category', '')} / {c.get('meal_category', '')}）")

        tab_roulette, tab_amida = st.tabs(["🎡 ルーレット", "🪜 あみだくじ"])

        # ---- ルーレット ----
        with tab_roulette:
            st.markdown("ボタンを押すと、候補の中からランダムに1つのレシピが選ばれます。")
            if st.button("🎡 ルーレットを回す！", key="spin_roulette", type="primary"):
                # 🌸 パラパラ回るドラムロール演出
                placeholder = st.empty()
                for i in range(12):
                    dummy_choice = pick_roulette(candidates)
                    placeholder.markdown(f"### 🌀 ルーレット回転中... 『**{dummy_choice['name']}**』")
                    time.sleep(0.08 + i * 0.015)
                
                st.session_state.roulette_result = pick_roulette(candidates)
                placeholder.empty()

            if st.session_state.roulette_result:
                r = st.session_state.roulette_result
                st.balloons()
                st.success(f"🎉 今日の献立は「**{r['name']}**」に決定！")
                st.caption(f"{r.get('cuisine_category', '')} / {r.get('meal_category', '')}")
                if r.get("ingredients"):
                    st.write("材料：" + "、".join(r["ingredients"]))
                if r.get("notes"):
                    with st.expander("作り方を見る"):
                        st.write(r["notes"])

                meal_time_for_log = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="rt_log_time")
                if st.button("この結果を今日の記録に追加する", key="save_roulette_log"):
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    db.add_meal_log(today_str, meal_time_for_log, r["id"], "")
                    st.success("記録モードに保存しました！")

        # ---- あみだくじ ----
        with tab_amida:
            st.markdown(
                "参加人数（＝縦線の本数）を決めて、あみだくじを生成します。"
                "各縦線にランダムで候補レシピが割り当てられ、選んだスタート位置の結果が献立になります。"
            )
            num_players = st.slider("縦線の本数", min_value=2, max_value=min(8, max(2, len(candidates))), value=min(4, len(candidates)))

            if st.button("🪜 あみだくじを生成する", key="gen_amida", type="primary"):
                amidakuji = build_amidakuji(num_players)
                result_map = assign_amidakuji_results(amidakuji, candidates)
                st.session_state.amidakuji_data = amidakuji
                st.session_state.amidakuji_results = result_map

            if st.session_state.amidakuji_data:
                amidakuji = st.session_state.amidakuji_data
                result_map = st.session_state.amidakuji_results
                labels = [result_map[i]["name"] for i in range(amidakuji["num_players"])]

                svg_code = render_amidakuji_svg(amidakuji, labels)
                st.markdown(svg_code, unsafe_allow_html=True)

                st.markdown("**スタート位置を選んで結果を確認：**")
                start_choice = st.selectbox(
                    "自分の番号",
                    list(range(1, amidakuji["num_players"] + 1)),
                    key="amida_start_choice",
                )
                chosen_recipe = result_map[start_choice - 1]
                st.success(f"🎉 番号{start_choice}の結果 → 「**{chosen_recipe['name']}**」")
                st.caption(f"{chosen_recipe.get('cuisine_category', '')} / {chosen_recipe.get('meal_category', '')}")
                if chosen_recipe.get("notes"):
                    with st.expander("作り方を見る"):
                        st.write(chosen_recipe["notes"])

                meal_time_for_log2 = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="am_log_time")
                if st.button("この結果を今日の記録に追加する", key="save_amida_log"):
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    db.add_meal_log(today_str, meal_time_for_log2, chosen_recipe["id"], "")
                    st.success("記録モードに保存しました！")