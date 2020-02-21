# Mistune Flavored Markdown

- Version: 2019-01-01
- Author: Hsiaoming Yang

---

## Introduction

Mistune Flavored Markdown (MFM) is a dialect of Markdown that Mistune 2.0
supported. This document contains the basic Markdown syntax.

### Why Not CommonMark

CommonMark has certainly done something right. But there are so many weird
rules that made it not Markdown anymore. Mistune 2.0 has taken CommonMark
into consideration at the rewriting, there are test cases for CommonMark
in the tests folder. While implementing the CommonMark rules, it turns out
that John Gruber is right, the name of
[Pedantic Markdown](https://twitter.com/gruber/status/507615356295200770)
makes sense.

> Markdown is a text-to-HTML conversion tool for web writers. Markdown allows
> you to write using an easy-to-read, easy-to-write plain text format, then
> convert it to structurally valid XHTML (or HTML).
>
> -- [John Gruber](https://daringfireball.net/projects/markdown/)

The most difference among Markdown and other formatting syntax is
readability, while cases in CommonMark on the other hand are not. Take the
link definition as an example:

```
[foo]: /url '
title
line1
line2
'

[foo]
```

Is it easy-to-read? Absolutely no. There are certainly cases that you need
multiple lines for a link definition, either the link or the title is too
long. The original perl script provided by John Gruber does accept multiple
line link definition, but the title will always stay in one line, it looks
like:

```
[foo]: /url
"title"

[foo]
```

### Why MFM

Mistune Flavored Markdown is not a specification. It is not created to enforce
other developers to follow these rules. Instead, it is a clarification on how
will Mistune render your text.

This documentation is mainly based on CommonMark. But it doesn't contain the
weird rules that Mistune dislikes.

MFM is a guide on how will Mistune render the text in a lot of edge cases.
Writers should read the [Style Guide][] instead, you are not supposed to write
in those edge cases.

[Style Guide]: docs/style-guide.md


## Blocks

### Thematic breaks

A line consisting of 0-3 spaces of indentation, followed by a sequence of
three or more matching `-`,` _`, or `*` characters, each followed optionally
by any number of spaces, forms a thematic break:

```````````````````````````````` example
* * *
***
*****
- - -
---------------------------------------
.
<hr />
<hr />
<hr />
<hr />
<hr />
````````````````````````````````

One to three spaces indent are allowed:

```````````````````````````````` example
 ***
  ***
   ***
.
<hr />
<hr />
<hr />
````````````````````````````````

Four spaces indent produces a code block:

```````````````````````````````` example
    ***
.
<pre><code>***
</code></pre>
````````````````````````````````

Although a thematic break do not need blank lines before or after, it is
still suggested putting blank lines around them.

```````````````````````````````` example
Foo
***
bar
.
<p>Foo</p>
<hr />
<p>bar</p>
````````````````````````````````

Mistune can convert it correctly, but you **SHOULD NOT** write in this syntax,
keeping blank lines around a thematic break is easier to read:

```````````````````````````````` example
Foo

***

bar
.
<p>Foo</p>
<hr />
<p>bar</p>
````````````````````````````````

### AXT headings

[atx]: http://www.aaronsw.com/2002/atx/

AXT headings was created by **Aaron Swartz** in its [atx][] software.
Atx-style headers use 1-6 unescaped `#` at the start of the line and followed
by a space, corresponding to header levels 1-6:

```````````````````````````````` example
# This is an H1
## This is an H2
###### This is an H6
.
<h1>This is an H1</h1>
<h2>This is an H2</h2>
<h6>This is an H6</h6>
````````````````````````````````

Optionally, you may "close" atx-style headers. But it is **NOT SUGGESTED** in
Mistune.

```````````````````````````````` example
# This is an H1 #
## This is an H2 ##
### This is an H3 ######
.
<h1>This is an H1</h1>
<h2>This is an H2</h2>
<h3>This is an H3</h3>
````````````````````````````````

More than six `#` characters is not a heading:

```````````````````````````````` example
####### foo
.
<p>####### foo</p>
````````````````````````````````

At least one space is required between the `#` characters and the heading's
contents, unless the heading is empty:

```````````````````````````````` example
#5 bolt

#hashtag
.
<p>#5 bolt</p>
<p>#hashtag</p>
````````````````````````````````

This is not a heading, because the first # is escaped:

```````````````````````````````` example
\## foo
.
<p>## foo</p>
````````````````````````````````

One to three spaces indentation are allowed, but it is **NOT SUGGESTED**:

```````````````````````````````` example
 ### foo
  ## foo
   # foo
.
<h3>foo</h3>
<h2>foo</h2>
<h1>foo</h1>
````````````````````````````````

Although ATX headings need not be separated from surrounding content by
blank lines, and they can interrupt paragraphs, but it is **NOT SUGGESTED**:

```````````````````````````````` example
Foo bar
# baz
Bar foo
.
<p>Foo bar</p>
<h1>baz</h1>
<p>Bar foo</p>
````````````````````````````````

Instead, you **SHOULD** always keep blank lines around headings like this::

```````````````````````````````` example
Foo bar

# baz

Bar foo
.
<p>Foo bar</p>
<h1>baz</h1>
<p>Bar foo</p>
````````````````````````````````

### Setext headings

Setext-style headings are "underlined" with at least two `=` or `-`
characters:

```````````````````````````````` example
This is an H1
=============

This is an H2
-------------
.
<h1>This is an H1</h1>
<h2>This is an H2</h2>
````````````````````````````````

The original `Markdown.pl` by John Gruber allows any number of the
underline characters. But Mistune requires at least two characters:

```````````````````````````````` example
Foo
=
.
<p>Foo
=</p>
````````````````````````````````

Unlike CommonMark, Mistune only allows one line content for a setext-style
heading:

```````````````````````````````` example
Foo
Bar
---
.
<p>Foo
Bar</p>
<hr />
````````````````````````````````

The result in CommonMark is:

````
<h2>Foo
Bar</h2>
````

The result in `Markdown.pl` is:

````
<p>Foo</p>

<h2>Bar</h2>
````

You **SHOULD** write only one line contents in a setext-style heading,
and keep blank lines around it:

```````````````````````````````` example
Foo

Bar
---
.
<p>Foo</p>
<h2>Bar</h2>
````````````````````````````````

The heading content can be indented up to three spaces, and need not line up
with the underlining, but **DON'T DO THIS**:

```````````````````````````````` example
   Foo
---

  Foo
-----

  Foo
  ===
.
<h2>Foo</h2>
<h2>Foo</h2>
<h1>Foo</h1>
````````````````````````````````

Four spaces indent creates code block:

```````````````````````````````` example
    Foo
    ---

    Foo
---
.
<pre><code>Foo
---

Foo
</code></pre>
<hr />
````````````````````````````````

The setext heading underline cannot contain internal spaces:

```````````````````````````````` example
Foo
= =

Foo
--- -
.
<p>Foo
= =</p>
<p>Foo</p>
<hr />
````````````````````````````````

### Blockquote

Keep only 6 level containers.

```````````````````````````````` example
> > > > > > > 7
.
<blockquote>
<blockquote>
<blockquote>
<blockquote>
<blockquote>
<blockquote>
<p>&gt; 7</p>
</blockquote>
</blockquote>
</blockquote>
</blockquote>
</blockquote>
</blockquote>
````````````````````````````````


### Lists

```````````````````````````````` example
- 1
  - 2
    - 3
      - 4
        - 5
          - 6
            - 7
.
<ul>
<li>1<ul>
<li>2<ul>
<li>3<ul>
<li>4<ul>
<li>5<ul>
<li>6
- 7</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
````````````````````````````````

## Inlines


### Emphasis


### Links

Links can't contain links.

```````````````````````````````` example
[<https://example.com>](/foo)
.
<p><a href="/foo">&lt;https://example.com&gt;</a></p>
````````````````````````````````

```````````````````````````````` example
[[foo]](/foo)

[foo]: https://example.com/
.
<p><a href="/foo">[foo]</a></p>
````````````````````````````````

```````````````````````````````` example
[[foo][]](/foo)

[foo]: https://example.com/
.
<p><a href="/foo">[foo][]</a></p>
````````````````````````````````

Harmful link protection:

```````````````````````````````` example
<javascript:alert(0)>
.
<p><a href="#harmful-link">javascript:alert(0)</a></p>
````````````````````````````````
