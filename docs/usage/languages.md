# Languages

TSColor supports any programming language with a tree-sitter parser.

## Supported Languages

Languages with built-in query files:

- **Python** - `tree-sitter-python`
- **JavaScript** - `tree-sitter-javascript`
- **MATLAB** - `tree-sitter-matlab`

Many more languages can be used with custom query files.

## Using Languages

### Register a Language

```python
from tscolor.languages import register_language
import tree_sitter_python as tsp

register_language("python", tsp.language())
```

### Get Configuration

```python
from tscolor.languages import get_configuration

config = get_configuration("python")
```

### Example

```python
import tree_sitter_python as tsp
import tree_sitter_javascript as tsj
from tscolor.languages import register_language, get_configuration
from tscolor import Highlighter, get_theme
from tscolor.formatters import AnsiFormatter

# Register languages
register_language("python", tsp.language())
register_language("javascript", tsj.language())

# Use Python
py_config = get_configuration("python")
py_source = b"def hello(): pass"

# Use JavaScript
js_config = get_configuration("javascript")
js_source = b"function hello() {}"

# Highlight
highlighter = Highlighter()
theme = get_theme("dracula")
formatter = AnsiFormatter(theme)

# Python
py_events = highlighter.highlight(py_config, py_source)
print(formatter.format(py_source, py_events, py_config))

# JavaScript
js_events = highlighter.highlight(js_config, js_source)
print(formatter.format(js_source, js_events, js_config))
```

## Language Configuration

Language configurations consist of:

1. **Highlights Query** - Defines syntax highlighting patterns
2. **Injections Query** (optional) - For embedded languages
3. **Locals Query** (optional) - For scope tracking

### Query Files

Query files are located in `tscolor/languages/{language}/`:

- `highlights.scm` - Required
- `injections.scm` - Optional
- `locals.scm` - Optional

## Adding New Languages

To add a new language:

1. Install the tree-sitter parser:
   ```bash
   pip install tree-sitter-{language}
   ```

2. Create query files in `tscolor/languages/{language}/`

3. Register the language:
   ```python
   import tree_sitter_{language} as tsl
   from tscolor.languages import register_language

   register_language("{language}", tsl.language())
   ```

### Example: Adding Rust

1. Install parser:
   ```bash
   pip install tree-sitter-rust
   ```

2. Create `tscolor/languages/rust/highlights.scm`:
   ```scheme
   (identifier) @variable
   (function_item name: (identifier) @function)
   "fn" @keyword
   "let" @keyword
   "mut" @keyword
   (string_literal) @string
   (integer_literal) @number
   (line_comment) @comment
   ```

3. Use it:
   ```python
   import tree_sitter_rust as tsr
   from tscolor.languages import register_language

   register_language("rust", tsr.language())
   config = get_configuration("rust")
   ```

## Language Detection

The CLI automatically detects languages from file extensions:

| Extension | Language |
|-----------|----------|
| .py | python |
| .js, .jsx | javascript |
| .ts, .tsx | typescript |
| .m | matlab |
| .rs | rust |
| .go | go |
| .c, .h | c |
| .cpp, .hpp, .cc, .cxx | cpp |
| .java | java |
| .rb | ruby |
| .php | php |
| .swift | swift |
| .kt | kotlin |
| .scala | scala |
| .html | html |
| .css | css |
| .json | json |
| .yaml, .yml | yaml |
| .sh, .bash, .zsh | bash |

## Query Language

Queries use the tree-sitter query language. See the [tree-sitter documentation](https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries) for details.

### Basic Patterns

```scheme
; Match any identifier
(identifier) @variable

; Match function definitions
(function_definition
  name: (identifier) @function)

; Match string literals
(string) @string

; Match keywords
"if" @keyword
"else" @keyword
"return" @keyword
```

### Capture Names

Common capture names:

- `@keyword` - Language keywords
- `@function` - Function names
- `@variable` - Variables
- `@type` - Type names
- `@string` - String literals
- `@number` - Numeric literals
- `@comment` - Comments
- `@operator` - Operators
- `@punctuation` - Punctuation
- `@constant` - Constants

## Resources

- [tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [tree-sitter Query Syntax](https://tree-sitter.github.io/tree-sitter/using-parsers#pattern-matching-with-queries)
- [tree-sitter Parsers](https://github.com/tree-sitter)
- [nvim-treesitter Queries](https://github.com/nvim-treesitter/nvim-treesitter/tree/master/queries) - Good reference for query files
