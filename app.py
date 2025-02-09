import streamlit as st
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import japanize_matplotlib

st.title("株価比較ツール")

# 複数の銘柄コードを入力
stock_codes = st.text_area("銘柄コードを入力してください（例: 7203, 6758）", height=100)

# 現在の日付を選択
today = st.date_input("比較終了日を選択してください", datetime.datetime.now())

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

            # 5日移動平均線とボリンジャーバンドを計算
            df['SMA5'] = df['Close'].rolling(window=5).mean()
            df['BB_upper'] = df['SMA5'] + 1.5 * df['Close'].rolling(window=5).std()
            df['BB_lower'] = df['SMA5'] - 1.5 * df['Close'].rolling(window=5).std()

            # 差分を計算し、積算
            df['Diff'] = df['Close'] - df['SMA5']
            df['Cumulative_Pos'] = df['Diff'].clip(lower=0).cumsum()
            df['Cumulative_Neg'] = df['Diff'].clip(upper=0).cumsum()

            # チャートを表示
            plt.figure(figsize=(10, 6))
            plt.plot(df['Close'], label='終値', linewidth=4)  # 終値の線を太く
            plt.plot(df['SMA5'], label='5日移動平均線', linestyle='--')
            plt.plot(df['BB_upper'], label='判定バンド (上限)', linestyle='--', color='red')
            plt.plot(df['BB_lower'], label='判定バンド (下限)', linestyle='--', color='blue')
            plt.fill_between(df.index, df['BB_upper'], df['BB_lower'], color='gray', alpha=0.1)

            # 終値がボリンジャーバンドを超えた日を強調
            plt.scatter(df.index[df['Close'] > df['BB_upper']], df['Close'][df['Close'] > df['BB_upper']], color='red', label='判定バンド超え', marker='^',s=100, zorder=3)
            plt.scatter(df.index[df['Close'] < df['BB_lower']], df['Close'][df['Close'] < df['BB_lower']], color='blue', label='判定バンド下回り', marker='v',s=100, zorder=3)

            # 積算が10倍に達した日を強調
            plt.scatter(df.index[df['Cumulative_Pos'] >= 1.1 * df['SMA5']], df['Close'][df['Cumulative_Pos'] >= 1.1 * df['SMA5']], color='orange', label='積算 > 1.1倍 SMA5', marker='o',s=100, zorder=3)
            plt.scatter(df.index[df['Cumulative_Neg'] <= -1.1 * df['SMA5']], df['Close'][df['Cumulative_Neg'] <= -1.1 * df['SMA5']], color='purple', label='積算 < -1.1倍 SMA5', marker='x',s=100, zorder=3)

            # 比較開始日と終了日の株価で水平線を引く
            plt.axhline(y=price_two_months_ago, color='green', linewidth=0.5, label='開始日の株価')
            plt.axhline(y=current_price, color='purple', linewidth=0.5, label='終了日の株価')

            plt.title(f"{stock_code} 株価チャート")
            plt.legend(loc='upper left')  # 位置を左上に設定
            st.pyplot(plt)
        else:
            st.write(f"データが見つかりませんでした。銘柄コードを確認してください: {stock_code}")
