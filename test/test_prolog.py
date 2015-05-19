#

from io import StringIO
import pytest
from docmanager.xmlutil import root_sourceline, prolog

from lxml import etree


class TestResolver(etree.Resolver):
     def resolve(self, url, pubid, context):
         print("Resolving URL '%s'" % url)
         #return self.resolve_string(
         #    '<!ENTITY myentity "[resolved text: %s]">' % url, context)
         return self.resolve_empty(context)


doctypeslist = [
  # 0
  ("\n<!DOCTYPE book>\n<book/>", 3, 17
  ),
  # 1
  ("\n<!DOCTYPE  \tbook\n\n>\n\n<book/>", 6, 22
  ),
  # 2
  ("""\n<!DOCTYPE book SYSTEM "book.dtd"><book/>""", 2, 41
  ),
  # 3
  (r"""<!DOCTYPE book SYSTEM "c:\Program\book.dtd"><book/>""", 1, 43
  ),
  # 4
  (r"""<!DOCTYPE book SYSTEM "c:\Program\book.dtd" []><book/>""", 1, 47
  ),
  # 5
  ("""<!DOCTYPE book PUBLIC
     "-//OASIS//DTD DocBook XML V5.0//EN"
     "http://www.docbook.org/xml/5.0/docbookx.dtd">
     <book/>""", 4, 116
  ),
]

@pytest.mark.parametrize("doctype,rootpos,length",
                         doctypeslist,
                         # ids=[]
                        )
def test_doctype_rootline(doctype, rootpos, length, bookdtd):
    """
    """
    #testresolver = TestResolver()
    #source = StringIO(doctype)
    #assert rootpos == root_sourceline(source, testresolver)

    #source.seek(0)
    #seeknr, pro = prolog(source, testresolver)
    #assert seeknr == length

