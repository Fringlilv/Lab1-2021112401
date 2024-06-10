import pytest
from WordGraph import WordGraph

@pytest.fixture
def word_graph():
    graph = WordGraph()
    str = 'a b e o a b c o a d c'
    words = str.split(' ')
    for wd, wd_next in zip(words[:-1], words[1:]):
        # print(wd, wd_next)
        graph.graph.addEdge(wd, wd_next)
    return graph

def test_queryBridgeWords_exist_0(word_graph):
    assert word_graph.queryBridgeWords('c', 'e') < 0

def test_queryBridgeWords_exist_1(word_graph):
    assert word_graph.queryBridgeWords('a', 'e') == ['b']

def test_queryBridgeWords_exist_m(word_graph):
    assert word_graph.queryBridgeWords('a', 'c') == ['b', 'd']

def test_queryBridgeWords_word_not_in_graph(word_graph):
    assert word_graph.queryBridgeWords(',', 'c') < 0

def test_queryBridgeWords_word_not_str(word_graph):
    assert word_graph.queryBridgeWords('a', 1) < 0

if __name__ == '__main__':
    pytest.main(['-v', __file__])