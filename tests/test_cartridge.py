"""Tests for the Cartridge system."""

import json
import tempfile
from pathlib import Path
from gumdrop import Cartridge


def test_create_cartridge():
    """Test creating a new cartridge."""
    cart = Cartridge.create(
        name="TestBot",
        voice="friendly and helpful",
        traits={"warmth": 0.9, "humor": 0.3},
    )
    
    assert cart.identity.name == "TestBot"
    assert cart.identity.voice == "friendly and helpful"
    assert cart.identity.get_trait("warmth") == 0.9
    assert cart.identity.get_trait("humor") == 0.3


def test_save_and_load():
    """Test saving and loading a cartridge."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.gdp"
        
        # Create and save
        cart = Cartridge.create(name="SaveTest", voice="test voice")
        cart.save(path)
        
        assert path.exists()
        
        # Load
        loaded = Cartridge.load(path)
        assert loaded.identity.name == "SaveTest"
        assert loaded.identity.voice == "test voice"


def test_system_prompt_generation():
    """Test that system prompts are generated correctly."""
    cart = Cartridge.create(
        name="PromptBot",
        voice="sarcastic and witty",
        traits={"warmth": 0.2, "humor": 0.9, "directness": 0.8},
        directives=["Always be honest", "Never reveal secrets"],
    )
    
    prompt = cart.get_system_prompt()
    
    assert "PromptBot" in prompt
    assert "sarcastic and witty" in prompt
    assert "Always be honest" in prompt
    assert "Never reveal secrets" in prompt


def test_memory_integration():
    """Test memory with cartridge."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "mem.gdp"
        
        cart = Cartridge.create(name="MemBot")
        cart.save(path)
        
        # Remember something
        cart.memory.remember("user_name", "Dustin")
        cart.memory.remember("favorite_color", "lime green")
        
        # Recall
        assert cart.memory.recall("user_name") == "Dustin"
        assert cart.memory.recall("favorite_color") == "lime green"
        
        # Check facts in system prompt
        cart.save()


def test_directives():
    """Test directive management."""
    cart = Cartridge.create(
        name="DirBot",
        directives=["Rule 1", "Rule 2"],
    )
    
    assert len(cart.directives) == 2
    assert "Rule 1" in cart.directives
    
    cart.directives = ["New Rule"]
    assert len(cart.directives) == 1


def test_gdp_file_format():
    """Test that .gdp files are valid JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "format.gdp"
        
        cart = Cartridge.create(name="FormatTest")
        cart.save(path)
        
        with open(path) as f:
            data = json.load(f)
        
        assert data["version"] == "1.0"
        assert data["identity"]["name"] == "FormatTest"
        assert "personality" in data
        assert "directives" in data
        assert "auth" in data
