from ollama_chat.assistant import Assistant
from PySide2 import QtWidgets
from PySide2.QtWidgets import *

class OllamaChatAssistantGUI(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ollama Chat Assistant")
        self.resize(500, 400)

        self.assistant = Assistant()

        self.model_combobox = QComboBox()
        self.populate_models()

        self.chat_display = QTextBrowser()
        # self.chat_display.setReadOnly(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        message_layout = QHBoxLayout()
        message_layout.addWidget(self.input_field)
        message_layout.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Model"))
        layout.addWidget(self.model_combobox)
        layout.addWidget(self.chat_display)
        layout.addLayout(message_layout)
        self.setLayout(layout)

    def populate_models(self):        

        models = self.assistant.get_available_models()

        for model in models:
            self.model_combobox.addItem(model)

    def send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        selected_model = self.model_combobox.currentText()
        response = self.assistant.send_message(user_message, selected_model)

        self.chat_display.append(f"User: {user_message}")
        self.chat_display.append(f"Assistant: {response}\n")

        self.input_field.clear()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = OllamaChatAssistantGUI()
    dialog.show()
    app.exec_()