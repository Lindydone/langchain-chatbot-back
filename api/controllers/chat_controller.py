from api.schemas.chat.chat import ChatRequest

class ChatController:
    def echo_message(self, req: ChatRequest) -> dict:
        """
        단순 에코 처리 (추후 AI 연동 로직으로 확장 가능)
        """
        return {"session_id": req.session_id, "reply": req.message}