from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

app = Flask(__name__)

# 여기에 당신의 Bot Token을 넣어주세요 (보안상 .env로 관리하는 것이 좋음)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")  # <-- 여기에 당신 토큰 입력
client = WebClient(token=SLACK_BOT_TOKEN)

@app.route("/gongji", methods=["POST"])
def gongji():
    text = request.form.get("text", "")
    user = request.form.get("user_name", "")

    try:
        # "채널명 메시지내용"으로 분리
        parts = text.strip().split()
        if len(parts) < 2:
            return jsonify({"text": "❗ 형식 오류: `/공지 [채널명] [메시지내용]` 형식으로 입력하세요."})

        channel_name = parts[0].lstrip("#")
        message = " ".join(parts[1:])

        # Slack API로 채널 리스트 받아서 이름 → ID 변환
        response = client.conversations_list()
        channel_id = None
        for ch in response["channels"]:
            if ch["name"] == channel_name:
                channel_id = ch["id"]
                break

        if not channel_id:
            return jsonify({"text": f"❗ 채널 `#{channel_name}`을 찾을 수 없습니다."})

        # 메시지 전송
        client.chat_postMessage(channel=channel_id, text=message)
        return jsonify({"text": f"✅ `#{channel_name}` 채널에 공지를 보냈습니다: \"{message}\""})

    except SlackApiError as e:
        return jsonify({"text": f"Slack API 오류: {e.response['error']}"})
    except Exception as e:
        return jsonify({"text": f"서버 오류: {str(e)}"})

if __name__ == "__main__":
    app.run(port=5000)
