from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from .block_parser import BlockParser
from .core import BaseRenderer, BlockState
from .inline_parser import InlineParser
from .plugins import Plugin


class Markdown:
    """Markdown instance to convert markdown text into HTML or other formats.
    Here is an example with the HTMLRenderer::

        from mistune import HTMLRenderer

        md = Markdown(renderer=HTMLRenderer(escape=False))
        md('hello **world**')

    :param renderer: a renderer to convert parsed tokens
    :param block: block level syntax parser
    :param inline: inline level syntax parser
    :param plugins: mistune plugins to use
    """

    def __init__(
        self,
        renderer: Optional[BaseRenderer] = None,
        block: Optional[BlockParser] = None,
        inline: Optional[InlineParser] = None,
        plugins: Optional[Iterable[Plugin]] = None,
        enable_enhanced: bool = False,
    ):
        if block is None:
            block = BlockParser()

        if inline is None:
            inline = InlineParser()

        self.renderer = renderer
        self.block: BlockParser = block
        self.inline: InlineParser = inline
        self.enable_enhanced = enable_enhanced
        self.before_parse_hooks: List[Callable[["Markdown", BlockState], None]] = []
        self.before_render_hooks: List[Callable[["Markdown", BlockState], Any]] = []
        self.after_render_hooks: List[
            Callable[["Markdown", Union[str, List[Dict[str, Any]]], BlockState], Union[str, List[Dict[str, Any]]]]
        ] = []

        if plugins:
            for plugin in plugins:
                plugin(self)

        # Add hook to inject frontend code when enhanced features are enabled
        if self.enable_enhanced:
            def inject_frontend_code(md, result, state):
                if isinstance(result, str):
                    # Add CSS
                    css = '''
<style>
.tabs-container {
    border: 1px solid #ddd;
    border-radius: 4px;
    margin: 1em 0;
}
.tabs-title {
    background-color: #f5f5f5;
    padding: 0.5em 1em;
    border-bottom: 1px solid #ddd;
    font-weight: bold;
}
.tabs-nav {
    display: flex;
    border-bottom: 1px solid #ddd;
    background-color: #f9f9f9;
}
.tabs-nav button {
    padding: 0.5em 1em;
    border: none;
    background: none;
    cursor: pointer;
    border-bottom: 3px solid transparent;
}
.tabs-nav button.active {
    border-bottom-color: #0288d1;
    color: #0288d1;
    font-weight: bold;
}
.tabs-content {
    padding: 1em;
}
.tabs-content .tab-panel {
    display: none;
}
.tabs-content .tab-panel.active {
    display: block;
}
.tip-container {
    border: 1px solid #e1f5fe;
    border-radius: 4px;
    background-color: #e1f5fe;
    margin: 1em 0;
    padding: 1em;
}
.tip-title {
    font-weight: bold;
    margin-bottom: 0.5em;
    color: #0288d1;
}
</style>
                    '''
                    # Add JavaScript
                    js = '''
<script>
// Tab switching functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabContainers = document.querySelectorAll('.tabs-container');
    tabContainers.forEach(container => {
        const contentDiv = container.querySelector('.tabs-content');
        const codeBlocks = contentDiv.querySelectorAll('pre');
        const navDiv = container.querySelector('.tabs-nav');
        
        // Generate tab navigation based on code blocks
        const panels = [];
        codeBlocks.forEach((block, index) => {
            // Extract language from class name
            let language = 'code';
            const classList = block.querySelector('code').className;
            if (classList) {
                const match = classList.match(/language-(\w+)/);
                if (match) {
                    language = match[1];
                }
            }
            
            // Create tab button
            const button = document.createElement('button');
            button.textContent = language;
            button.dataset.tabIndex = index;
            navDiv.appendChild(button);
            
            // Create tab panel
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.appendChild(block.cloneNode(true));
            panels.push(panel);
            
            // Hide original code block
            block.style.display = 'none';
        });
        
        // Add panels to content
        panels.forEach(panel => {
            contentDiv.appendChild(panel);
        });
        
        // Set first tab as active
        if (panels.length > 0) {
            navDiv.querySelector('button').classList.add('active');
            panels[0].classList.add('active');
        }
        
        // Add click event listeners to tab buttons
        navDiv.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function() {
                const tabIndex = parseInt(this.dataset.tabIndex);
                
                // Remove active class from all buttons and panels
                navDiv.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
                panels.forEach(panel => panel.classList.remove('active'));
                
                // Add active class to clicked button and corresponding panel
                this.classList.add('active');
                panels[tabIndex].classList.add('active');
            });
        });
    });
});
</script>
                    '''
                    # Insert CSS at the beginning and JS at the end
                    result = css + result + js
                return result
            self.after_render_hooks.append(inject_frontend_code)

    def use(self, plugin: Plugin) -> None:
        plugin(self)

    def render_state(self, state: BlockState) -> Union[str, List[Dict[str, Any]]]:
        data = self._iter_render(state.tokens, state)
        if self.renderer:
            return self.renderer(data, state)
        return list(data)

    def _iter_render(self, tokens: Iterable[Dict[str, Any]], state: BlockState) -> Iterable[Dict[str, Any]]:
        for tok in tokens:
            if tok is None:
                continue
            if "children" in tok:
                children = self._iter_render(tok["children"], state)
                tok["children"] = list(children)
            elif "text" in tok:
                text = tok.pop("text")
                # process inline text
                # avoid striping emsp or other unicode spaces
                tok["children"] = self.inline(text.strip(" \r\n\t\f"), state.env)
            yield tok

    def parse(self, s: str, state: Optional[BlockState] = None) -> Tuple[Union[str, List[Dict[str, Any]]], BlockState]:
        """Parse and convert the given markdown string. If renderer is None,
        the returned **result** will be parsed markdown tokens.

        :param s: markdown string
        :param state: instance of BlockState
        :returns: result, state
        """
        if state is None:
            state = self.block.state_cls()

        # normalize line separator
        s = s.replace("\r\n", "\n")
        s = s.replace("\r", "\n")
        if not s.endswith("\n"):
            s += "\n"

        state.process(s)

        for hook in self.before_parse_hooks:
            hook(self, state)

        self.block.parse(state)

        for hook2 in self.before_render_hooks:
            hook2(self, state)

        result = self.render_state(state)

        for hook3 in self.after_render_hooks:
            result = hook3(self, result, state)
        return result, state

    def read(
        self, filepath: str, encoding: str = "utf-8", state: Optional[BlockState] = None
    ) -> Tuple[Union[str, List[Dict[str, Any]]], BlockState]:
        if state is None:
            state = self.block.state_cls()

        state.env["__file__"] = filepath
        with open(filepath, "rb") as f:
            s = f.read()

        s2 = s.decode(encoding)
        return self.parse(s2, state)

    def __call__(self, s: str) -> Union[str, List[Dict[str, Any]]]:
        if s is None:
            s = "\n"
        return self.parse(s)[0]
