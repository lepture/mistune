# Mistune Architecture

## 1. System Overview

Mistune is a Python Markdown parser that converts Markdown text into structured tokens and renders those tokens into HTML or other output formats. Its architecture separates block-level parsing, inline parsing, token management, rendering, and plugin extensions.

The main processing flow is:

```text
             Markdown Input
                    |
                    v
              Markdown
              Coordinator
                    |
          +---------+---------+
          |                   |
          v                   v
      BlockParser        BlockState
          |
          v
      InlineParser
          |
          v
       Token Tree
          |
          v
      BaseRenderer
          |
          v
       HTMLRenderer
          |
          v
        HTML Output

  Plugins and Directives extend parsing
  and rendering at designated points.
```

## 2. Main Components

### 2.1 Markdown Coordinator
**File:** `src/mistune/markdown.py`

The `Markdown` class coordinates the complete parsing and rendering process. It initializes the block parser, inline parser, and renderer. It also registers plugins and supports hooks before parsing, before rendering, and after rendering.

It processes input, invokes the block parser, converts inline text into child tokens, and passes the resulting tokens to the renderer.

### 2.2 BlockParser
**File:** `src/mistune/block_parser.py`

The `BlockParser` identifies block-level Markdown structures, including headings, lists, blockquotes, fenced code blocks, and thematic breaks.

It uses parsing rules and regular expressions to identify these structures and produces tokens representing them. It also supports nested parsing inside lists and blockquotes.

### 2.3 InlineParser
**File:** `src/mistune/inline_parser.py`

The `InlineParser` handles inline Markdown syntax, such as emphasis, strong text, links, images, code spans, and line breaks.

It processes text within block-level tokens and generates inline tokens. Plugins can register additional inline parsing rules.

### 2.4 Core State and Token Management
**File:** `src/mistune/core.py`

The core module provides shared parsing and rendering abstractions.

- `BlockState` stores the source text, parsing cursor, generated tokens, parent state, and environment.
- `InlineState` stores inline parsing information and tokens.
- `BaseRenderer` provides common rendering functionality and supports custom rendering methods.

Nested block states share the parent's environment, allowing information such as reference links to be reused.

### 2.5 Renderer
**File:** `src/mistune/renderers/html.py`

`HTMLRenderer` converts parsed tokens into HTML elements. It provides methods for rendering headings, paragraphs, links, images, code blocks, and other Markdown structures.

It also handles HTML escaping and URL sanitization. Custom rendering methods can be registered through the base renderer.

### 2.6 Plugins
**File:** `src/mistune/plugins/__init__.py`

Plugins extend Mistune without requiring changes to the central parsing workflow.

A plugin can register additional block parsing rules, inline parsing rules, or renderer methods. Plugins can be supplied to `create_markdown()` and are applied when a `Markdown` instance is initialized.

### 2.7 Directives
**Directory:** `src/mistune/directives/`

Directives provide an extension mechanism for more structured block-level content.

The directive system contains:
- `BaseDirective`: manages directive parsing and registration.
- `DirectiveParser`: defines how directive type, title, and content are extracted.
- `FencedDirective`: supports fenced directive syntax.
- `Admonition`: implements note, warning, tip, and related directive types.

Directives can generate nested tokens by parsing their content through the block parser. They can also register corresponding rendering methods.

## 3. Architecture Decisions

The following decisions are inferred from the implementation rather than documented as formal ADRs in the repository.

### ADR 1: Separate Block and Inline Parsing
**Status:** Inferred

**Context:** Markdown contains both block-level structures and inline formatting.

**Decision:** Mistune uses separate `BlockParser` and `InlineParser` components.

**Alternatives:** A single parser handling all Markdown syntax.

**Consequences:** The responsibilities are separated, making parsing rules easier to organize and extend. The coordinator must manage the interaction between both parsers.

### ADR 2: Token-Based Rendering
**Status:** Verified

**Context:** Parsing Markdown and generating output are different responsibilities.

**Decision:** Mistune produces structured tokens and passes them to a renderer.

**Alternatives:** Generate HTML directly while parsing the input.

**Consequences:** Different renderers can consume the same parsed representation. The HTML renderer can evolve separately from the parsing logic.

### ADR 3: Extensibility Through Plugins
**Status:** Verified

**Context:** New Markdown syntax should be supported without modifying the central parsing workflow for every extension.

**Decision:** Mistune provides plugins that register parsing rules and rendering methods.

**Alternatives:** Implement every extension directly inside the core parser.

**Consequences:** Extensions can be added independently. However, plugins must register compatible parsing and rendering behaviour.

## 4. Architectural Constraints

1. **Parsing and rendering are separate responsibilities.** The Markdown coordinator produces tokens before invoking the renderer. Evidence: `src/mistune/markdown.py`, lines 53–57 and 93–102.

2. **Block and inline parsing use separate parser components.** Evidence: `src/mistune/markdown.py`, lines 3–5 and 24–39.

3. **Nested parsing must respect the configured nesting limit.** Evidence: `src/mistune/core.py`, line 28; `src/mistune/block_parser.py`, lines 88–108; `src/mistune/inline_parser.py`, lines 93–107.

4. **Plugins must follow the plugin interface and register through the Markdown instance.** Evidence: `src/mistune/plugins/__init__.py`, lines 26–28 and `src/mistune/markdown.py`, lines 46–51.

5. **Generated HTML attributes and URLs must follow renderer safety rules.** Evidence: `src/mistune/renderers/html.py`, lines 58–74 and 76–88.

## 6. Summary

Mistune uses a modular, extensible architecture. The Markdown coordinator connects separate block and inline parsers, shared token and state abstractions, and renderers. Plugins and directives extend the system by registering additional parsing and rendering behaviour.

This separation allows new syntax and output behaviour to be introduced while keeping the central parsing workflow relatively independent of individual extensions.