import argparse
import os
import sys
import re
from datetime import datetime
import yaml
import glob
import shutil
from jinja2 import Markup, FileSystemLoader
from jinja2.environment import Environment

parser = argparse.ArgumentParser(description='Builds the final, static site.')
parser.add_argument('-i', '--input', metavar='DIR', dest='input_dir',
                    help='top directory of posts', default='posts')
parser.add_argument('-o', '--output', metavar='DIR', dest='output_dir',
                    help='output directory', default='_build')
parser.add_argument('-e', '--ext', metavar='STR', dest='fn_exts', nargs='+',
                    help='additional file extensions to consider', default=[])
parser.add_argument('-r', '--root', metavar='URL', dest='root_url',
                   help='root URL; default: /', default='/')

args = parser.parse_args()
md_exts = set(args.fn_exts + ['md', 'markdown'])

md_fns = []
for root, dns, fns in os.walk(args.input_dir):
    for fn in fns:
        _, fn_ext = os.path.splitext(fn)
        if fn_ext.lstrip('.') in md_exts:
            md_fns.append(os.path.join(root, fn))

meta_re = re.compile(r'---\s+(.+?)\n---', re.DOTALL)

def extract_metadata(fn):
    meta_data = {}
    with open(fn) as f:
        fn_cont = f.read()
    m = meta_re.match(fn_cont)
    if m:
        meta_data = yaml.load(m.group(1))
    return meta_data

posts = []

# TODO need to update properly
if os.path.exists(os.path.join(args.output_dir, 'static')):
    shutil.rmtree(os.path.join(args.output_dir, 'static'))

shutil.copytree('static', os.path.join(args.output_dir, 'static'))

date_fmt = '%Y-%m-%d %H:%M'
for md_fn in md_fns:
    md_meta = extract_metadata(md_fn)
    if not md_meta:
        continue
    d = datetime.strptime(md_meta['post_date'], date_fmt)
    dest_dir = os.path.join(d.strftime('%Y'),
                            d.strftime('%m'),
                            d.strftime('%d'),
                            md_meta['post_slug'])

    posts.append({'file': md_fn,
                  'dest_dir': dest_dir,
                  'meta': md_meta})

posts.sort(key=lambda x: x['meta']['post_date'], reverse=True)

env = Environment()
env.loader = FileSystemLoader('templates')
index_template = env.get_template('index.html')
#index_template = Template(f.read())

with open(os.path.join(args.output_dir, 'index.html'), 'w') as f:
    print(index_template.render(title='Blog',
                                root_url=args.root_url,
                                posts=posts,
                                style=Markup(r'<link rel="stylesheet" href="{}/static/style.css" />'.format('' if args.root_url == '/' else args.root_url))),
          file=f)

for p in posts:
    html_fn = os.path.join(args.output_dir, p['dest_dir'], 'index.html')

    #if os.path.exists(html_fn):
    #    html_mtime = os.path.getmtime(html_fn)
    #    md_mtime = os.path.getmtime(p['file'])
    #    if html_mtime > md_mtime:
    #        print('{} newer than {} -- nothing to do.'.format(html_fn, p['file']),
    #              file=sys.stderr)
    #        continue
    #    else:
    #        print('{} older than {} -- recompiling.'.format(html_fn, p['file']),
    #              file=sys.stderr)
    #else:
    #    print('{} does not exist -- 1st compile.'.format(html_fn),
    #          file=sys.stderr)
    #    os.makedirs(os.path.dirname(html_fn))

    if not os.path.exists(html_fn):
        os.makedirs(os.path.dirname(html_fn))

    cmd = r'pandoc --standalone --to=html --mathjax ' \
           + '--bibliography=citations.bib {} '.format(p['file']) \
           + '| python scripts/convert_pandoc.py "{}" "{}" > {}'.format(p['meta']['post_title'], args.root_url, html_fn)

    print(cmd)
    os.system(cmd)

    # check if additional files need to be copied
    source_dir = os.path.dirname(p['file'])
    add_fns = set(glob.glob('{}/*'.format(source_dir))) - set([p['file']])
    for add_fn in add_fns: 
        print('copying {} to {}'.format(add_fn, os.path.dirname(html_fn)))
        shutil.copy(add_fn, os.path.dirname(html_fn))
