cdef class BlockLexer(object):
    cdef public list tokens
    cdef public dict def_links
    cdef public dict def_footnotes
    cdef public object rules


cdef class InlineLexer(object):
    cdef public object renderer
    cdef public dict links
    cdef public dict footnotes
    cdef public object footnote_index
    cdef public object rules
    cdef bint _in_link, _in_footnote
    cdef bint _parse_inline_html
    cdef object line_match


cdef class Renderer(object):
    cdef public dict options


cdef class Markdown(object):
    cdef public object renderer
    cdef public object inline "Markdown_inline"
    cdef public object block
    cdef public list footnotes
    cdef public list tokens
    cdef public object token
    cdef bint _parse_block_html
