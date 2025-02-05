import streamlit as st
import yfinance as yf
import datetime
import matplotlib.pyplot as plt

st.title("株価比較ツール")

# 複数の銘柄コードを入力
stock_codes = st.text_area("銘柄コードを入力してください（例: 7203, 6758）", height=100)

# 現在の日付を取得
today = datetime.datetime.now()

# 2ヶ月前の日付を選択
two_months_ago = st.date_input("比較開始日を選択してください", today - datetime.timedelta(weeks=8))

if stock_codes:
    stock_codes_list = [code.strip() + ".T" for code in stock_codes.split(",")]

    for stock_code in stock_codes_list:
        # 株価データを取得
        df = yf.download(stock_code, start=two_months_ago, end=today)

        if not df.empty:
            # 2ヶ月前と現在の株価を取得
            price_two_months_ago = df['Close'].iloc[0]
            current_price = df['Close'].iloc[-1]

            # 株価の比較結果を表示
            st.write(f"銘柄コード: {stock_code}")
            st.write(f"選択した日の株価: {price_two_months_ago}円")
            st.write(f"現在の株価: {current_price}円")
            st.write(f"変化率: {((current_price - price_two_months_ago) / price_two_months_ago) * 100:.2f}%")

            # チャートを表示
            st.line_chart(df['Close'])
        else:
            st.write(f"データが見つかりませんでした。銘柄コードを確認してください: {stock_code}")