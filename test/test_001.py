#!/usr/bin/python3

def test_true():
    assert True

def test_hallo(tmpdir):
    a = "Hallo"
    print("tempdir=", tmpdir)
    assert a == "Hallo"
