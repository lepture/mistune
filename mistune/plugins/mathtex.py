"""
Mistune Math Plugin. See documentation in mathplugn.rst file.

Copyright (c) 2021, Kevin Crouse. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of the creator nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
    
    math_pattern = r'\n*\$\$\s?(?!\s)([^\$\n]([^\$\n]|(?<!\n)\n(?!\n))*)(?<!\s)\s?\$\$\n*'
    mathblock_re = re.compile(r'(.*?)' + math_pattern + r'(.*)\n?')  

    #
    # define how to parse matched item
    #
    def parse_mathblock(parser, rematch, state):
        """ This takes in the match from the registered pattern and returns a data structure. The data structure must have a 'type' field and then one of several others: 'text' will be re-evaluated by the parser, 'raw' is passed on to the renderer as is, and children will each be individually processed. Note that the 'type' field is the type of rendered to use, not the final type.  """
        # so here the rematch is the result of the pattern.
        # we return the top-level blocks, which depend a bit on the result

        groups = rematch.groups()
        if isinstance(parser, inline_parser.InlineParser):
            # inline parsers are expected to return a tuple of the render function name and the matched parameters.  
            return(('mathblock_renderer', groups[0].strip()))
        
        prolog = groups[0].strip()
        mathexpr = groups[1].strip()
        epilog = groups[-1].strip()

        # In contrast, block parsers are expected to have a dict with at least a type value. It will fail if it does not have another key as well. In this case, we use 'raw' because then it passes the math expression directly to the renderer

        mathblock = {
            'type': 'mathblock_renderer', 
            'raw': mathexpr,
        }
        if not prolog and not epilog:
            # a standalone mathblock.  Just return
            return(mathblock)

        # here the math block is inline in the raw markdown text - but there may or may not be preceeding or following text. So we return any text, if it exists, in paragraphs, and the mathblock at an equal level positions accordingly.
        
        children = []
        if prolog:
            children.append({
                'type': 'paragraph', 
                'text': prolog,
            })
        
        children.append(mathblock)

        if epilog:
            children.append({
                'type': 'paragraph', 
                'text': epilog,
            })
        return(children)

    # register the rule with the block parser
    md.block.register_rule(
        'mathblock_parser', 
        mathblock_re, 
        parse_mathblock,
    )
    # add the rule to the list of rules
    md.block.rules.append('mathblock_parser')

    # Not to be confused with the mathspan plugin, we need to 
    # register the $$..$$ mathblock as an inline rule as well, 
    # because it is not uncommon in examples around the web to see it written 
    # inline and rendered as a block, and block-only parsing fails to catch it.
    # 
    # use the 'mathblock_inline_..' notation to distinguish it from the mathspan
    # inline parser in the next plugin.
    # But parse_mathblock() is generalized to take the input from either the 
    # true block or inline block notation.
    md.inline.register_rule(
        'mathblock_inline_parser', 
        math_pattern,
        parse_mathblock,
    )
    # add the inline-block rule to the list of rules
    md.inline.rules.append('mathblock_inline_parser')

    # register the renderers
    if md.renderer.NAME == 'html':
        md.renderer.register('mathblock_renderer', render_html_mathblock)
    elif md.renderer.NAME == 'ast':
        md.renderer.register('mathblock_renderer', render_ast_mathblock)
    else:
        raise Exception(f"Unknown renderer {md.renderer.NAME}")


def plugin_mathspan(md):
    """ This processes $...$, which creates an inline span for the math equation. It should also process formulas that cross multiple lines of successive text; no renderer tested processed multiline math blocks that contained entirely blank lines. """
    # compared to mathblock, this is soo much easier to manage.

    #
    # Define the regex
    #
    mathspan_re = r'(?<!\$)\$([^\$\s][^\$]*?)(?<!\s)\$'
    
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
