from ollama import chat
from ollama import ChatResponse
from ollama import list as models

class Assistant():

    # available_models = []
    
    def __init__(self):
        self.system_messages = []
        self.message_history = []

        # set default message storage length
        self.message_history_length = 20

    def send_message(self, input_text: str, model: str) -> str:

        new_message = {'role': 'user', 'content': input_text}
        self.message_history.append(new_message)

        # maintain size of chat history
        if len(self.message_history) > self.message_history_length:
            self.message_history = self.message_history[-self.message_history_length:]

        input_messages = self.system_messages + self.message_history
        print(input_messages)
        response: ChatResponse = chat(model, messages=input_messages, stream=True)

        full_response = ""
        for chunk in response:
            text = chunk['message']['content']
            full_response += text
            yield text

        self.message_history.append({"role": "assistant", "content": full_response})

        return full_response

    def get_available_models(self) -> list[str]:
        available_models = models()

        model_names = [model['model'] for model in available_models['models']]

        if len(model_names) == 0:
            print("No Models Found")
            model_names.append("Unavailable")

        # self.available_models = model_names

        return model_names
    
    def add_system_message(self, input_text: str):
        self.system_messages.append({'role': 'system', 'content': input_text})

    def get_system_messages(self) -> list[str]:
        return self.system_messages
    
    def set_history_length(self, input_length):
        pass

    def export_chat(self, filename: str):
        pass

    def load_chat(self, filename: str):
        pass

    def clear_chat(self):
        pass
    