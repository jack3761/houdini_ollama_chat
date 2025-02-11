from ollama import chat
from ollama import ChatResponse
from ollama import list as models

class Assistant():

    # available_models = []
    
    def __init__(self):
        self.system_messages = []

    def send_message(self, input_text: str, model: str) -> str:
        input_messages = self.system_messages + [{'role': 'user', 'content': input_text}]
        response: ChatResponse = chat(model, messages=input_messages)

        return response.message.content

    def get_available_models(self) -> list[str]:
        available_models = models()

        model_names = [model['model'] for model in available_models['models']]

        if len(model_names) == 0:
            print("No Models Found")
            model_names.append("Unavailable")

        # self.available_models = model_names

        return model_names
    
    def add_system_message(self, input_text):
        self.system_messages.append([{'role': 'system', 'content': input_text}])

    def get_system_messages(self) -> list[str]:
        return self.system_messages