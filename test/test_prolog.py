#

from io import StringIO

import pytest
from docmanager.xmlutil import root_sourceline


doctypeslist = [# doctype,columnstart,startline,span
  # 0
  ("\n<!DOCTYPE book>\n<book/>", 0, 3, (0, 7),
  ),
  # 1
  ("\n<!DOCTYPE  \tbook\n\n>\n\n<book\n/>", 0, 6, (1,9),
  ),
  # 2
  ("""\n<!DOCTYPE book SYSTEM "book.dtd"><book/>""", 33, 2, (33, 40),
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
/>""", 0, 6, (88,268),
  ),

  ## 4
  ("""<!DOCTYPE d:book
[]>
<d:book id="x"
        xmlns:d="urn:x-example:ns"
>
</d:book>
""",
    0, 3, (21, 72),
  ),
]

@pytest.mark.parametrize("doctype,columnstart,startline,span",
                         doctypeslist,
                         ids=['normal', 'with_cr',
                              'with_systemid', 'complete',
                              'with_ns']
                        )
def test_doctype_rootline(doctype, columnstart, startline, span):
    """Checks if parsing of prolog works
    """

    source = StringIO(doctype)
    result =  root_sourceline(source)

    assert columnstart == result.get('columnstart', -1)
    assert startline == result.get('startline', -1)
    assert span == result.get('span', (-1, -1))
