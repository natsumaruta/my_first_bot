# 	•	.env に保存してある秘密情報（トークンやシークレット）を安全に読み込む
# 	•	Flask を使って LINE公式アカウントとつながるサーバー を立ち上げる準備をしている部分


import os  # OS（環境変数など）を扱う標準ライブラリを読み込む
from flask import Flask, request, abort  # FlaskのWebアプリ機能と、リクエスト処理・エラー中断を使う
from linebot import (
    LineBotApi,
    WebhookHandler,
)  # LINE公式SDK：メッセージ送信やWebhook処理を行うクラスを読み込む
from linebot.exceptions import (
    InvalidSignatureError,
)  # LINEから送られてきた署名が正しいか確認するためのエラークラス（exception：例外）
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)  # 受信・送信メッセージの型（テキスト用）を読み込む
from dotenv import load_dotenv  # .envファイル（環境変数をまとめたファイル）を読み込むための関数をインポート

load_dotenv(override=True)  # .envファイルの内容を環境変数として読み込む（既存の値があっても上書きする）

app = Flask(__name__)  # Flaskアプリを作成（__name__ はこのファイル自身のモジュール名）

# 環境変数からLINE公式アカウントの認証情報を取得
# LineBotApiとWebhookHandlerを入れると登録したチャネルを認識して動くようになる。
# os.environ：マシンにある環境変数（[""]内にあるもの）を参照する。load_dotenvすることで使えるようになるもの。
line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])  # LINE Messaging APIに接続するためのアクセストークン
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])  # Webhookの署名検証に使うチャンネルシークレット


@app.route("/")
def index():
    # ただただ文字列を返す処理
    return "You call index()"


@app.route("/callback", methods=["POST"])
def callback():
    """Messaging APIからの呼び出し関数"""
    # LINEがリクエストの改ざんを防ぐために付与する署名を取得
    signature = request.headers["X-Line-Signature"]
    # リクエストの内容をテキストで取得
    body = request.get_data(as_text=True)
    # ログに出力
    app.logger.info("Request body: " + body)

    try:
        # signature と body を比較することで、リクエストがLINEから送信されたものであることを検証
        handler.handle(body, signature)
    except InvalidSignatureError:
        # クライアントからのリクエストに誤りがあったことを示すエラーを返す
        abort(400)  # 400番を返す

    return "OK"


# テキストメッセージを受け取ったときの処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))


# このファイルが直接実行されたときだけ、この中を動かす
if __name__ == "__main__":
    # .env やシステムの環境変数から "PORT" という名前の値を取得する
    # 環境変数 PORT があればその番号で起動。なければ5000番で起動
    port = int(os.getenv("PORT", 8000))
    # どこからでもこのプログラムにアクセスできるようにapp.runでhost="0.0.0.0"とする
    app.run(host="0.0.0.0", port=port)
