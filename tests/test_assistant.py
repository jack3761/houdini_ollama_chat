from ollama_chat.assistant import Assistant
import pytest

@pytest.fixture
def assistant():
    return Assistant()

def test_send_message(assistant):
    response = assistant.send_message("Hello", "llama3.1")
    assert isinstance(response, str)
    assert len(response) > 0


def test_get_available_models(assistant):
    available_models = assistant.get_available_models()
    assert isinstance(available_models, list)
    assert len(available_models) > 0

def test_add_system_message(assistant):
    assistant.add_system_message("Test system message")
    assert len(assistant.get_system_messages()) == 1
    assert assistant.get_system_messages()[0]['role'] == "system"
    assert assistant.get_system_messages()[0]['content'] == "Test system message"

def test_get_system_messages(assistant):
    assistant.add_system_message("System message 1")
    assistant.add_system_message("System message 2")
    
    system_messages = assistant.get_system_messages()
    assert len(system_messages) == 2
    assert system_messages[0]['content'] == "System message 1"
    assert system_messages[1]['content'] == "System message 2"