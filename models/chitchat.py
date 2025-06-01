import sys
sys.path.append(r"C:\Users\unmes\Documents\RAGful_dev\meet_scheduler")

from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage
from prompts.chitchat_prompt import CHITCHAT_PROMPT

llm = ChatOllama(model="gemma3:4b") 


class ChitChatModel:
    def __init__(self):
        pass


    def chitchat(self,user_input: str) -> str:
        try:
            system_prompt = CHITCHAT_PROMPT.format(user_input=user_input)
            response = llm.invoke([HumanMessage(content=system_prompt.strip())])
            answer = response.content.strip()
            return answer
        except Exception as e:
            print("ERROR[CHITCHAT]",e)
            return None


if __name__ == "__main__":
    ccm = ChitChatModel()
    user_input = "How are you today?"
    reply = ccm.chitchat(user_input)
    print("Assistant:", reply)