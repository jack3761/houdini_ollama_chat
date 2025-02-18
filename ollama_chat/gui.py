from ollama_chat.assistant import Assistant
from PySide2 import QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import QThread, Signal
from PySide2.QtGui import QTextCursor
import markdown2



class ChatWorker(QThread):
    new_text = Signal(str)
    finished = Signal()

    def __init__(self, assistant, user_input, model):
        super().__init__()
        self.assistant = assistant
        self.user_input = user_input
        self.model = model

    def run(self):
        response_text = ""  # Accumulate the entire response here (not emitted)

        # For each chunk in the response, accumulate and emit just the latest chunk
        for chunk in self.assistant.send_message(self.user_input, self.model):
            response_text += chunk  # Add the new chunk to the accumulated response
            self.new_text.emit(chunk)  # Emit only the new chunk
            

        self.finished.emit()

class OllamaChatAssistantGUI(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ollama Chat Assistant")
        self.resize(1000, 800)

        self.assistant = Assistant()

        self.model_combobox = QComboBox()
        self.populate_models()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.format_chat_display()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.handle_send_message)

        message_layout = QHBoxLayout()
        message_layout.addWidget(self.input_field)
        message_layout.addWidget(self.send_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Model"))
        layout.addWidget(self.model_combobox)
        layout.addWidget(self.chat_display)
        layout.addLayout(message_layout)
        self.setLayout(layout)

    def format_chat_display(self):
        font = self.chat_display.font()
        font.setPointSize(12)  # Adjust size
        font.setFamily("Arial")  # Use a cleaner font
        self.chat_display.setFont(font)
        self.chat_display.setStyleSheet("QTextEdit { padding: 10px; }")  # Add spacing

    def populate_models(self):        

        models = self.assistant.get_available_models()

        for model in models:
            self.model_combobox.addItem(model)

    def handle_send_message(self):
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self.chat_display.append(f"User: {user_message}")
        self.chat_display.append(f"Assistant: \n")
        self.input_field.clear()        

        selected_model = self.model_combobox.currentText()
        # response = self.assistant.send_message(user_message, selected_model)
        self.worker = ChatWorker(self.assistant, user_message, selected_model)

        self.worker.new_text.connect(self.update_response)
        self.worker.finished.connect(self.finish_response)

        self.worker.start()

    def update_response(self, text):
        """Update chat window with the new chunk of text."""
        self.chat_display.moveCursor(QTextCursor.End)  # Move cursor to end

        # html_text = markdown2.markdown(text)
        self.chat_display.insertPlainText(text)  # Insert text without new lines

        
    def finish_response(self):
        """Called when the response streaming is finished. Applies Markdown only to the last assistant message."""
        current_text = self.chat_display.toMarkdown()
        self.chat_display.setMarkdown(current_text)
        self.chat_display.moveCursor(QTextCursor.End)  # Move cursor to end
        self.chat_display.ensureCursorVisible()
        


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = OllamaChatAssistantGUI()
    dialog.show()
    app.exec_()