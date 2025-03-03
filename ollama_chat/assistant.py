from ollama import chat
from ollama import ChatResponse
from ollama import list as models
import json

class Assistant():

    # available_models = []
    
    def __init__(self):
        self.system_messages = []
        self.message_history = []

        # set default message storage length
        self.message_history_length = 20

    def send_message(self, input_text: str, model: str):

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

        print(full_response)
        
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

        if input_length>0:
            self.message_history_length = input_length
        else:
            raise ValueError
        
        if len(self.message_history) > self.message_history_length:
            self.message_history = self.message_history[-self.message_history_length:]

    def export_data(self, data, filename: str):
        """Exports given data (chat messages or system messages) to a JSON file."""
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    def load_data(self, filename: str):
        """Loads data (chat messages or system messages) from a JSON file."""
        with open(filename, "r") as file:
            return json.load(file)  # Returns the loaded data

    def export_chat(self, filename: str):
        self.export_data(self.message_history, filename)

    def load_chat(self, filename: str):
        input_messages = self.load_data(filename)

        self.message_history = input_messages

    def export_system_messages(self, filename: str):
        self.export_data(self.system_messages, filename)


    def load_system_messages(self, filename: str):
        input_messages = self.load_data(filename)

        self.system_messages = input_messages

    def clear_chat(self):
        self.message_history = []


    def clear_system_messages(self):
        self.system_messages = []
    