import re


ABBR_PATTERN = re.compile(r"[*]\[(?P<key>[^\]]*)\][ ]?:[ ]*\n?[ ]*(?P<definition>.*)")


def render_html_abbr(key, definition):
    title_attribute = ""
    if definition:
        title_attribute = ' title="{}"'.format(definition)

    return "<abbr{title_attribute}>{key}</abbr>".format(
        key=key,
        title_attribute=title_attribute,
    )


def plugin_abbr(md):
    def _def_abbr(block, match, state):
        key = match.group("key")
        definition = match.group("definition")

        def _abbr_rule(parser, match, state):
            return "abbr", key, definition

        rule_name = "{key}_abbr".format(key=key)

        md.inline.register_rule(rule_name, key, _abbr_rule)
        md.inline.rules.append(rule_name)

    md.block.register_rule("def_abbr", ABBR_PATTERN, _def_abbr)
    md.block.rules.append("def_abbr")

    if md.renderer.NAME == "html":
        md.renderer.register("abbr", render_html_abbr)
