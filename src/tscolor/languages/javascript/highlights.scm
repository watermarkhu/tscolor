; Keywords
[
  "as"
  "async"
  "await"
  "break"
  "case"
  "catch"
  "class"
  "const"
  "continue"
  "debugger"
  "default"
  "delete"
  "do"
  "else"
  "export"
  "extends"
  "finally"
  "for"
  "from"
  "function"
  "get"
  "if"
  "import"
  "in"
  "instanceof"
  "let"
  "new"
  "of"
  "return"
  "set"
  "static"
  "switch"
  "target"
  "throw"
  "try"
  "typeof"
  "var"
  "void"
  "while"
  "with"
  "yield"
] @keyword

; Function definitions
(function_declaration
  name: (identifier) @function)

(function
  name: (identifier) @function)

(method_definition
  name: (property_identifier) @method)

(arrow_function) @function

; Function calls
(call_expression
  function: (identifier) @function.call)

(call_expression
  function: (member_expression
    property: (property_identifier) @method.call))

; Built-in objects
((identifier) @type.builtin
 (#match? @type.builtin "^(Array|Boolean|Date|Error|Function|Math|Number|Object|Promise|RegExp|String|Symbol|console|window|document|JSON|Map|Set|WeakMap|WeakSet)$"))

; Class definitions
(class_declaration
  name: (identifier) @class)

; Variables
(variable_declarator
  name: (identifier) @variable)

; Constants (all caps)
((identifier) @constant
 (#match? @constant "^[A-Z][A-Z_0-9]*$"))

; Constructor calls (capitalized)
((identifier) @constructor
 (#match? @constructor "^[A-Z]"))

; Parameters
(formal_parameters (identifier) @parameter)

; Properties
(property_identifier) @property
(shorthand_property_identifier) @property

; Literals
(this) @variable.builtin
(super) @variable.builtin
(true) @boolean
(false) @boolean
(null) @constant.builtin
(undefined) @constant.builtin
(number) @number
(string) @string
(template_string) @string
(regex) @string.escape
(escape_sequence) @string.escape

; Comments
(comment) @comment

; Operators
[
  "="
  "+"
  "-"
  "*"
  "/"
  "%"
  "**"
  "++"
  "--"
  "=="
  "==="
  "!="
  "!=="
  ">"
  ">="
  "<"
  "<="
  "&&"
  "||"
  "!"
  "??"
  "?."
  "&"
  "|"
  "^"
  "~"
  "<<"
  ">>"
  ">>>"
  "+="
  "-="
  "*="
  "/="
  "%="
  "**="
  "&&="
  "||="
  "??="
  "&="
  "|="
  "^="
  "<<="
  ">>="
  ">>>="
  "=>"
] @operator

; Punctuation
[
  ","
  "."
  ";"
  ":"
] @punctuation.delimiter

[
  "("
  ")"
  "["
  "]"
  "{"
  "}"
] @punctuation.bracket
