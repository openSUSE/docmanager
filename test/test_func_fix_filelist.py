from docmanager.cli import fix_filelist

def test_func_fix_filelist_0():
	"""Tests the function fix_filelist from cli.py
	"""

	expected_files = [
		'test/testfiles/globtest/missing_info_element.xml',
		'test/testfiles/globtest/analyze_output-1.xml',
		'test/testfiles/globtest/analyze_output-2.xml',
		'test/testfiles/globtest/dm-test.conf',
		'test/testfiles/globtest/docmanager_overwrite_test.xml',
		'test/testfiles/globtest/analyze_output-3.xml',
		'test/testfiles/globtest/broken_xml_file.xml'
	]

	files = [ "test/testfiles/globtest/*" ]
	fix_filelist(files)

	assert set(files) == set(expected_files)

def test_func_fix_filelist_1():
	"""Tests the function fix_filelist from cli.py
	"""
	expected_files = [
		'test/testfiles/globtest/analyze_output-3.xml',
		'test/testfiles/globtest/analyze_output-2.xml',
		'test/testfiles/globtest/analyze_output-1.xml'
	]

	files = [ "test/testfiles/globtest/*-*.xml" ]
	fix_filelist(files)

	assert set(files) == set(expected_files)

def test_func_fix_filelist_2():
	"""Tests the function fix_filelist from cli.py
	"""
	expected_files = [
		'test/testfiles/globtest/analyze_output-3.xml',
		'test/testfiles/globtest/analyze_output-2.xml',
		'test/testfiles/globtest/analyze_output-1.xml'
	]

	files = [ "test/testfiles/globtest/*-?.x?l" ]
	fix_filelist(files)

	assert set(files) == set(expected_files)

def test_func_fix_filelist_3():
	"""Tests the function fix_filelist from cli.py
	"""
	expected_files = [
		'test/testfiles/globtest/broken_xml_file.xml'
	]

	files = [ "test/testfiles/globtest/*broken*.xml" ]
	fix_filelist(files)

	assert set(files) == set(expected_files)
