<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/_static/logo-white.svg" />
  <img alt="Mistune v3" src="docs/_static/logo-black.svg" height="68" />
</picture>

A fast yet powerful Python Markdown parser with renderers and plugins.

[![Build Status](https://github.com/lepture/mistune/actions/workflows/tests.yml/badge.svg)](https://github.com/lepture/mistune/actions)
[![PyPI version](https://img.shields.io/pypi/v/mistune.svg)](https://pypi.org/project/mistune)
[![conda-forge version](https://img.shields.io/conda/v/conda-forge/mistune.svg?label=conda-forge&colorB=0090ff)](https://anaconda.org/conda-forge/mistune)
[![PyPI Downloads](https://static.pepy.tech/badge/mistune/month)](https://pepy.tech/projects/mistune)
[![Code Coverage](https://codecov.io/gh/lepture/mistune/branch/main/graph/badge.svg?token=mcpitD54Tx)](https://codecov.io/gh/lepture/mistune)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=lepture_mistune&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=lepture_mistune)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=lepture_mistune&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=lepture_mistune)

</div>

## Paid plugins

You can ask me to create a custom mistune plugin or directive for your needs with GitHub sponsor
[one time tier (Mistune enhance)](https://github.com/sponsors/lepture/sponsorships?tier_id=220664)

## Sponsors

<table>
<tr>
<td><img align="middle" width="64" src="https://typlog.com/android-chrome-512x512.png"></td>
<td>Mistune is sponsored by Typlog, a blogging and podcast hosting platform, simple yet powerful. <a href="https://typlog.com/?utm_source=mistune&utm_medium=referral&utm_campaign=readme">Write in Markdown</a>.
</td>
</tr>
</table>

[**Support Me via GitHub Sponsors**](https://github.com/sponsors/lepture).

## Install

To install mistune:

```
$ pip install mistune
```

## Overview

Convert Markdown to HTML with ease:

```python
import mistune

mistune.html(your_markdown_text)
```

## Security Reporting

If you found security bugs, please do not send a public issue or patch.
You can send me email at <me@lepture.com>. Attachment with patch is welcome.
My PGP Key fingerprint is:

```
72F8 E895 A70C EBDF 4F2A DFE0 7E55 E3E0 118B 2B4C
```

Or, you can use the [Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

## Benchmarks

<details>
<summary>
Here is the benchmark score on my computer. Check the `benchmark/bench.py` script.
</summary>  

```
mistune (3.0.0) - atx: 13.901472091674805ms
mistune (slow) - atx: 13.122797012329102ms
mistune (fast) - atx: 13.248443603515625ms
mistune (full) - atx: 15.445232391357422ms
markdown (3.3.7) - atx: 48.41303825378418ms
markdown2 (2.4.3) - atx: 379.30870056152344ms
mistletoe (0.8.2) - atx: 25.46215057373047ms
markdown_it (2.1.0) - atx: 42.37723350524902ms
mistune (3.0.0) - setext: 8.43048095703125ms
mistune (slow) - setext: 8.97979736328125ms
mistune (fast) - setext: 8.122920989990234ms
mistune (full) - setext: 9.525299072265625ms
markdown (3.3.7) - setext: 30.74812889099121ms
markdown2 (2.4.3) - setext: 218.90878677368164ms
mistletoe (0.8.2) - setext: 20.46680450439453ms
markdown_it (2.1.0) - setext: 27.010202407836914ms
mistune (3.0.0) - normal_ul: 60.910940170288086ms
mistune (slow) - normal_ul: 59.69667434692383ms
mistune (fast) - normal_ul: 60.41216850280762ms
mistune (full) - normal_ul: 62.89219856262207ms
markdown (3.3.7) - normal_ul: 83.7857723236084ms
markdown2 (2.4.3) - normal_ul: 175.36139488220215ms
mistletoe (0.8.2) - normal_ul: 74.82385635375977ms
markdown_it (2.1.0) - normal_ul: 103.0113697052002ms
mistune (3.0.0) - insane_ul: 104.1865348815918ms
mistune (slow) - insane_ul: 105.83090782165527ms
mistune (fast) - insane_ul: 103.03664207458496ms
mistune (full) - insane_ul: 105.80086708068848ms
markdown (3.3.7) - insane_ul: 133.82673263549805ms
markdown2 (2.4.3) - insane_ul: 337.23902702331543ms
mistletoe (0.8.2) - insane_ul: 122.10249900817871ms
markdown_it (2.1.0) - insane_ul: 85.92629432678223ms
mistune (3.0.0) - normal_ol: 25.092601776123047ms
mistune (slow) - normal_ol: 25.321483612060547ms
mistune (fast) - normal_ol: 25.11453628540039ms
mistune (full) - normal_ol: 25.945663452148438ms
markdown (3.3.7) - normal_ol: 43.30158233642578ms
markdown2 (2.4.3) - normal_ol: 75.87885856628418ms
mistletoe (0.8.2) - normal_ol: 33.63537788391113ms
markdown_it (2.1.0) - normal_ol: 40.307044982910156ms
mistune (3.0.0) - insane_ol: 46.201229095458984ms
mistune (slow) - insane_ol: 49.14569854736328ms
mistune (fast) - insane_ol: 45.96853256225586ms
mistune (full) - insane_ol: 47.544002532958984ms
markdown (3.3.7) - insane_ol: 50.154924392700195ms
markdown2 (2.4.3) - insane_ol: 210.48712730407715ms
mistletoe (0.8.2) - insane_ol: 84.07974243164062ms
markdown_it (2.1.0) - insane_ol: 83.61554145812988ms
mistune (3.0.0) - blockquote: 15.484809875488281ms
mistune (slow) - blockquote: 16.12544059753418ms
mistune (fast) - blockquote: 15.350818634033203ms
mistune (full) - blockquote: 16.104936599731445ms
markdown (3.3.7) - blockquote: 63.04144859313965ms
markdown2 (2.4.3) - blockquote: 702.4445533752441ms
mistletoe (0.8.2) - blockquote: 28.56159210205078ms
markdown_it (2.1.0) - blockquote: 37.35041618347168ms
mistune (3.0.0) - blockhtml: 7.898569107055664ms
mistune (slow) - blockhtml: 7.080316543579102ms
mistune (fast) - blockhtml: 7.414340972900391ms
mistune (full) - blockhtml: 8.559703826904297ms
markdown (3.3.7) - blockhtml: 46.65660858154297ms
markdown2 (2.4.3) - blockhtml: 122.09773063659668ms
mistletoe (0.8.2) - blockhtml: 12.23611831665039ms
markdown_it (2.1.0) - blockhtml: 26.836156845092773ms
mistune (3.0.0) - fenced: 4.281282424926758ms
mistune (slow) - fenced: 4.092931747436523ms
mistune (fast) - fenced: 4.024267196655273ms
mistune (full) - fenced: 4.453897476196289ms
markdown (3.3.7) - fenced: 33.83779525756836ms
markdown2 (2.4.3) - fenced: 92.49091148376465ms
mistletoe (0.8.2) - fenced: 9.19342041015625ms
markdown_it (2.1.0) - fenced: 12.503623962402344ms
mistune (3.0.0) - paragraph: 95.94106674194336ms
mistune (slow) - paragraph: 561.2788200378418ms
mistune (fast) - paragraph: 93.597412109375ms
mistune (full) - paragraph: 110.09836196899414ms
markdown (3.3.7) - paragraph: 304.1346073150635ms
markdown2 (2.4.3) - paragraph: 267.84825325012207ms
mistletoe (0.8.2) - paragraph: 779.3235778808594ms
markdown_it (2.1.0) - paragraph: 825.5178928375244ms
mistune (3.0.0) - emphasis: 23.591041564941406ms
mistune (slow) - emphasis: 16.934871673583984ms
mistune (fast) - emphasis: 23.232460021972656ms
mistune (full) - emphasis: 25.2840518951416ms
markdown (3.3.7) - emphasis: 76.50399208068848ms
markdown2 (2.4.3) - emphasis: 9.393930435180664ms
mistletoe (0.8.2) - emphasis: 33.68663787841797ms
markdown_it (2.1.0) - emphasis: 60.90521812438965ms
mistune (3.0.0) - auto_links: 3.7980079650878906ms
mistune (slow) - auto_links: 3.3910274505615234ms
mistune (fast) - auto_links: 3.6630630493164062ms
mistune (full) - auto_links: 3.9186477661132812ms
markdown (3.3.7) - auto_links: 23.04673194885254ms
markdown2 (2.4.3) - auto_links: 6.537914276123047ms
mistletoe (0.8.2) - auto_links: 8.360624313354492ms
markdown_it (2.1.0) - auto_links: 19.732236862182617ms
mistune (3.0.0) - std_links: 21.920442581176758ms
mistune (slow) - std_links: 17.487764358520508ms
mistune (fast) - std_links: 19.87743377685547ms
mistune (full) - std_links: 24.514198303222656ms
markdown (3.3.7) - std_links: 39.1237735748291ms
markdown2 (2.4.3) - std_links: 14.519691467285156ms
mistletoe (0.8.2) - std_links: 22.84979820251465ms
markdown_it (2.1.0) - std_links: 32.60660171508789ms
mistune (3.0.0) - ref_links: 47.673940658569336ms
mistune (slow) - ref_links: 39.449214935302734ms
mistune (fast) - ref_links: 44.81911659240723ms
mistune (full) - ref_links: 52.37579345703125ms
markdown (3.3.7) - ref_links: 87.65625953674316ms
markdown2 (2.4.3) - ref_links: 23.118972778320312ms
mistletoe (0.8.2) - ref_links: 59.136390686035156ms
markdown_it (2.1.0) - ref_links: 80.44648170471191ms
mistune (3.0.0) - readme: 56.607723236083984ms
mistune (slow) - readme: 68.8173770904541ms
mistune (fast) - readme: 53.86018753051758ms
mistune (full) - readme: 61.25998497009277ms
markdown (3.3.7) - readme: 211.02523803710938ms
markdown2 (2.4.3) - readme: 533.4112644195557ms
mistletoe (0.8.2) - readme: 110.12959480285645ms
markdown_it (2.1.0) - readme: 247.9879856109619ms
```

</details>

All results are in milliseconds (ms).

| / Parser ➡ Case ⬇       | mistune (3.0.0) | mistune (slow) | mistune (fast) | mistune (full) | markdown (3.3.7) | markdown2 (2.4.3) | mistletoe (0.8.2) | markdown_it (2.1.0) |
| -------------- | --------------: | -------------: | -------------: | -------------: | ---------------: | ----------------: | ----------------: | ------------------: |
| **atx**        |           13.90 |      <mark>13.12</mark> |          13.25 |          15.45 |            48.41 |            379.31 |             25.46 |               42.38 |
| **setext**     |            8.43 |           8.98 |       <mark>8.12</mark> |           9.53 |            30.75 |            218.91 |             20.47 |               27.01 |
| **normal_ul**  |           60.91 |      <mark>59.70</mark> |          60.41 |          62.89 |            83.79 |            175.36 |             74.82 |              103.01 |
| **insane_ul**  |          104.19 |         105.83 |         103.04 |         105.80 |           133.83 |            337.24 |            122.10 |           <mark>85.93</mark> |
| **normal_ol**  |       <mark>25.10</mark> |          25.32 |          25.11 |          25.95 |            43.30 |             75.88 |             33.64 |               40.31 |
| **insane_ol**  |           46.20 |          49.15 |      <mark>45.97</mark> |          47.54 |            50.15 |            210.49 |             84.08 |               83.62 |
| **blockquote** |           15.48 |          16.13 |      <mark>15.35</mark> |          16.10 |            63.04 |            702.44 |             28.56 |               37.35 |
| **blockhtml**  |            7.90 |       <mark>7.08</mark> |           7.41 |           8.56 |            46.66 |            122.10 |             12.24 |               26.84 |
| **fenced**     |            4.28 |           4.09 |       <mark>4.02</mark> |           4.45 |            33.84 |             92.49 |              9.19 |               12.50 |
| **paragraph**  |           95.94 |         561.28 |      <mark>93.60</mark> |         110.10 |           304.13 |            267.85 |            779.32 |              825.52 |
| **emphasis**   |           23.59 |          16.93 |          23.23 |          25.28 |            76.50 |          <mark>9.39</mark> |             33.69 |               60.91 |
| **auto_links** |            3.80 |       <mark>3.39</mark> |           3.66 |           3.92 |            23.05 |              6.54 |              8.36 |               19.73 |
| **std_links**  |           21.92 |          17.49 |          19.88 |          24.51 |            39.12 |         <mark>14.52</mark> |             22.85 |               32.61 |
| **ref_links**  |           47.67 |          39.45 |          44.82 |          52.38 |            87.66 |         <mark>23.12</mark> |             59.14 |               80.45 |
| **readme**     |           56.61 |          68.82 |      <mark>53.86</mark> |          61.26 |           211.03 |            533.41 |            110.13 |              247.99 |

## License

Mistune is licensed under BSD. Please see LICENSE for licensing details.
