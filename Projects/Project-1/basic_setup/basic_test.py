from basic_server import BasicServer
from basic_client import BasicClient
from socket import socket, AF_INET, SOCK_STREAM
import pytest
alphabet = "'()-./abcdefghijklmnopqrstuvwxyz"

word_set = set()
with open('../wordlist.txt', 'r') as f:
    words = f.read().splitlines()
    for word in words:
        word_set.add(word)
    
def pattern_to_list(pattern: str) -> list[str]:
    possible_words = []
    wildcard = False
    
    for i in range(len(pattern)):
        if pattern[i] == '?':
            wildcard = True
            for letter in alphabet:
                new_pattern = pattern[:i] + letter + pattern[i+1:]
                possible_words.extend(pattern_to_list(new_pattern))
    
    if not wildcard:
        possible_words.append(pattern)
        
    return possible_words

def check_output_is_possible_words(pattern: str, output: list[str]):
    possible_words = set(pattern_to_list(pattern))
    for word in output:
        assert word in possible_words

def test_findQuery_exact_match():
    '''tests both findQuery and checkWord methods for exact matches'''
    testServer = BasicServer()
    findQuery = testServer.findQuery
    
    assert findQuery('cat') == (['cat'], 1)
    assert findQuery('bat') == (['bat'], 1)
    assert findQuery('dog') == (['dog'], 1)
    assert findQuery('elephant') == (['elephant'], 1)
    assert findQuery('3422') == ([], 0)

def test_checkWord_with_single_wildcards():
    testServer = BasicServer()
    findQuery = testServer.findQuery
    
    test1 = 'c?t'
    check_output_is_possible_words(test1, findQuery(test1)[0])
    
    test2 = 'd?g'
    check_output_is_possible_words(test2, findQuery(test2)[0])

    test3 = '?ss'
    check_output_is_possible_words(test3, findQuery(test3)[0])

def test_checkWord_with_multiple_wildcards():
    testServer = BasicServer()
    findQuery = testServer.findQuery
    
    test1 = '??t'
    check_output_is_possible_words(test1, findQuery(test1)[0])
    
    test2 = '?o?'
    check_output_is_possible_words(test2, findQuery(test2)[0])

    test3 = 'b??k'
    check_output_is_possible_words(test3, findQuery(test3)[0])
        
