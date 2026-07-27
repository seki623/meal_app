# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（カード直押し・余計なボタン完全排除版）
"""

import datetime
import random
import time
import os
import streamlit as st
import database as db

# 画像ファイルのパス
TAROT_BACK_IMAGE = "static/tarot_back.jpg"


def render_decision_page():
    # ==================================================================
    # 🌸 星空＆アニメーションCSS
    # ==================================================================
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@700&display=swap');

        :root {
            --navy: #030d22;
            --navy-2: #081231;
            --navy-3: #0d1c42;
            --gold: #c9a94f;
            --gold-2: #e0c47a;
            --ivory: #e8d9a8;
            --danger: #d97a7a;
        }

        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html, body, .stApp {
            color: var(--ivory) !important;
            font-family: 'Noto Sans JP', sans-serif !important;
            background: linear-gradient(180deg, var(--navy) 0%, var(--navy-2) 100%) !important;
            overflow-x: hidden;
        }

        /* ------------------------------------
           ✨ 淡く点滅する星空（30個）
        ------------------------------------ */
        .starfield {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        @keyframes twinkle {
            0%, 100% { opacity: 0.12; transform: scale(0.6); }
            50% { opacity: 0.95; transform: scale(1.3); }
        }

        .twinkle-star {
            position: absolute;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 5px #fff;
            animation: twinkle linear infinite;
        }

        .ts-1  { top: 08%; left: 12%; width: 2px; height: 2px; animation-duration: 3.2s; animation-delay: 0.0s; }
        .ts-2  { top: 18%; left: 82%; width: 3px; height: 3px; animation-duration: 4.5s; animation-delay: 1.2s; }
        .ts-3  { top: 32%; left: 22%; width: 2px; height: 2px; animation-duration: 2.8s; animation-delay: 2.4s; }
        .ts-4  { top: 42%; left: 72%; width: 2px; height: 2px; animation-duration: 5.1s; animation-delay: 0.7s; }
        .ts-5  { top: 52%; left: 08%; width: 3px; height: 3px; animation-duration: 3.8s; animation-delay: 3.1s; }
        .ts-6  { top: 62%; left: 88%; width: 2px; height: 2px; animation-duration: 4.2s; animation-delay: 1.8s; }
        .ts-7  { top: 72%; left: 28%; width: 2px; height: 2px; animation-duration: 3.0s; animation-delay: 0.4s; }
        .ts-8  { top: 82%; left: 58%; width: 3px; height: 3px; animation-duration: 4.8s; animation-delay: 2.9s; }
        .ts-9  { top: 12%; left: 42%; width: 2px; height: 2px; animation-duration: 3.5s; animation-delay: 1.5s; }
        .ts-10 { top: 28%; left: 92%; width: 2px; height: 2px; animation-duration: 4.0s; animation-delay: 3.7s; }
        .ts-11 { top: 48%; left: 38%; width: 3px; height: 3px; animation-duration: 5.5s; animation-delay: 0.2s; }
        .ts-12 { top: 68%; left: 16%; width: 2px; height: 2px; animation-duration: 3.3s; animation-delay: 2.1s; }
        .ts-13 { top: 78%; left: 92%; width: 2px; height: 2px; animation-duration: 4.1s; animation-delay: 1.0s; }
        .ts-14 { top: 88%; left: 32%; width: 3px; height: 3px; animation-duration: 3.7s; animation-delay: 2.6s; }
        .ts-15 { top: 04%; left: 62%; width: 2px; height: 2px; animation-duration: 4.6s; animation-delay: 0.9s; }
        .ts-16 { top: 15%; left: 25%; width: 2px; height: 2px; animation-duration: 3.9s; animation-delay: 1.1s; }
        .ts-17 { top: 24%; left: 65%; width: 3px; height: 3px; animation-duration: 4.3s; animation-delay: 0.5s; }
        .ts-18 { top: 38%; left: 05%; width: 2px; height: 2px; animation-duration: 3.1s; animation-delay: 2.7s; }
        .ts-19 { top: 46%; left: 82%; width: 2px; height: 2px; animation-duration: 5.0s; animation-delay: 1.9s; }
        .ts-20 { top: 58%; left: 48%; width: 3px; height: 3px; animation-duration: 3.6s; animation-delay: 0.3s; }
        .ts-21 { top: 66%; left: 76%; width: 2px; height: 2px; animation-duration: 4.4s; animation-delay: 3.3s; }
        .ts-22 { top: 76%; left: 04%; width: 2px; height: 2px; animation-duration: 3.4s; animation-delay: 1.6s; }
        .ts-23 { top: 86%; left: 78%; width: 3px; height: 3px; animation-duration: 4.9s; animation-delay: 2.2s; }
        .ts-24 { top: 94%; left: 18%; width: 2px; height: 2px; animation-duration: 3.7s; animation-delay: 0.8s; }
        .ts-25 { top: 02%; left: 35%; width: 2px; height: 2px; animation-duration: 4.2s; animation-delay: 2.5s; }
        .ts-26 { top: 22%; left: 50%; width: 3px; height: 3px; animation-duration: 5.2s; animation-delay: 1.4s; }
        .ts-27 { top: 36%; left: 55%; width: 2px; height: 2px; animation-duration: 2.9s; animation-delay: 3.0s; }
        .ts-28 { top: 54%; left: 28%; width: 2px; height: 2px; animation-duration: 4.7s; animation-delay: 0.6s; }
        .ts-29 { top: 70%; left: 62%; width: 3px; height: 3px; animation-duration: 3.3s; animation-delay: 2.0s; }
        .ts-30 { top: 92%; left: 52%; width: 2px; height: 2px; animation-duration: 4.0s; animation-delay: 1.3s; }

        /* ------------------------------------
           🌠 15秒に1回の控えめな流れ星
        ------------------------------------ */
        .shooting-star {
            position: absolute;
            top: 10%;
            right: 10%;
            width: 3px;
            height: 3px;
            background: #fff;
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.1), 0 0 20px rgba(255, 255, 255, 1);
            animation: shoot 15s linear infinite;
            opacity: 0;
        }
        .shooting-star::before {
            content: '';
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 180px;
            height: 1px;
            background: linear-gradient(90deg, rgba(255, 255, 255, 0.8), transparent);
        }

        @keyframes shoot {
            0% { transform: rotate(315deg) translateX(0); opacity: 0; }
            3% { opacity: 1; }
            15% { transform: rotate(315deg) translateX(-600px); opacity: 0; }
            100% { transform: rotate(315deg) translateX(-600px); opacity: 0; }
        }

        /* ------------------------------------
           ✨ 金色のふわふわ光アニメーション
        ------------------------------------ */
        @keyframes goldGlow {
            0%, 100% {
                box-shadow: 0 0 12px rgba(201, 169, 79, 0.3);
                border-color: var(--gold);
            }
            50% {
                box-shadow: 0 0 22px rgba(224, 196, 122, 0.6);
                border-color: var(--gold-2);
            }
        }

        @keyframes goldPulseBtn {
            0%, 100% { box-shadow: 0 8px 20px rgba(201, 169, 79, 0.3); }
            50% { box-shadow: 0 10px 28px rgba(224, 196, 122, 0.55); }
        }

        .brand {
            text-align: center;
            position: relative;
            z-index: 1;
        }

        .sub-caption {
            margin-top: 8px;
            font-size: 13px;
            color: var(--ivory);
            opacity: 0.85;
            letter-spacing: .05em;
        }

        /* 通常の操作ボタン（シャッフル・ガチャ・保存用） */
        .stButton > button {
            width: 100% !important;
            margin-top: 12px !important;
            padding: 14px 20px !important;
            border-radius: 14px !important;
            font-size: 16px !important;
            background: linear-gradient(135deg, var(--gold-2), var(--gold)) !important;
            color: #1c1408 !important;
            border: none !important;
            font-family: 'Shippori Mincho', serif !important;
            font-weight: 700 !important;
            letter-spacing: .08em !important;
            transition: .2s ease !important;
            animation: goldPulseBtn 4s infinite ease-in-out !important;
        }
        .stButton > button:active {
            transform: scale(0.98) !important;
        }

        /* ------------------------------------
           🂠 タロットカード専用ボタンデザイン（黄色ボタンを排除）
        ------------------------------------ */
        /* カード枠コンテナ内のボタンをカードそのものにする */
        .card-container div[data-testid="stButton"] > button {
            width: 100% !important;
            height: 210px !important;
            margin-top: 0 !important;
            padding: 12px !important;
            border-radius: 14px !important;
            border: 2px solid var(--gold) !important;
            animation: goldGlow 4s infinite ease-in-out !important;
            cursor: pointer !important;
            transition: transform 0.25s ease-in-out, background 0.3s !important;
            white-space: pre-wrap !important;
            word-break: break-word !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* カードホバー・アクティブ時 */
        .card-container div[data-testid="stButton"] > button:hover {
            transform: translateY(-4px) scale(1.02) !important;
        }
        .card-container div[data-testid="stButton"] > button:active {
            transform: scaleX(0) !important; /* 押し込んだ瞬間に横幅0に縮む */
        }

        /* 裏面カードスタイル */
        .card-container.back-card div[data-testid="stButton"] > button {
            color: var(--gold-2) !important;
            font-size: 32px !important;
            text-shadow: 0 0 10px rgba(224, 196, 122, 0.8) !important;
        }

        /* 表面（めくられた後）スタイル */
        .card-container.front-card div[data-testid="stButton"] > button {
            background: linear-gradient(145deg, var(--navy-3), var(--navy-2)) !important;
            color: var(--ivory) !important;
            font-family: 'Shippori Mincho', serif !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            line-height: 1.5 !important;
            text-shadow: 0 0 8px rgba(201, 169, 79, 0.6) !important;
            border-color: var(--gold-2) !important;
        }
    </style>

    <!-- 背景の星空（30個）＆流れ星 -->
    <div class="starfield">
        <div class="twinkle-star ts-1"></div><div class="twinkle-star ts-2"></div>
        <div class="twinkle-star ts-3"></div><div class="twinkle-star ts-4"></div>
        <div class="twinkle-star ts-5"></div><div class="twinkle-star ts-6"></div>
        <div class="twinkle-star ts-7"></div><div class="twinkle-star ts-8"></div>
        <div class="twinkle-star ts-9"></div><div class="twinkle-star ts-10"></div>
        <div class="twinkle-star ts-11"></div><div class="twinkle-star ts-12"></div>
        <div class="twinkle-star ts-13"></div><div class="twinkle-star ts-14"></div>
        <div class="twinkle-star ts-15"></div><div class="twinkle-star ts-16"></div>
        <div class="twinkle-star ts-17"></div><div class="twinkle-star ts-18"></div>
        <div class="twinkle-star ts-19"></div><div class="twinkle-star ts-20"></div>
        <div class="twinkle-star ts-21"></div><div class="twinkle-star ts-22"></div>
        <div class="twinkle-star ts-23"></div><div class="twinkle-star ts-24"></div>
        <div class="twinkle-star ts-25"></div><div class="twinkle-star ts-26"></div>
        <div class="twinkle-star ts-27"></div><div class="twinkle-star ts-28"></div>
        <div class="twinkle-star ts-29"></div><div class="twinkle-star ts-30"></div>
        <div class="shooting-star"></div>
    </div>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # メインコンテンツ
    # ------------------------------------------------------------------
    st.markdown('<div class="brand"><h1 style="font-family: \'Shippori Mincho\', serif; color: var(--gold-2); text-shadow: 0 0 12px rgba(224, 196, 122, 0.5);">🎯 決定モード</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="brand sub-caption">条件を絞り込んでから、神秘的なカードかガチャで献立を決定しますの🌸</div>', unsafe_allow_html=True)

    st.write("")

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
    # 🌸 タブ1：タロットカード
    # ==================================================================
    with tab_tarot:
        st.markdown('<div class="sub-caption" style="text-align: center;">カードをタップしてめくってくださいませ✨</div>', unsafe_allow_html=True)
        st.write("")

        num_cards = min(4, len(candidates))

        # 初期化・シャッフル
        if "tarot_deck" not in st.session_state or len(st.session_state.get("tarot_deck", [])) != num_cards or st.button("🂠 カードをシャッフルする", key="shuffle_tarot"):
            st.session_state.tarot_deck = random.sample(candidates, num_cards)
            st.session_state.tarot_selected_idx = None

        st.markdown("---")

        actual_deck_size = len(st.session_state.tarot_deck)
        cols = st.columns(actual_deck_size)

        has_image = os.path.exists(TAROT_BACK_IMAGE)
        bg_style = f"background-image: url('{TAROT_BACK_IMAGE}'); background-size: cover; background-position: center;" if has_image else "background: linear-gradient(135deg, var(--navy-3), var(--navy-2));"

        for idx in range(actual_deck_size):
            with cols[idx]:
                is_selected = (st.session_state.get("tarot_selected_idx") == idx)
                recipe = st.session_state.tarot_deck[idx]

                # 選択状態によってボタン（＝カード本体）のテキストとクラスを切り替え
                if not is_selected:
                    btn_text = "🔮" if not has_image else ""
                    container_class = "card-container back-card"
                else:
                    btn_text = f"✨ 今日の献立 ✨\n\n{recipe['name']}"
                    container_class = "card-container front-card"

                # カード枠用のdivで囲む
                st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)

                # 裏面画像がある場合のCSS（動的設定）
                if not is_selected and has_image:
                    st.markdown(f"""
                    <style>
                        .card-container.back-card div[data-testid="stButton"] > button {{
                            background-image: url('{TAROT_BACK_IMAGE}') !important;
                            background-size: cover !important;
                            background-position: center !important;
                        }}
                    </style>
                    """, unsafe_allow_html=True)

                # ボタンそのものがカードになります
                if st.button(btn_text, key=f"tarot_card_{idx}"):
                    st.session_state.tarot_selected_idx = idx
                    st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # 結果表示
        if st.session_state.get("tarot_selected_idx") is not None and st.session_state.tarot_selected_idx < actual_deck_size:
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
        st.markdown('<div class="sub-caption" style="text-align: center;">ハンドルを回して、今日の献立カプセルを取り出しましょう✨</div>', unsafe_allow_html=True)
        st.write("")

        if st.button("🎰 ガチャを回す", key="turn_gacha", type="primary", use_container_width=True):
            placeholder = st.empty()

            for i in range(3, 0, -1):
                placeholder.markdown(f"<h3 style='text-align:center; color:var(--gold-2); font-family: \"Shippori Mincho\", serif; text-shadow: 0 0 10px rgba(224,196,122,0.6);'>🌀 ガチャガチャ回転中... {i}</h3>", unsafe_allow_html=True)
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