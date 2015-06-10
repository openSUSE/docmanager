#

import pytest

from lxml import etree
from docmanager.xmlutil import findinfo_pos


IDS =['with_title', 'with_subtitle', 'with_titleabbrev',
      #
      'with_comment_before_title', 'with_comment_before_title_and_subtitle',
      'with_comment_before_title_subtitle_and_titleabbrev',
      #
      'with_pi_before_title', 'with_pi_before_title_and_subtitle',
      'with_pi_before_title_subtitle_and_titleabbrev',
      #
      'with_comment_between_title_and_subtitle',
      'with_comment_between_title_and_subtitle_and_titleabbrev',
      #
      'with_pi_between_title_and_subtitle',
      'with_pi_between_title_and_subtitle_and_titleabbrev',
     ]

xmltestlist = [
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '</sect1>',
    1
  ),
  #
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '</sect1>',
    2
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '  <titleabbrev/>\n'
    '</sect1>',
    3
  ),
  # ------------------------
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <!-- comment -->\n'
    '  <title/>\n'
    '</sect1>',
    2
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <!-- comment -->\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '</sect1>',
    3
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <!-- comment -->\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '  <titleabbrev/>\n'
    '</sect1>',
    4
  ),
  # ------------------------
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <?foo?>\n'
    '  <title/>\n'
    '</sect1>',
    2
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <?foo?>\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '</sect1>',
    3
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <?foo?>\n'
    '  <title/>\n'
    '  <subtitle/>\n'
    '  <titleabbrev/>\n'
    '</sect1>',
    4
  ),
  # ------------------------
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <!-- x -->\n'
    '  <subtitle/>\n'
    '</sect1>',
    3
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <!-- x -->\n'
    '  <subtitle/>\n'
    '  <!-- y -->\n'
    '  <titleabbrev/>\n'
    '</sect1>',
    5
  ),
  # ------------------------
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <?foo?>\n'
    '  <subtitle/>\n'
    '</sect1>',
    3
  ),
  ( '<sect1 xmlns="http://docbook.org/ns/docbook" version="5.0">\n'
    '  <title/>\n'
    '  <?foo?>\n'
    '  <subtitle/>\n'
    '  <?bar?>\n'
    '  <titleabbrev/>\n'
    '</sect1>',
    5
   ),
]

@pytest.mark.parametrize("xml, expected", xmltestlist, ids=IDS)
def test_findinfo_pos(xml, expected):
    root = etree.XML(xml)
    assert findinfo_pos(root) == expected
