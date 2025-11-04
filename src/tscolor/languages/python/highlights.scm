; Keywords
[
  "and"
  "as"
  "assert"
  "async"
  "await"
  "break"
  "class"
  "continue"
  "def"
  "del"
  "elif"
  "else"
  "except"
  "finally"
  "for"
  "from"
  "global"
  "if"
  "import"
  "in"
  "is"
  "lambda"
  "nonlocal"
  "not"
  "or"
  "pass"
  "raise"
  "return"
  "try"
  "while"
  "with"
  "yield"
] @keyword

; Function definitions
(function_definition
  name: (identifier) @function)

(call
  function: (identifier) @function.call)

(call
  function: (attribute
    attribute: (identifier) @method.call))

; Built-in functions
((identifier) @function.builtin
 (#match? @function.builtin "^(abs|all|any|ascii|bin|bool|breakpoint|bytearray|bytes|callable|chr|classmethod|compile|complex|delattr|dict|dir|divmod|enumerate|eval|exec|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|isinstance|issubclass|iter|len|list|locals|map|max|memoryview|min|next|object|oct|open|ord|pow|print|property|range|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|vars|zip|__import__)$"))

; Types
((identifier) @type.builtin
 (#match? @type.builtin "^(bool|bytearray|bytes|dict|float|frozenset|int|list|set|str|tuple)$"))

; Class definitions
(class_definition
  name: (identifier) @class)

; Decorators
(decorator "@" @decorator)
(decorator (identifier) @decorator)

; Parameters
(parameters (identifier) @parameter)
(default_parameter name: (identifier) @parameter)
(typed_parameter (identifier) @parameter)
(typed_default_parameter name: (identifier) @parameter)

; Variables
(identifier) @variable

; Constants (all caps)
((identifier) @constant
 (#match? @constant "^[A-Z][A-Z_0-9]*$"))

; Literals
(none) @constant.builtin
(true) @boolean
(false) @boolean
(integer) @number
(float) @float
(string) @string
(escape_sequence) @string.escape

; Comments
(comment) @comment

; Operators
[
  "+"
  "-"
  "*"
  "/"
  "//"
  "%"
  "**"
  "="
  "+="
  "-="
  "*="
  "/="
  "//="
  "%="
  "**="
  "&="
  "|="
  "^="
  ">>="
  "<<="
  "<"
  ">"
  "<="
  ">="
  "=="
  "!="
  "->"
] @operator

; Punctuation
[
  ","
  "."
  ":"
  ";"
] @punctuation.delimiter

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket
