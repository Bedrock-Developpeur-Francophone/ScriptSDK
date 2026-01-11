import json
import threading
import typing
from urllib import error, request

if typing.TYPE_CHECKING:
    from endstone_scriptsdk.handler import EventHandler


class Discord:
    @staticmethod
    def _normalize_webhook(value: str) -> str:
        if value.startswith("http://") or value.startswith("https://"):
            return value
        return f"https://discord.com/api/webhooks/{value}"

    @staticmethod
    def _post_webhook(url: str, payload: dict) -> int:
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ScriptSDK/1.8.1",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                return int(resp.getcode())
        except error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise Exception(f"HTTP {e.code}: {body}")

    @staticmethod
    def _parse_json(body: str):
        if not body:
            return None
        return json.loads(body)

    @staticmethod
    def _parse_bool(value: str) -> bool:
        if not value:
            return False
        return value.lower() in ["1", "true", "yes", "y", "on"]

    @staticmethod
    def _invalid_body(handler: "EventHandler", uuid: str):
        return handler.response(uuid, False, 400, ["invalid body"])

    @staticmethod
    def _schedule_response(handler: "EventHandler", uuid: str, success: bool, code: int, result: list[str]):
        handler.plugin.server.scheduler.run_task(
            handler.plugin,
            lambda: handler.response(uuid, success, code, result),
        )

    @staticmethod
    def request(handler: "EventHandler", uuid: str, action: str, message: str):
        match action:
            case "discordSendMessage":
                """
                    Body: webhookUrl;#;content;#;username;#;avatarUrl;#;tts;#;allowedMentionsJson
                """
                result = handler.deserializer(message, 6)
                if not result:
                    return Discord._invalid_body(handler, uuid)

                webhook_url = Discord._normalize_webhook(result[1])
                content = result[2]
                username = result[3]
                avatar_url = result[4]
                tts = Discord._parse_bool(result[5])
                allowed_mentions_json = result[6]

                try:
                    allowed_mentions = Discord._parse_json(allowed_mentions_json)
                except Exception as e:
                    return handler.response(uuid, False, 400, [str(e)])

                payload = {"content": content}
                if username:
                    payload["username"] = username
                if avatar_url:
                    payload["avatar_url"] = avatar_url
                if result[5]:
                    payload["tts"] = tts
                if allowed_mentions is not None:
                    payload["allowed_mentions"] = allowed_mentions

                def send():
                    try:
                        status = Discord._post_webhook(webhook_url, payload)
                        Discord._schedule_response(handler, uuid, True, 200, [str(status)])
                    except Exception as e:
                        Discord._schedule_response(handler, uuid, False, 500, [str(e)])

                threading.Thread(target=send).start()
                return None

            case "discordSendEmbed":
                """
                    Body: webhookUrl;#;embedsJson;#;content;#;username;#;avatarUrl;#;tts;#;allowedMentionsJson
                """
                result = handler.deserializer(message, 7)
                if not result:
                    return Discord._invalid_body(handler, uuid)

                webhook_url = Discord._normalize_webhook(result[1])
                embeds_json = result[2]
                content = result[3]
                username = result[4]
                avatar_url = result[5]
                tts = Discord._parse_bool(result[6])
                allowed_mentions_json = result[7]

                try:
                    embeds = Discord._parse_json(embeds_json)
                    if isinstance(embeds, dict):
                        embeds = [embeds]
                    if not isinstance(embeds, list):
                        return handler.response(uuid, False, 400, ["embeds must be a JSON object or array"])
                    allowed_mentions = Discord._parse_json(allowed_mentions_json)
                except Exception as e:
                    return handler.response(uuid, False, 400, [str(e)])

                payload = {"embeds": embeds}
                if content:
                    payload["content"] = content
                if username:
                    payload["username"] = username
                if avatar_url:
                    payload["avatar_url"] = avatar_url
                if result[6]:
                    payload["tts"] = tts
                if allowed_mentions is not None:
                    payload["allowed_mentions"] = allowed_mentions

                def send():
                    try:
                        status = Discord._post_webhook(webhook_url, payload)
                        Discord._schedule_response(handler, uuid, True, 200, [str(status)])
                    except Exception as e:
                        Discord._schedule_response(handler, uuid, False, 500, [str(e)])

                threading.Thread(target=send).start()
                return None

            case "discordSendPayload":
                """
                    Body: webhookUrl;#;payloadJson
                """
                result = handler.deserializer(message, 2)
                if not result:
                    return Discord._invalid_body(handler, uuid)

                webhook_url = Discord._normalize_webhook(result[1])
                payload_json = result[2]

                try:
                    payload = Discord._parse_json(payload_json)
                    if not isinstance(payload, dict):
                        return handler.response(uuid, False, 400, ["payload must be a JSON object"])
                except Exception as e:
                    return handler.response(uuid, False, 400, [str(e)])

                def send():
                    try:
                        status = Discord._post_webhook(webhook_url, payload)
                        Discord._schedule_response(handler, uuid, True, 200, [str(status)])
                    except Exception as e:
                        Discord._schedule_response(handler, uuid, False, 500, [str(e)])

                threading.Thread(target=send).start()
                return None
