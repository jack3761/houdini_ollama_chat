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

        self.export_chat_button = QPushButton("Save Chat")
        self.export_chat_button.clicked.connect(self.export_chat)
        self.load_chat_button = QPushButton("Load Chat")
        self.load_chat_button.clicked.connect(self.load_chat)
        

        chat_button_layout = QHBoxLayout()
        chat_button_layout.addWidget(self.export_chat_button)
        chat_button_layout.addWidget(self.load_chat_button)

        self.export_system_messages_button = QPushButton("Save System Messages")
        self.export_system_messages_button.clicked.connect(self.export_system_messages)
        self.load_system_messages_button = QPushButton("Load System Messages")
        self.load_system_messages_button.clicked.connect(self.load_system_messages)


        system_button_layout = QHBoxLayout()
        system_button_layout.addWidget(self.export_system_messages_button)
        system_button_layout.addWidget(self.load_system_messages_button)

        model_layout = QHBoxLayout()
        message_button_layout = QVBoxLayout()

        message_button_layout.addLayout(chat_button_layout)
        message_button_layout.addLayout(system_button_layout)

        model_layout.addWidget(self.model_combobox)
        model_layout.addLayout(message_button_layout)

        self.input_system_message_field = QLineEdit()
        self.input_system_message_field.setPlaceholderText("Add a system message...")

        self.add_system_message_button = QPushButton("Send")
        self.add_system_message_button.clicked.connect(self.add_system_message)

        self.clear_system_message_button = QPushButton("Clear all")
        self.clear_system_message_button.clicked.connect(self.clear_system_messages)

        system_message_layout = QHBoxLayout()
        system_message_layout.addWidget(self.input_system_message_field)
        system_message_layout.addWidget(self.add_system_message_button)


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
        # layout.addWidget(self.model_combobox)
        layout.addLayout(model_layout)
        layout.addLayout(system_message_layout)
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

    def add_system_message(self):
        system_message = self.input_system_message_field.text()

        self.assistant.add_system_message(system_message)
        self.input_system_message_field.clear()

        self.chat_display.append(f"New System Message: {system_message}\n")

    def clear_system_messages(self) -> None:
        """Clear all system messages and update the chat display."""
        self.assistant.clear_system_messages()
        self.chat_display.append("All system messages cleared.\n")

    def export_system_messages(self):
        filename = QFileDialog.getSaveFileName(self, "Save System Messages", "", "JSON Files (*.json)")
        if filename:
            self.assistant.export_system_messages(filename)

    def load_system_messages(self):
        filename = QFileDialog.getOpenFileName(self, "Load System Messages", "", "JSON Files (*.json)")
        if filename:
            self.assistant.load_system_messages(filename)
            
    def export_chat(self):
        """
        Opens a file dialog to select a file path and exports chat messages
        using the assistant's export_chat function.
        """
        # Open a file dialog to select the file path
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chat", "", "JSON Files (*.json);;All Files (*)")

        # If a file path is selected, call the assistant's export_chat function
        if file_path:
            self.assistant.export_chat(file_path)

    def load_chat(self):
        filename = QFileDialog.getOpenFileName(self, "Load Chat", "", "JSON Files (*.json)")
        if filename:
            self.assistant.load_chat(filename)
        


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = OllamaChatAssistantGUI()
    dialog.show()
    app.exec_()