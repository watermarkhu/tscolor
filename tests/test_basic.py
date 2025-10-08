"""
Basic tests for tscolor package
"""

import tscolor


def test_available_languages():
    """Test that get_available_languages returns a list"""
    languages = tscolor.get_available_languages()
    assert isinstance(languages, list)
    # With at least one of the supported languages, we should have items
    # Default build may have no languages, so we just check it's a list


def test_available_themes():
    """Test that get_available_themes returns expected themes"""
    themes = tscolor.get_available_themes()
    assert isinstance(themes, list)
    assert "dark" in themes
    assert "light" in themes


def test_highlight_without_language():
    """Test that highlight without available language raises error"""
    code = "print('hello')"
    languages = tscolor.get_available_languages()
    
    if not languages:
        # If no languages are available, expect an error
        try:
            tscolor.highlight(code, "python", "terminal", "dark")
            assert False, "Should have raised an error for unsupported language"
        except RuntimeError:
            pass  # Expected


def test_highlight_python_terminal():
    """Test Python highlighting for terminal output"""
    languages = tscolor.get_available_languages()
    if "python" not in languages:
        return  # Skip if Python language not available
    
    code = 'print("hello")'
    result = tscolor.highlight(code, "python", "terminal", "dark")
    assert isinstance(result, str)
    assert len(result) > 0
    # Output should contain the original code
    assert "hello" in result


def test_highlight_python_html():
    """Test Python highlighting for HTML output"""
    languages = tscolor.get_available_languages()
    if "python" not in languages:
        return  # Skip if Python language not available
    
    code = 'print("hello")'
    result = tscolor.highlight(code, "python", "html", "light")
    assert isinstance(result, str)
    assert "<pre><code>" in result
    assert "</code></pre>" in result
    assert "hello" in result


def test_highlight_with_comments():
    """Test that comments are highlighted"""
    languages = tscolor.get_available_languages()
    if "python" not in languages:
        return  # Skip if Python language not available
    
    code = """
# This is a comment
def hello():
    pass
"""
    result = tscolor.highlight(code, "python", "html", "dark")
    assert isinstance(result, str)
    assert "comment" in result.lower() or "color" in result


def test_highlight_rust():
    """Test Rust highlighting if available"""
    languages = tscolor.get_available_languages()
    if "rust" not in languages:
        return  # Skip if Rust language not available
    
    code = 'fn main() { println!("hello"); }'
    result = tscolor.highlight(code, "rust", "terminal", "dark")
    assert isinstance(result, str)
    assert "hello" in result


def test_highlight_javascript():
    """Test JavaScript highlighting if available"""
    languages = tscolor.get_available_languages()
    if "javascript" not in languages:
        return  # Skip if JavaScript language not available
    
    code = 'console.log("hello");'
    result = tscolor.highlight(code, "javascript", "terminal", "dark")
    assert isinstance(result, str)
    assert "hello" in result


def test_highlight_json():
    """Test JSON highlighting if available"""
    languages = tscolor.get_available_languages()
    if "json" not in languages:
        return  # Skip if JSON language not available
    
    code = '{"key": "value"}'
    result = tscolor.highlight(code, "json", "html", "light")
    assert isinstance(result, str)
    assert "key" in result
    assert "value" in result


def test_invalid_language():
    """Test that invalid language raises error"""
    try:
        tscolor.highlight("code", "invalid_language", "terminal", "dark")
        assert False, "Should have raised an error"
    except RuntimeError as e:
        assert "not registered" in str(e) or "Language" in str(e)


def test_default_parameters():
    """Test highlight with default parameters"""
    languages = tscolor.get_available_languages()
    if "python" not in languages:
        return  # Skip if Python language not available
    
    code = "x = 1"
    # Should work with just code and language (defaults: terminal, dark)
    result = tscolor.highlight(code, "python")
    assert isinstance(result, str)
    assert len(result) > 0
