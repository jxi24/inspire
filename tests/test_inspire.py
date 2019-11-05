import os
import inspire
from unittest.mock import patch, call, mock_open
import requests
import pytest

TEST_STRING = """@article{Perry:2019bqg,
      author         = "Perry, Anastasia and Sun, Ranbel and Hughes, Ciaran and
                        Isaacson, Joshua and Turner, Jessica",
      title          = "{Quantum Computing as a High School Module}",
      year           = "2019",
      eprint         = "1905.00282",
      archivePrefix  = "arXiv",
      primaryClass   = "physics.ed-ph",
      reportNumber   = "FERMILAB-FN-1077-T",
      SLACcitation   = "%%CITATION = ARXIV:1905.00282;%%"
}"""

TEST_CITE = r"""\cite{key1} \citet{key2} \citep{key3} \citet*{key4}
                \citep*{key5} \citeauthor{key6} \citeyear{key7}
                \cite{key8, key9, key10, key1, key2} """


@patch('requests.get')
def test_search(mock_request):
    mock_request.return_value.text = TEST_STRING
    obj = inspire.Inspire('html')

    results = obj.search('f eprint 1905.00282')
    print(results)
    assert results == TEST_STRING

    url = 'http://inspirehep.net/search?p=f+eprint+1905.00282&of=hx&em=B'
    mock_request.assert_called_with(url)


@patch('requests.get')
def test_publication_list(mock_request):
    mock_request.return_value.text = TEST_STRING
    obj = inspire.Inspire('html')

    results = obj.publication_list('foo bar', output='bibtex')
    assert results == TEST_STRING

    url = 'http://inspirehep.net/search?p=f+a+foo+bar&of=hx&em=B'
    mock_request.assert_called_with(url)


@patch('requests.get')
def test_get_citation(mock_request):
    mock_request.return_value.text = TEST_STRING
    obj = inspire.Inspire('html')

    results = obj.get_citation('foo')
    assert results == TEST_STRING

    url = 'http://inspirehep.net/search?p=foo&of=hx&em=B'
    mock_request.assert_called_with(url)


def test_find_cite():
    obj = inspire.Inspire('html')

    obj.find_cite(TEST_CITE)
    print(obj.citations)
    assert len(obj.citations) == 10


@patch('inspire.Inspire.get_citation')
def test_generate_bib(mock_citation):
    mock_citation.return_value = TEST_STRING
    obj = inspire.Inspire('html')
    obj.citations = ['key1', 'key2']
    result = obj.generate_bib()
    assert result == ''.join([TEST_STRING, TEST_STRING])

    print(mock_citation.call_args_list)
    mock_citation.assert_has_calls([call('key1', 'bibtex'),
                                    call('key2', 'bibtex')])


@patch('builtins.open', new_callable=mock_open, read_data=TEST_CITE)
def test_parse_latex(mock_file):
    obj = inspire.Inspire('html')
    obj.parse_latex('latex_file.tex', path='tmp')
    mock_file.assert_called_with(os.path.join('tmp', 'latex_file.tex'), 'r')

    assert len(obj.citations) == 10
