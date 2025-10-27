from Extra_server import ExtraServer
from Extra_client import ExtraClient
from socket import socket, AF_INET, SOCK_STREAM
import pytest
alphabet = "'()-./abcdefghijklmnopqrstuvwxyz"
    
def test_2():
    testServer = ExtraServer()
    findQuery = testServer.findQuery

    test2 = '?'
    _, matches = findQuery(test2)
    assert matches == 69903
    
def test_3():
    testServer = ExtraServer()
    findQuery = testServer.findQuery
    
    test3 = '?(a)'
    _, matches = findQuery(test3)
    assert matches == 414
    
def test_4():
    testServer = ExtraServer()
    findQuery = testServer.findQuery
    
    test4 = '-?-'
    _, matches = findQuery(test4)
    assert matches == 13
    
def test_1():
    testServer = ExtraServer()
    findQuery = testServer.findQuery
    
    test1 = '??????????'
    _, matches = findQuery(test1)
    assert matches == 24071
