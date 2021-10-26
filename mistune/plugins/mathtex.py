"""
Mistune Math Plugin.

Copyright (c) 2021, Kevin Crouse. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of the creator nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
# Mistune Math Plugin.

This plugin supports the very common $..$ and $$..$$ extended syntax for latex math inclusion in markdown. Certain pacakage parameters are modifiable to reflect specific markdown parser flavors.

## Features

- The plugin supports three distinct plugin names: 
    - 'mathblock', which represents the $$..$$ math syntax that usually is rendered as a block display.
    - 'mathspan', which represents the $..$ math syntax that usually is rendered as an inline display.
    - 'math' will call the plugin_allmath function, which simply includes both $..$ as mathspan and $$..$$ as mathblock.
- The plugin allows for the mathblock $$ token to be space-padded, e.g. $$ \\alpha $$. 
- mathspan $ tokens may not be space padded as it creates syntax conflict with currency usage (and no major parser supports this).
- The plugin supports multiline equations so long as each consecutive line between the open and close tokens have text. Multiline support does not cross paragraph breaks.
- In cases of uneven start and end tokens, $$..$ and $..$$ will both be rendered as math spans with an extra $ token.


## Usage 

The following package variables may be altered to modify the plugin operation:
- ALLOW_SPACE_PADDING: If True, allows math blocks to be space padded, i.e. $$ x**2 $$ in addition to $$x**2$$ . Default is True.
- MATHSPAN_DOUBLE_TOKEN: If True, the mathspan plugin looks for the double dollar sign for its token, which we see in dillinger.io's implementation. Note that in this case the mathblock plugin should not be used at all as they will conflict.


## Comparison by Major Parsers

- StackEdit's KaTeX implementation matches the full set of usage and features provided. 
- Typora's math is exclusively '$$' math blocks. There is no support for inline spans.
- dillinger.io's math implementation:
    - does not recognize the $..$ math span at all.
    - renders $$..$$ the same as an inline math span.
    - does not allow padded tokens, i.e. $$ \alpha $$ does not render but $$\alpha$$ does.

 
"""
import re 

# the parsers are needed to separte return types 
# for inline vs block parsers.
# They have different interfaces for some reason.
from .. import block_parser, inline_parser

__all__ = [
    'plugin_mathspan', 
    'plugin_mathblock',
    'plugin_allmath',
]

ALLOW_SPACE_PADDING = True
MATHSPAN_DOUBLE_TOKEN = False

# Define the renderers 

# define the HTML renderer for math block
def render_html_mathblock(mathexpression):
    return (f'<div class="mathexpr">{mathexpression}</div>')

# define the AST renderer for math blocks
def render_ast_mathblock(mathexpression):
    return({
        'type': 'mathblock', 
        'expression': mathexpression,
    })


# define the HTML renderer for math spans
def render_html_mathspan(mathexpression):
    return (f'<span class="mathexpr">{mathexpression}</span>')

# define the AST renderer for math spans
def render_ast_mathspan(mathexpression):
    return ({'expression': mathexpression, 'type': 'mathspan'})


def plugin_allmath(md):
    """ This simply runs both the mathblock and the mathspan plugins """
    plugin_mathblock(md)
    plugin_mathspan(md)

def plugin_mathblock(md):
    """ This processes $$...$$, which creates a separate block/paragraph for the math equation. Based on several existing renderers, this should support math blocks that begin on a new line as well as blocks that begin in the middle of other text. In cases in which it is in other text, it should still be rendered as a separate block/paragraph. It should also process formulas that cross multiple lines of successive text; no renderer tested processed multiline math blocks that contained entirely blank lines. """
    
    if ALLOW_SPACE_PADDING:
        # $${math expression}$$ or $$ {math expression} $$ 
        # - these seem to work
        math_pattern = r'(\s*)\$\$\s?(?!\s)([^\$\n]([^\$\n]|(?<!\n)\n(?!\n))*)(?<!\s)\s?\$\$'
        inline_mathblock = re.compile(math_pattern) 

        mathblock_re = re.compile(math_pattern + r'(.*?)', re.DOTALL) 
    else:
        raise Exception("Not tested yet")
        mathblock_pattern = re.compile(r'([^\n]*)\$\$([^\$\s][^\$]*?)(?<!\s)\$\$([^\n]*)') 

    #
    # define how to parse matched item
    #
    def parse_mathblock(parser, rematch, state):
        """ This takes in the match from the registered pattern and returns a data structure. The data structure must have a 'type' field and then one of several others: 'text' will be re-evaluated by the parser, 'raw' is passed on to the renderer as is, and children will each be individually processed. Note that the 'type' field is the type of rendered to use, not the final type.  """
        # so here the rematch is the result of the pattern.
        # we return the top-level blocks, which depend a bit on the result
        #prolog = rematch.group(1).strip()
        #mathexpr = rematch.group(2).strip()
        #epilog = rematch.group(4).strip()
        groups = rematch.groups()
        mathexpr = groups[1]

        if isinstance(parser, inline_parser.InlineParser):
            # inline parsers are expected to return a tuple of the render function name and the matched parameters.  
            return(('mathblock_renderer', mathexpr))


        prolog = groups[0].strip()
        epilog = groups[-1].strip()

        #import pdb ; pdb.set_trace()

        #
        # In contrast, block parsers are expected to have a dict with at least a type value. It will fail if it does not have another key as well. In this case, we use 'raw' because then it passes the math expression directly to the renderer

        mathblock = {
            'type': 'mathblock_renderer', 
            'raw': mathexpr,
        }
        if not prolog and not epilog:
            # a standalone mathblock.  Just return
            return(mathblock)

        # here the math block is inline in the raw markdown text.
        # So we return a pargaraph with the mathblock in the middle and the rest of the text sent along for additional parsing.
        children = []
        if prolog:
            children.append({
                'type': 'text', 
                'text': prolog,
            })
        
        children.append(mathblock)
        #import pdb ; pdb.set_trace()
        if epilog:
            children.append({
                'type': 'text', 
                'text': epilog,
            })

        return({
            'type': 'paragraph',    
            'children': children,
        })

    # register the rule with the parser
    md.block.register_rule(
        'mathblock_parser', 
        #mathblock_pattern, 
        mathblock_re, 
        parse_mathblock,
    )
    # add the rule to the list of rules
    md.block.rules.append('mathblock_parser')

    # register the rule with the parser
    md.inline.register_rule(
        'mathspan_parser', 
        math_pattern,
        parse_mathblock,
    )
    # add the rule to the list of rules
    md.inline.rules.append('mathspan_parser')

    # register the renderers
    if md.renderer.NAME == 'html':
        md.renderer.register('mathblock_renderer', render_html_mathblock)

    elif md.renderer.NAME == 'ast':
        md.renderer.register('mathblock_renderer', render_ast_mathblock)
    else:
        raise Exception(f"Unknown renderer {md.renderer.NAME}")


def plugin_mathspan(md):
    """ This processes $...$, which creates an inline span for the math equation. It should also process formulas that cross multiple lines of successive text; no renderer tested processed multiline math blocks that contained entirely blank lines. """

    #
    # Define the regex
    #
    if not MATHSPAN_DOUBLE_TOKEN:
        mathspan_re = r'(?<!\$)\$([^\$\s][^\$]*?)(?<!\s)\$'
    elif ALLOW_SPACE_PADDING:
        mathspan_re = r'(?<!\$)\$\$\s*([^\$\s][^\$]*?)\s*\$\$'
    else:
        mathspan_re = r'(?<!\$)\$\$([^\$\s][^\$]*?)(?<!\s)\$\$'
    
    #
    # define how to parse matched item
    #
    def parse_mathspan(parser, rematch, state):
        # ``inline`` is ``md.inline``, see below
        # ``m`` is matched regex item
        mathexpr = rematch.group(1)
        return(('mathspan_renderer',  mathexpr))

    # register the rule with the parser
    md.inline.register_rule(
        'mathspan_parser', 
        mathspan_re, 
        parse_mathspan,
    )

    # add the rule to the list of rules
    md.inline.rules.append('mathspan_parser')


    # register the renderers
    if md.renderer.NAME == 'html':
        md.renderer.register('mathspan_renderer', render_html_mathspan)
    elif md.renderer.NAME == 'ast':
        md.renderer.register('mathspan_renderer', render_ast_mathspan)
    else:
        raise Exception(f"Unknown renderer {md.renderer.NAME}")
