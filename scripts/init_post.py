import sys
import time

usage = 'Usage: {} <name.md>'.format(sys.argv[0])

if len(sys.argv) != 2:
    print(usage, file=sys.stderr)
    sys.exit(2)

date_fmt = '%Y-%m-%d %H:%M'

template = r"""---
post_title:     <FIXME>
post_author:    Markus Hsi-Yang Fritz
post_date:      {date}
post_tags:      [<FIXME>]
post_slug:      <FIXME>
post_summary:   <FIXME>
is_public:      true
---

Post Title
==========

off you go...
"""

with open(sys.argv[1], 'w') as f:
    print(template.format(date=time.strftime(date_fmt)), file=f)
