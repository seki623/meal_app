# -*- coding: utf-8 -*-
"""
views/decision_view.py
-----------------------
🎯 決定モード（カード直接タップ・めくりアニメーション完全対応版）
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
           🂠 タロットカード＆幅収縮アニメーション
        ------------------------------------ */
        .tarot-card-box {
            position: relative;
            width: 100%;
            height: 200px;
            margin-bottom: 10px;
        }

        .card-element {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px;
            box-sizing: border-box;
            border: 2px solid var(--gold);
            animation: goldGlow 4s infinite ease-in-out;
            pointer-events: none;
            z-index: 1;
            transition: transform 0.2s ease-in-out;
        }

        /* タップ時に横幅を0に縮めるクラス */
        .card-element.flipping {
            transform: scaleX(0);
        }

        /* めくられた後の表面 */
        .card-back-face {
            background: linear-gradient(145deg, var(--navy-3), var(--navy-2));
            color: var(--ivory);
            font-family: 'Shippori Mincho', serif;
            font-weight: 700;
            font-size: 15px;
            text-shadow: 0 0 6px rgba(201, 169, 79, 0.5);
            text-align: center;
        }

        /* 🌸 カード上の透明ボタン */
        .tarot-card-box div[data-testid="stButton"] {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 10 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .tarot-card-box div[data-testid="stButton"] button {
            width: 100% !important;
            height: 200px !important;
            opacity: 0 !important;
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            cursor: pointer !important;
            margin: 0 !important;
            padding: 0 !important;
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

                if not is_selected:
                    card_html = f"""
                    <div class="tarot-card-box" id="card-box-{idx}">
                        <div class="card-element card-front-face" id="card-elem-{idx}" style="{bg_style}">
                            {'<div style="color:var(--gold-2); font-size:28px; filter: drop-shadow(0 0 6px rgba(224,196,122,0.8));">🔮</div>' if not has_image else ''}
                        </div>
                    </div>
                    """
                else:
                    card_html = f"""
                    <div class="tarot-card-box">
                        <div class="card-element card-back-face">
                            <div style="font-size: 10px; color: var(--gold-2); margin-bottom: 6px; letter-spacing: .05em;">✨ 今日の献立 ✨</div>
                            <div>{recipe['name']}</div>
                        </div>
                    </div>
                    """

                st.markdown(card_html, unsafe_allow_html=True)

                # カード押下時のイベント
                if st.button("", key=f"tarot_btn_{idx}"):
                    st.session_state.tarot_selected_idx = idx
                    st.rerun()

        # JavaScriptによるリアルタイムタップ時のアニメーション連動
        st.components.v1.html("""
        <script>
            const doc = window.parent.document;
            const boxes = doc.querySelectorAll('.tarot-card-box');
            
            boxes.forEach((box) => {
                const btn = box.querySelector('button');
                const elem = box.querySelector('.card-element');
                
                if (btn && elem && !btn.dataset.hasListener) {
                    btn.dataset.hasListener = "true";
                    btn.addEventListener('click', (e) => {
                        // タップ時に幅を0にアニメーション縮小させる
                        elem.classList.add('flipping');
                    });
                }
            });
        </script>
        """, height=0)

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