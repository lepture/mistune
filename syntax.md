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
into consideration at the rewritting, there are test cases for CommonMark
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
line link definition, it looks like:

```
[foo]: /url
"title"

[foo]
```

### Why MFM

This Mistune Flavored Markdown is not a specification. It is not created to
enforce other developers to follow these rules. Instead, it is a clarification
on how will Mistune render your text.

This file contains only the very basic Markdown syntax. Mistune has serval
plugins to extend Markdown grammers, there documentation will be located in
docs folder.


## Blocks


### Thematic breaks

```````````````````````````````` example
***
---
___
.
<hr />
<hr />
<hr />
````````````````````````````````

```````````````````````````````` example
+++
.
<p>+++</p>
````````````````````````````````

```````````````````````````````` example
--
**
__
.
<p>--
**
__</p>
````````````````````````````````

```````````````````````````````` example
 ***
  ***
   ***

.
<hr />
<hr />
<hr />
````````````````````````````````

```````````````````````````````` example
    ***
.
<pre><code>***
</code></pre>
````````````````````````````````

```````````````````````````````` example
Foo
    ***
.
<p>Foo
    ***</p>
````````````````````````````````

```````````````````````````````` example
_____________________________________
.
<hr />
````````````````````````````````

```````````````````````````````` example
 - - -
.
<hr />
````````````````````````````````

```````````````````````````````` example
 **  * ** * ** * **
.
<hr />
````````````````````````````````

```````````````````````````````` example
-     -      -      -
.
<hr />
````````````````````````````````

```````````````````````````````` example
- - - -    
.
<hr />
````````````````````````````````

### Setext headings



```````````````````````````````` example
Foo
Bar
---
.
<p>Foo
Bar</p>
<hr />
````````````````````````````````

## Containers

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

Harmful link protection:

```````````````````````````````` example
<javascript:alert(0)>
.
<p><a href="#harmful-link">javascript:alert(0)</a></p>
````````````````````````````````
