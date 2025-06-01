from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage
import json
import re


llm = ChatOllama(model="gemma3:4b")


class UserIntentModel:

    def __init__(self):
        pass


    def detect_intent(self,user_input: str) -> str:
        try:
            messages = [
                SystemMessage(
                    content=(
                        "You are an intent classifier.\n"
                        "Classify the user input STRICTLY into ONLY ONE of the following categories:\n"
                        "1. chitchat\n"
                        "2. schedule\n"
                        "3. modify\n\n"
                        "STRICTLY Respond only in this JSON format:\n"
                        '{ "intent": "<chitchat or schedule or modify>"}'
                        "DO NOT BLUFF"
                    )
                ),
                HumanMessage(content=user_input)
            ]

            response = llm.invoke(messages)
            # print(response)
            content = response.content.strip()
            content = re.sub(r"```json|```", "", content).strip()
            # print(content)
            try:
                match = re.search(r'\{.*?\}', content, re.DOTALL)
                if match:
                    json_str = match.group(0).replace("'", '"')
                    parsed = json.loads(json_str)
                    print(parsed)
                    intent = parsed.get("intent", "chitchat")
                    if str(intent).lower() in ["chitchat", "schedule", "modify"]:
                        return str(intent).lower()
            except Exception as e:
                print("Intent parsing failed:", e)

            print("Raw model output:", response.content)
            return "chitchat"
        except Exception as e:
            return e



if __name__ == "__main__":
    ui = UserIntentModel()
    print(ui.detect_intent("Hey, can I reschedule my appointment to next Monday?"))  # -> modify
    print(ui.detect_intent("I want to book a new appointment for Tuesday"))          # -> schedule
    print(ui.detect_intent("How are you today?"))                                    # -> chitchat
    print(ui.detect_intent("Can you move my appointment with Dr. Smith from June 10 at 2 PM to June 12 at 3:30 PM?")) # -> modify