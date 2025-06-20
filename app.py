from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# 여기에 당신의 Bot Token을 넣어주세요 (보안상 .env로 관리하는 것이 좋음)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")  # <-- 여기에 당신 토큰 입력
client = WebClient(token=SLACK_BOT_TOKEN)

@app.route("/gongji-debug", methods=["POST"])
def gongji_debug():
    text = request.form.get("text", "")
    user_id = request.form.get("user_id", "")
    user_name = request.form.get("user_name", "")
    channel_id = request.form.get("channel_id", "")
    channel_name = request.form.get("channel_name", "")
    team_id = request.form.get("team_id", "")

    print("====== [DEBUG: /gongji-debug 요청 수신] ======")
    print(f"text: {text}")
    print(f"user_id: {user_id}")
    print(f"user_name: {user_name}")
    print(f"channel_id: {channel_id}")
    print(f"channel_name: {channel_name}")
    print(f"team_id: {team_id}")
    print("=============================================")

    return jsonify({"text": f"✅ 디버깅 성공! text='{text}', user={user_name}"}), 200

@app.route("/gongji", methods=["POST"])
def gongji():
    text = request.form.get("text", "")
    user_id = request.form.get("user_id", "")  # 멘션용
    user_name = request.form.get("user_name", "")  # 로그 또는 디버그용

    try:
        # 채널명과 메시지 분리
        parts = text.strip().split()
        if len(parts) < 2:
            return jsonify({"text": "❗ 형식 오류: `/공지 [채널명] [메시지내용]` 형식으로 입력하세요."})

        channel_name = parts[0].lstrip("#")
        message = " ".join(parts[1:])

        # 채널 ID 찾기
        response = client.conversations_list()
        channel_id = None
        matched_channel = None
        for ch in response["channels"]:
            if channel_name in ch["name"]:
                channel_id = ch["id"]
                matched_channel = ch["name"]
                break
        
        if not channel_id:
            return jsonify({"text": f"❗ 입력한 채널 이름에 해당하는 채널을 찾을 수 없습니다: `{channel_name}`"})

        # 메시지 작성: @user_id: 메시지
        formatted_message = f"<@{user_id}>: {message}"

        # 메시지 전송
        client.chat_postMessage(channel=channel_id, text=formatted_message)
        return jsonify({"text": f"✅ `#{matched_channel}` 채널에 공지를 보냈습니다."})


    except SlackApiError as e:
        reason = e.response["error"]
        if reason == "not_in_channel":
            return jsonify({"text": "❗ 봇이 해당 채널에 초대되어 있지 않습니다. `/invite @공지봇`으로 초대한 후 다시 시도하세요."})
        return jsonify({"text": f"Slack API 오류({reason})로 인해 */공지*에 실패했습니다."})
    except Exception as e:
        return jsonify({"text": f"서버 오류: {str(e)}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
