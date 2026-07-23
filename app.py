# -*- coding: utf-8 -*-
"""
app.py
------
メインエントリーポイント。
セッション初期化とサイドバーメニューによる画面ルーティングを担当します。
"""

import streamlit as st
import database as db

# 各画面ビューの読み込み
from views.record_view import render_record_page
from views.search_view import render_search_page
from views.decision_view import render_decision_page

# ------------------------------------------------------------------
# 初期化
# ------------------------------------------------------------------
st.set_page_config(page_title="毎日ごはん記録＆献立ルーレット", page_icon="🍚", layout="wide")
db.init_db()

# セッションステート初期化
if "roulette_result" not in st.session_state:
    st.session_state.roulette_result = None
if "amidakuji_data" not in st.session_state:
    st.session_state.amidakuji_data = None
if "amidakuji_results" not in st.session_state:
    st.session_state.amidakuji_results = None
if "editing_recipe_id" not in st.session_state:
    st.session_state.editing_recipe_id = None

# ------------------------------------------------------------------
# サイドバー：ナビゲーション
# ------------------------------------------------------------------
st.sidebar.title("🍚 メニュー")
mode = st.sidebar.radio(
    "モードを選択してください",
    ["📅 記録モード", "🔍 検索モード", "🎯 決定モード"],
)

st.sidebar.markdown("---")
st.sidebar.caption("日々の食事を記録し、迷ったらルーレット・あみだくじで献立を決めよう！")

# ------------------------------------------------------------------
# 画面ルーティング
# ------------------------------------------------------------------
if mode == "📅 記録モード":
    render_record_page()
elif mode == "🔍 検索モード":
    render_search_page()
elif mode == "🎯 決定モード":
    render_decision_page()