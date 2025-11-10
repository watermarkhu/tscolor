# Themes

TSColor uses YAML-based themes to define colors for syntax highlighting.

## Built-in Themes

TSColor comes with three built-in themes:

### Dark Themes

- **Dracula** - Popular dark theme with vibrant colors
- **Monokai** - Classic dark theme from Sublime Text

### Light Themes

- **GitHub Light** - Clean light theme inspired by GitHub's syntax highlighting

## Using Themes

### Get a Theme

```python
from tscolor import get_theme

theme = get_theme("dracula")
```

### List Themes

```python
from tscolor import list_themes

# List all themes
all_themes = list_themes()
print(all_themes)
# ['dracula', 'github-light', 'monokai']

# List only dark themes
dark_themes = list_themes(category="dark")
print(dark_themes)
# ['dracula', 'monokai']

# List only light themes
light_themes = list_themes(category="light")
print(light_themes)
# ['github-light']
```

### Get Theme Information

```python
from tscolor import get_theme_info

info = get_theme_info("dracula")
print(info)
# {
#     'name': 'Dracula',
#     'category': 'dark',
#     'author': 'Dracula Theme',
#     'description': 'A dark theme for many editors, shells, and more',
#     'url': 'https://draculatheme.com/'
# }
```

### Check Theme Category

```python
from tscolor import get_theme

theme = get_theme("dracula")

if theme.is_dark():
    print("Dark theme")
elif theme.is_light():
    print("Light theme")
```

## Theme Structure

Themes are defined in YAML files with the following structure:

```yaml
name: dracula
category: dark
author: Dracula Theme
description: A dark theme for many editors, shells, and more
url: https://draculatheme.com/

colors:
  foreground: "#f8f8f2"
  background: "#282a36"
  selection: "#44475a"
  comment: "#6272a4"

  # Syntax highlighting colors
  keyword: "#ff79c6"
  function: "#50fa7b"
  string: "#f1fa8c"
  number: "#bd93f9"
  type: "#8be9fd"
  variable: "#f8f8f2"
  constant: "#bd93f9"
  operator: "#ff79c6"
  # ... more colors
```

## Creating Custom Themes

You can create custom themes by:

1. Creating a YAML file with your theme definition
2. Registering it programmatically

### Example Custom Theme

Create a file `my-theme.yaml`:

```yaml
name: my-theme
category: dark
author: Your Name
description: My custom theme

colors:
  foreground: "#ffffff"
  background: "#000000"
  comment: "#888888"
  keyword: "#ff6188"
  function: "#a9dc76"
  string: "#ffd866"
  number: "#ab9df2"
  type: "#78dce8"
  variable: "#ffffff"
  constant: "#ab9df2"
  operator: "#ff6188"
```

### Register Custom Theme

```python
from tscolor.theme import Theme

# Load theme from YAML
theme = Theme.from_yaml("my-theme.yaml")

# Register it
from tscolor import register_theme
register_theme(theme)

# Now you can use it
theme = get_theme("my-theme")
```

## Theme Colors

Common capture names and their typical colors:

| Capture Name | Description | Dracula | Monokai |
|--------------|-------------|---------|---------|
| `keyword` | Language keywords (if, def, class) | Pink | Pink |
| `function` | Function names | Green | Green |
| `string` | String literals | Yellow | Yellow |
| `number` | Numeric literals | Purple | Purple |
| `comment` | Comments | Blue-gray | Brown |
| `type` | Type names | Cyan | Blue |
| `variable` | Variables | Foreground | Foreground |
| `constant` | Constants | Purple | Purple |
| `operator` | Operators (+, -, etc.) | Pink | Pink |
| `punctuation` | Brackets, parens | Foreground | Foreground |

## Color Format

Colors can be specified in hex format:

- **Full hex**: `#ff79c6`
- **Short hex**: `#f7c` (expanded to `#ff77cc`)

RGB values are automatically extracted from hex colors.

## Theme Metadata

### Required Fields

- `name` - Theme name (used as identifier)
- `category` - Either "light" or "dark"
- `colors` - Dictionary of color mappings

### Optional Fields

- `author` - Theme author name
- `description` - Theme description
- `url` - Theme homepage or documentation URL

## Fallback Colors

If a capture name is not defined in the theme, TSColor uses:

1. The `foreground` color if defined
2. White (`#ffffff`) as final fallback

## Theme Tips

### Creating a Dark Theme

- Use a dark background (#282a36, #2d2d2d, etc.)
- Use lighter foreground colors
- Ensure sufficient contrast for readability

### Creating a Light Theme

- Use a light background (#ffffff, #fafafa, etc.)
- Use darker foreground colors
- Test against white and light gray backgrounds

### Color Harmony

For best results:

- Choose a limited color palette (5-8 main colors)
- Use consistent hue relationships
- Test with real code samples
- Consider color blindness (avoid relying solely on red/green)

## Command Line

Use themes via the CLI:

```bash
# Use a specific theme
tscolor --theme monokai script.py

# List available themes
tscolor --list-themes
```
