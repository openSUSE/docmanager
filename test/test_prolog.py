#

import pytest
import re
from docmanager.xmlutil import findprolog
from io import StringIO

IDS =['normal', 'with_cr',
      'with_systemid', 'complete', 'with_ns',
      'without_linebreak', 'without_linebreak_2', 'everything_in_one_line',
      'with_comment', 'with_pi',
     ]

doctypeslist = [# xml,expected
  # 0
  ("\n<!DOCTYPE book>\n<book/>",
    {'root': '<book/>',
     'offset': 17,
     'header': '\n<!DOCTYPE book>\n'}
  ),
  # 1
  ("\n<!DOCTYPE  \tbook\n\n>\n\n<book\n/>",
    {'root': '<book\n/>',
     'offset': 22,
     'header': '\n<!DOCTYPE  \tbook\n\n>\n\n'}
  ),
  # 2
  ("""\n<!DOCTYPE book SYSTEM "book.dtd"><book/>""",
    {'root': '<book/>',
     'offset': 34,
     'header': '\n<!DOCTYPE book SYSTEM "book.dtd">'}
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
    {'root': '<article version="5.0" xml:lang="en"\n        xmlns:dm="urn:x-suse:ns:docmanager"\n        xmlns="http://docbook.org/ns/docbook"\n        xmlns:xlink="http://www.w3.org/1999/xlink"\n/>',
     'offset': 89,
     'header': '<!DOCTYPE article [\n  <!ENTITY % entity.ent SYSTEM "entity-decl.ent">\n  %entity.ent;\n]>\n\n'}
  ),
  ## 4
  ("""<!DOCTYPE d:book
[]>
<d:book id="x:q"
        xmlns:d="urn:x-example:ns"
>
</d:book>
""",
    {'root': '<d:book id="x:q"\n        xmlns:d="urn:x-example:ns"\n>\n',
     'offset': 21,
     'header': '<!DOCTYPE d:book\n[]>\n'}
  ),
  ## 5
  ("""<!DOCTYPE book
[]><book id="bla">
</book>""", {'header': '<!DOCTYPE book\n[]>',
             'offset': 18,
             'root': '<book id="bla">\n'}),
  ## 6
  ("""<!DOCTYPE article [
]>

<article id="bla">
</article>""", {'header': '<!DOCTYPE article [\n]>\n\n',
                'offset': 24,
                'root': '<article id="bla">\n'}),
  ## 7
  ("""<!DOCTYPE article []><article/>""",
   {'header': '<!DOCTYPE article []>',
    'offset': 21,
    'root': '<article/>'}),
  ## 8
  ("""<!DOCTYPE article []>\n<article id="a">\n<!-- bla -->\n  <title/></article>""",
    {'header': '<!DOCTYPE article []>\n',
     'offset': 22,
     'root':   '<article id="a">\n'
    }
  ),
  ## 9
  ("""<!DOCTYPE article []>\n<article id="a">\n<?dbfoo abc?>\n  <title/></article>""",
    {'header': '<!DOCTYPE article []>\n',
     'offset': 22,
     'root':   '<article id="a">\n'
    }
  ),
]

@pytest.mark.parametrize("xml,expected",
                         doctypeslist,
                         ids=IDS
                        )
def test_prolog_with_stringio(xml, expected):
    """Checks if parsing of prolog works with StringIO
    """
    source = StringIO(xml)
    result = findprolog(source)
    assert result == expected


@pytest.mark.parametrize("xml,expected",
                         doctypeslist,
                         ids=IDS
                        )
def test_prolog_with_string(xml, expected):
    """Checks if parsing of prolog works with normal strings
    """
    result = findprolog(xml)
    assert result == expected


@pytest.mark.parametrize("xml,expected",
                         doctypeslist,
                         ids=IDS
                        )
def test_prolog_with_filename(xml, expected, tmpdir):
    tmp = tmpdir.join("test.xml").strpath
    fh = open(tmp, 'w')
    fh.write(xml)
    fh.close()
    
    result = findprolog(tmp)
    assert result == expected

