#

from io import StringIO

import pytest
from docmanager.xmlutil import root_sourceline


doctypeslist = [# xml,expected
  # 0
  ("\n<!DOCTYPE book>\n<book/>",
    {'root': '<book/>', 'offset': 17, 'header': '\n<!DOCTYPE book>\n'}
  ),
  # 1
  ("\n<!DOCTYPE  \tbook\n\n>\n\n<book\n/>",
    {'root': '<!DOCTYPE  \tbook\n\n>\n\n<book\n/>', 'offset': 1, 'header': '\n'}
  ),
  # 2
  ("""\n<!DOCTYPE book SYSTEM "book.dtd"><book/>""",
    {'root': '<book/>', 'offset': 34, 'header': '\n<!DOCTYPE book SYSTEM "book.dtd">'}
  ),
  ## 3
  ("""<!DOCTYPE article [
  <!ENTITY % entity.ent SYSTEM "entity-decl.ent">
  %entity.ent;
]>

<article version="5.0" xml:lang="en"
        xmlns:dm="urn:x-suse:ns:docmanager"
        xmlns="http://docbook.org/ns/docbook"
        xmlns:xlink="http://www.w3.org/1999/xlink"
/>""",
    {'root': '\n<article version="5.0" xml:lang="en"\n        xmlns:dm="urn:x-suse:ns:docmanager"\n        xmlns="http://docbook.org/ns/docbook"\n        xmlns:xlink="http://www.w3.org/1999/xlink"\n/>',
     'offset': 88,
     'header': '<!DOCTYPE article [\n  <!ENTITY % entity.ent SYSTEM "entity-decl.ent">\n  %entity.ent;\n]>\n'}
  ),
  ## 4
  ("""<!DOCTYPE d:book
[]>
<d:book id="x"
        xmlns:d="urn:x-example:ns"
>
</d:book>
""",
    {'root': '<d:book id="x"\n        xmlns:d="urn:x-example:ns"\n>\n',
     'offset': 21,
     'header': '<!DOCTYPE d:book\n[]>\n'}
  ),
]

@pytest.mark.parametrize("xml,expected",
                         doctypeslist,
                         ids=['normal', 'with_cr',
                              'with_systemid', 'complete',
                              'with_ns']
                        )
def test_doctype_rootline(xml, expected):
    """Checks if parsing of prolog works
    """

    source = StringIO(xml)
    result =  root_sourceline(source)

    assert result == expected
