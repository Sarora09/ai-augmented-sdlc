from typing import List

class BytesConverter:

    @staticmethod
    def convert_to_text_bytes(messages: List):
        text_messages = []
        for role, content in messages:
            if role != "messages":
                text_messages.append(f"{role}: {content}")
                text_messages.append("")
        return "\n".join(text_messages)