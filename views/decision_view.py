# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（世界樹・幻想タロット＆ガチャ＋背景アニメーション）の画面描画
"""

import datetime
import random
import time
import streamlit as st
import database as db

# 🌸 切り抜いて static/ に置いた画像のパスを指定いたします
TAROT_BACK_IMAGE = "static/tarot_back.jpg"


def render_decision_page():
    # ==================================================================
    # 🌸 決定モード専用：背景粒子アニメーション（CSS）
    # ==================================================================
    bg_animation_html = """
    <style>
        /* 決定モード全体の背景設定 */
        .stApp {
            background: linear-gradient(180deg, #050b14 0%, #0a111e 50%, #121c2e 100%) !important;
            background-attachment: fixed;
            position: relative;
            overflow-x: hidden;
        }

        /* アニメーション用コンテナ */
        .stars-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        /* 粒子（光の粒子）のスタイル */
        .star {
            position: absolute;
            bottom: -10px;
            background: radial-gradient(circle, #f3e5ab 0%, rgba(212, 175, 55, 0) 70%);
            border-radius: 50%;
            opacity: 0.8;
            animation: floatUp linear infinite;
        }

        /* 個別の粒子の配置とスピード設定 */
        .star:nth-child(1) { left: 10%; width: 6px; height: 6px; animation-duration: 8s; animation-delay: 0s; }
        .star:nth-child(2) { left: 25%; width: 8px; height: 8px; animation-duration: 12s; animation-delay: 2s; }
        .star:nth-child(3) { left: 40%; width: 5px; height: 5px; animation-duration: 10s; animation-delay: 4s; }
        .star:nth-child(4) { left: 55%; width: 9px; height: 9px; animation-duration: 14s; animation-delay: 1s; }
        .star:nth-child(5) { left: 70%; width: 6px; height: 6px; animation-duration: 9s; animation-delay: 3s; }
        .star:nth-child(6) { left: 85%; width: 7px; height: 7px; animation-duration: 11s; animation-delay: 5s; }

        /* 上昇アニメーションの定義 */
        @keyframes floatUp {
            0% {
                transform: translateY(0) scale(0.8);
                opacity: 0;
            }
            20% {
                opacity: 0.8;
            }
            80% {
                opacity: 0.6;
            }
            100% {
                transform: translateY(-105vh) scale(1.2);
                opacity: 0;
            }
        }
    </style>

    <div class="stars-container">
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
        <div class="star"></div>
    </div>
    """
    st.markdown(bg_animation_html, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # メインコンテンツ
    # ------------------------------------------------------------------
    st.title("🎯 決定モード：今日の献立を決めよう")
    st.markdown("条件を絞り込んでから、神秘的な世界樹のカードかガチャで献立を決定しますの🌸")

    # ---- 条件絞り込み ----
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
        st.warning("条件に合うレシピがありません。検索モードでレシピを登録するか、条件を緩めてくださいませ。")
        return

    with st.expander("候補レシピの一覧を見る"):
        for c in candidates:
            st.write(f"- {c['name']}（{c.get('cuisine_category', '')} / {c.get('meal_category', '')}）")

    tab_tarot, tab_gacha = st.tabs(["🔮 タロットカード", "🎰 ガチャガチャ"])

    # ==================================================================
    # 🌸 タブ1：幻想フリップ・タロットカード
    # ==================================================================
    with tab_tarot:
        st.markdown("神秘的なカードの中から、直感で1枚選んでタップしてくださいませ✨")

        num_cards = min(4, len(candidates))

        # 初期化・シャッフル
        if "tarot_deck" not in st.session_state or len(st.session_state.get("tarot_deck", [])) != num_cards or st.button("🂠 カードをシャッフルする", key="shuffle_tarot"):
            st.session_state.tarot_deck = random.sample(candidates, num_cards)
            st.session_state.tarot_selected_idx = None

        st.markdown("---")

        actual_deck_size = len(st.session_state.tarot_deck)
        cols = st.columns(actual_deck_size)

        for idx in range(actual_deck_size):
            with cols[idx]:
                is_selected = (st.session_state.tarot_selected_idx == idx)
                recipe = st.session_state.tarot_deck[idx]

                card_html = f"""
                <style>
                    .card-container {{
                        perspective: 1000px;
                        width: 100%;
                        height: 200px;
                        margin-bottom: 10px;
                    }}
                    .card-inner {{
                        position: relative;
                        width: 100%;
                        height: 100%;
                        text-align: center;
                        transition: transform 0.8s ease-in-out;
                        transform-style: preserve-3d;
                        border-radius: 12px;
                        box-shadow: 0 6px 12px rgba(0,0,0,0.5);
                    }}
                    .card-flipped {{
                        transform: rotateY(180deg);
                    }}
                    .card-front, .card-back {{
                        position: absolute;
                        width: 100%;
                        height: 100%;
                        -webkit-backface-visibility: hidden;
                        backface-visibility: hidden;
                        border-radius: 12px;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        padding: 12px;
                        box-sizing: border-box;
                    }}
                    .card-front {{
                        background-image: url('{TAROT_BACK_IMAGE}');
                        background-size: cover;
                        background-position: center;
                        border: 2px solid #d4af37;
                        background-color: #0a111e;
                    }}
                    .card-back {{
                        background: linear-gradient(145deg, #0f172a, #1e293b);
                        color: #f3e5ab;
                        transform: rotateY(180deg);
                        border: 2px solid #d4af37;
                        font-weight: bold;
                        font-size: 15px;
                        text-shadow: 0 0 5px rgba(212, 175, 55, 0.5);
                    }}
                </style>
                <div class="card-container">
                    <div class="card-inner {'card-flipped' if is_selected else ''}">
                        <div class="card-front"></div>
                        <div class="card-back">
                            <div style="font-size: 11px; color: #a1a1aa; margin-bottom: 4px;">✨ 今日の献立 ✨</div>
                            <div>{recipe['name']}</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

                if st.button("めくる", key=f"tarot_btn_{idx}", use_container_width=True):
                    st.session_state.tarot_selected_idx = idx
                    st.rerun()

        # 結果表示
        if st.session_state.tarot_selected_idx is not None and st.session_state.tarot_selected_idx < actual_deck_size:
            selected_idx = st.session_state.tarot_selected_idx
            chosen_recipe = st.session_state.tarot_deck[selected_idx]

            st.markdown("---")
            st.success(f"🔮 運命のカードは 「**{chosen_recipe['name']}**」 でしたわ！")
            st.caption(f"{chosen_recipe.get('cuisine_category', '')} / {chosen_recipe.get('meal_category', '')}")

            if chosen_recipe.get("ingredients"):
                st.write("材料：" + "、".join(chosen_recipe["ingredients"]))
            if chosen_recipe.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(chosen_recipe["notes"])

            meal_time_for_log = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="tarot_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_tarot_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log, chosen_recipe["id"], "")
                st.success("記録モードに保存いたしましたわ！")

    # ==================================================================
    # 🌸 タブ2：ガチャガチャ
    # ==================================================================
    with tab_gacha:
        st.markdown("ハンドルを回して、今日の献立カプセルを取り出しましょう✨")

        if st.button("🎰 ガチャを回す", key="turn_gacha", type="primary", use_container_width=True):
            placeholder = st.empty()

            for i in range(3, 0, -1):
                placeholder.markdown(f"### 🌀 ガチャガチャ回転中... {i}")
                time.sleep(0.5)

            final_recipe = random.choice(candidates)
            st.session_state.gacha_result = final_recipe
            placeholder.empty()

        if st.session_state.get("gacha_result"):
            r = st.session_state.gacha_result

            st.markdown("---")
            st.success(f"🎉 カプセルの中から「**{r['name']}**」が出てまいりましたわ！")
            st.caption(f"{r.get('cuisine_category', '')} / {r.get('meal_category', '')}")

            if r.get("ingredients"):
                st.write("材料：" + "、".join(r["ingredients"]))
            if r.get("notes"):
                with st.expander("作り方・メモを見る"):
                    st.write(r["notes"])

            meal_time_for_log2 = st.selectbox("この結果を記録する食事区分", db.MEAL_TIME_CATEGORIES, key="gacha_log_time")
            if st.button("この結果を今日の記録に追加する", key="save_gacha_log"):
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.add_meal_log(today_str, meal_time_for_log2, r["id"], "")
                st.success("記録モードに保存いたしましたわ！")