from ollama_chat.assistant import Assistant
import pytest
import json

@pytest.fixture
def assistant():
    return Assistant()

def test_send_message(assistant):
    response = "".join(assistant.send_message("Hello", "llama3.1"))
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


def test_set_history_length(assistant):
    """Ensure set_history_length correctly updates and trims history."""
    assistant.message_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm good, thanks!"}
    ]
    
    assistant.set_history_length(2)
    
    assert len(assistant.message_history) == 2  # History should be trimmed
    assert assistant.message_history[0]["content"] == "How are you?"  # Older messages removed

    # Ensure negative or zero history length is not allowed
    with pytest.raises(ValueError):
        assistant.set_history_length(0)
    with pytest.raises(ValueError):
        assistant.set_history_length(-5)

def test_export_data(assistant, tmp_path):
    """Ensure export_data correctly saves to a file."""
    data = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    file_path = tmp_path / "test_data.json"
    
    assistant.export_data(data, str(file_path))

    assert file_path.exists()

    with open(file_path, "r") as file:
        loaded_data = json.load(file)

    assert loaded_data == data

def test_load_data(assistant, tmp_path):
    """Ensure load_data correctly restores from a file."""
    data = [
        {"role": "user", "content": "Hey!"},
        {"role": "assistant", "content": "Hello!"}
    ]
    file_path = tmp_path / "test_data.json"

    with open(file_path, "w") as file:
        json.dump(data, file)

    loaded_data = assistant.load_data(str(file_path))

    assert loaded_data == data

    # Test missing file
    with pytest.raises(FileNotFoundError):
        assistant.load_data(str(tmp_path / "missing.json"))

    # Test corrupted file
    corrupted_file_path = tmp_path / "corrupted.json"
    with open(corrupted_file_path, "w") as file:
        file.write("not valid json")

    with pytest.raises(json.JSONDecodeError):
        assistant.load_data(str(corrupted_file_path))

def test_clear_chat(assistant):
    assistant.send_message("This is a test message", "llama3.1")
    assistant.send_message("This is another test message", "llama3.1")

    assistant.clear_chat()

    assert len(assistant.message_history) == 0