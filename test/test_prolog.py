#

import pytest
import re
from docmanager.xmlutil import findprolog
from io import StringIO

IDS =['normal', 'with_cr',
      'with_systemid', 'complete', 'with_ns',
      'without_linebreak', 'without_linebreak_2', 'everything_in_one_line',
      'with_comment', 'with_pi', 'with_pi_before_dt', 'with_comment_before_dt',
     ]

doctypeslist = [# xml,expected
  # 0
  ("\n<!DOCTYPE book>\n<book/>",
    {'root': '<book/>',
     'offset': 17,
     'header': '\n<!DOCTYPE book>\n',
     'roottag': 'book'
    }
  ),
  # 1
  ("\n<!DOCTYPE  \tbook\n\n>\n\n<book\n/>",
    {'root': '<book\n/>',
     'offset': 22,
     'header': '\n<!DOCTYPE  \tbook\n\n>\n\n',
     'roottag': 'book'}
  ),
  # 2
  ("""\n<!DOCTYPE book SYSTEM "book.dtd"><book/>""",
    {'root': '<book/>',
     'offset': 34,
     'header': '\n<!DOCTYPE book SYSTEM "book.dtd">',
     'roottag': 'book'}
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
     'header': '<!DOCTYPE article [\n  <!ENTITY % entity.ent SYSTEM "entity-decl.ent">\n  %entity.ent;\n]>\n\n',
     'roottag': 'article'}
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
     'header': '<!DOCTYPE d:book\n[]>\n',
     'roottag': 'd:book'}
  ),
  ## 5
  ("""<!DOCTYPE book
[]><book id="bla">
</book>""",
    {'header': '<!DOCTYPE book\n[]>',
     'offset': 18,
     'root': '<book id="bla">\n',
     'roottag': 'book'}),
  ## 6
  ("""<!DOCTYPE article [
]>

<article id="bla">
</article>""",
    {'header': '<!DOCTYPE article [\n]>\n\n',
     'offset': 24,
     'root': '<article id="bla">\n',
     'roottag': 'article'}),
  ## 7
  ("""<!DOCTYPE article []><article/>""",
   {'header': '<!DOCTYPE article []>',
    'offset': 21,
    'root': '<article/>',
     'roottag': 'article'}),
  ## 8
  ("""<!DOCTYPE article []>\n<article id="a">\n<!-- bla -->\n  <title/></article>""",
    {'header': '<!DOCTYPE article []>\n',
     'offset': 22,
     'root':   '<article id="a">\n',
     'roottag': 'article'
    }
  ),
  ## 9
  ("""<!DOCTYPE article []>\n<article id="a">\n<?dbfoo abc?>\n  <title/></article>""",
    {'header': '<!DOCTYPE article []>\n',
     'offset': 22,
     'root':   '<article id="a">\n',
     'roottag': 'article'
    }
  ),
  ## 10
  ("""<?xml-stylesheet href="x"?>
<!DOCTYPE book PUBLIC "-//Novell//DTD NovDoc XML V1.0//EN" "novdocx.dtd"
[
]>

<book id="os-user-guide" lang="en">
  <bookinfo/>
</book>""",
   {'header':   '<?xml-stylesheet href="x"?>\n<!DOCTYPE book PUBLIC "-//Novell//DTD NovDoc XML V1.0//EN" "novdocx.dtd"\n[\n]>\n\n',
     'offset':  107,
     'root':    '<book id="os-user-guide" lang="en">\n',
     'roottag': 'book'
    }
  ),
  ## 11
  ("""<?xml version="1.0"?>
<!-- bla -->
<!DOCTYPE book []>
<!-- blabla -->

<book id="foo">
  <title/>
</book>
""",
   {'header':  '<?xml version="1.0"?>\n<!-- bla -->\n<!DOCTYPE book []>\n<!-- blabla -->\n\n',
    'offset':  71,
    'root':    '<book id="foo">\n',
    'roottag': 'book'
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

