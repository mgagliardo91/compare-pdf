"""Tests for OCR module."""

import pandas as pd
from pdf_ocr_diff.ocr import group_words_into_lines, _create_text_block_from_words


def test_group_words_into_lines_empty():
    """Test grouping with empty OCR data."""
    df = pd.DataFrame({
        'text': [],
        'conf': [],
        'left': [],
        'top': [],
        'width': [],
        'height': []
    })
    
    result = group_words_into_lines(df)
    assert result == []


def test_group_words_into_lines_single_line():
    """Test grouping words on a single line."""
    df = pd.DataFrame({
        'text': ['Hello', 'World'],
        'conf': [95, 95],
        'left': [10, 60],
        'top': [20, 20],
        'width': [40, 50],
        'height': [15, 15]
    })
    
    result = group_words_into_lines(df, line_height_tolerance=5)
    
    assert len(result) == 1
    assert result[0].text == "Hello World"
    assert result[0].bounding_box.x == 10
    assert result[0].bounding_box.y == 20
    assert result[0].bounding_box.width == 100  # 60 + 50 - 10
    assert result[0].line_number == 0


def test_group_words_into_lines_multiple_lines():
    """Test grouping words across multiple lines."""
    df = pd.DataFrame({
        'text': ['First', 'line', 'Second', 'line'],
        'conf': [95, 95, 95, 95],
        'left': [10, 60, 10, 70],
        'top': [20, 20, 50, 50],
        'width': [40, 40, 50, 50],
        'height': [15, 15, 15, 15]
    })
    
    result = group_words_into_lines(df, line_height_tolerance=5)
    
    assert len(result) == 2
    assert result[0].text == "First line"
    assert result[0].line_number == 0
    assert result[1].text == "Second line"
    assert result[1].line_number == 1


def test_group_words_filters_invalid_data():
    """Test that invalid OCR data is filtered out."""
    df = pd.DataFrame({
        'text': ['Valid', '', '  ', 'Also valid'],
        'conf': [95, -1, 90, 92],
        'left': [10, 50, 90, 130],
        'top': [20, 20, 20, 20],
        'width': [40, 40, 40, 40],
        'height': [15, 15, 15, 15]
    })
    
    result = group_words_into_lines(df, line_height_tolerance=5)
    
    assert len(result) == 1
    # Should only include "Valid" and "Also valid"
    assert result[0].text == "Valid Also valid"


def test_create_text_block_from_words():
    """Test creating a text block from word data."""
    words = [
        {'text': 'Hello', 'left': 10, 'top': 20, 'width': 40, 'height': 15},
        {'text': 'World', 'left': 60, 'top': 22, 'width': 50, 'height': 13}
    ]
    
    block = _create_text_block_from_words(words, line_number=5)
    
    assert block.text == "Hello World"
    assert block.line_number == 5
    # Bounding box should encompass both words
    assert block.bounding_box.x == 10
    assert block.bounding_box.y == 20
    assert block.bounding_box.width == 100  # 60 + 50 - 10
    assert block.bounding_box.height == 15  # 22 + 13 - 20
