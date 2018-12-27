# Mistune Flavored Markdown

- Version: 2019-01-01
- Author: Hsiaoming Yang

---

## Introduction

Mistune Flavored Markdown (MFM) is a dialect of Markdown that Mistune 2.0
supported. It includes the basic syntax and extension syntax.

### Why Not CommonMark

CommonMark has gained its popularity nowadays. CommonMark has been taken into
consideration when rewriting Mistune 2.0, there is even test cases for
CommonMark in Mistune 2.0, however it is not adopted in Mistune since there
are many weird rules in CommonMark.

CommonMark declares:

> John Gruber's canonical description of Markdown's syntax does not specify
> the syntax unambiguously.

It certainly makes some sense at first glimpse. But diving into the CommonMark
spec, it turns out that many so called unambiguous syntax are not unambiguous
at all. They are not declared clearly, because there are not needed to. No
wonder John Gruber would suggest a name of
[Pedantic Markdown](https://twitter.com/gruber/status/507615356295200770).

> Markdown is a text-to-HTML conversion tool for web writers. Markdown allows
> you to write using an easy-to-read, easy-to-write plain text format, then
> convert it to structurally valid XHTML (or HTML).
>
> -- [John Gruber](https://daringfireball.net/projects/markdown/)

The most important thing in Markdown would be readability. 

### Why MFM

This Mistune Flavored Markdown is not a specification. It is not created to
enforce other developers to follow these rules.
