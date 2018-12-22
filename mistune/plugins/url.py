from mistune.scanner import escape_url


URL_LINK = r'''(https?:\/\/[^\s<]+[^<.,:;"')\]\s])'''


def parse_url_link(self, m, state):
    return 'link', escape_url(m.group(0))


def url(md):
    md.inline.register_rule('url_link', URL_LINK, parse_url_link)
    md.inline.default_rules.append('url_link')
