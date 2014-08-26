from jinja2 import Template, Markup
import sys
import re

head_re = re.compile(r'<head>\s+(.+)</head>', re.DOTALL)
style_re = re.compile(r'<style.+?</style>', re.DOTALL)
script_re = re.compile(r'<script.+?</script>', re.DOTALL)
body_re = re.compile(r'<body>\s+(.+)</body>', re.DOTALL)

def process(f, title, root_url):
    with open('templates/common.html') as f_template:
        common_template = Template(f_template.read())

    pandoc_html = f.read()

    m = head_re.search(pandoc_html)
    if not m:
        print('error')
        sys.exit(1)
    pandoc_head = m.group(1)
    pandoc_style = Markup('\n'.join(style_re.findall(pandoc_head)))
    pandoc_script = Markup('\n'.join(script_re.findall(pandoc_head)))

    m = body_re.search(pandoc_html)
    if not m:
        print('error')
        sys.exit(1)
    pandoc_body = Markup(m.group(1))

    return common_template.render(title=title,
                                  root_url=root_url,
                                  content=pandoc_body,
                                  style=pandoc_style + '\n' + Markup(r'<link rel="stylesheet" href="{}/static/style.css" />'.format('' if root_url == '/' else root_url)),
                                  head_script=pandoc_script)

if __name__ == '__main__':
    usage = 'Usage: {} <title> <root_url>'.format(sys.argv[0])
    if len(sys.argv) != 3:
        print(usage, file=sys.stderr)
        sys.exit(2)
    print(process(sys.stdin, sys.argv[1], sys.argv[2]))
