import pytest
from unittest.mock import patch
import sys
import os

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import prompt_choice, prompt_integer, prompt_seed

def test_prompt_choice():
    # 'invalid' is not an integer, '3' is not in [1, 2], '2' is valid
    with patch('builtins.input', side_effect=['invalid', '3', '2']):
        assert prompt_choice("Test choice", [1, 2]) == 2

def test_prompt_integer():
    # 'abc' is invalid, '0' is < min, '15' is > max, '5' is valid
    with patch('builtins.input', side_effect=['abc', '0', '15', '5']):
        assert prompt_integer("Test integer", min_val=1, max_val=10) == 5

def test_prompt_seed_valid():
    # 'abc' is invalid, '42' is valid integer
    with patch('builtins.input', side_effect=['abc', '42']):
        assert prompt_seed("Test seed") == 42

def test_prompt_seed_empty():
    # Empty input generates a random seed
    with patch('builtins.input', return_value=''):
        with patch('random.randint', return_value=123456):
            assert prompt_seed("Test seed") == 123456
