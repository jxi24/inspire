""" Get from the inspire API information.

Possible run modes are:
    - search
    - publication list
    - create bib file based on tex file
    - etc.

Possible output formats are:
    - stdout
    - text file
    - latex file
    - bib file

"""

import sys
import os
import requests
from bs4 import BeautifulSoup
import re

from absl import flags, logging, app

PUB_OUTPUT = {'cv-latex': 'lcv',
              'cv-html': 'cv',
              'cv-text': 'tcv',
              'bibtex': 'x',
              'latex-eu': 'lxe',
              'latex-us': 'lxu'}

OUT_FORM = {'xml': 'x',
            'text': 't',
            'html': 'h'}


class Inspire:

    """ Obtain information from inspirehep.net,
        and parse this into useful formats.
    """

    def __init__(self, out_format):
        """ Initialize the class """
        self.out_format = OUT_FORM[out_format]
        self.root = 'http://inspirehep.net/search?p='
        self.citations = []

    def search(self, search, output='bibtex', **kwargs):
        """ Search given a keyword dictionary """

        options = Inspire._parse_options(**kwargs)
        request = (self.root
                   + search.replace(' ', '+')
                   + '&of=' + self.out_format + PUB_OUTPUT[output]
                   + '&em=B'
                   + options)

        result = self._request(request)
        return result.text

    def publication_list(self, name, output='cv-latex', **kwargs):
        """ Generate a publication list """
        name = name.replace(' ', '+')
        options = Inspire._parse_options(**kwargs)
        request = (self.root
                   + 'f+a+' + name.lower()
                   + '&of=' + self.out_format + PUB_OUTPUT[output]
                   + '&em=B'
                   + options)
        result = self._request(request)
        return result.text

    def get_citation(self, name, output='bibtex'):
        """ Find the citation given the Inspire format string.

        Args:
            name (str): The inspire tag to get a citation for
            output (str): Output format for bibliography

        Returns: Entry in bibliography in requested format

        """
        request = self.root + name + '&of=h' + PUB_OUTPUT[output] + '&em=B'
        result = BeautifulSoup(self._request(request).text, 'lxml')
        return result.text

    def parse_latex(self, filename, path='', format='bibtex'):
        """ Parse a latex file for the bibliography entries in inspire format.

        Args:
            filename (str): name of the latex file to be parsed
            path (str): path to latex file (default = pwd)
            format (str): output format(options are bibtex, latex-us, latex-eu)

        Returns: bibliography in requested format

        """
        with open(os.path.join(path, filename), 'r') as latex:
            for line in latex:
                self._find_cite(line)

    def _find_cite(self, string):
        regex = r"\\cite[a-zA-Z]*{([^}]+)}"
        matches = re.finditer(regex, string)
        for match in matches:
            print(match.group(1))
            citations = match.group(1).split(',')
            print(citations)
            for citation in citations:
                if citation not in self.citations:
                    self.citations.append(citation.strip())

    @staticmethod
    def _parse_options(**kwargs):
        options = ''
        if 'sort' in kwargs:
            options += '&sf=' + str(kwargs['sort'])
        if 'order' in kwargs:
            options += '&so=' + str(kwargs['order'])
        if 'count' in kwargs:
            options += '&rg=' + str(kwargs['count'])
        if 'start' in kwargs:
            options += '&jec=' + str(kwargs['start'])
        return options

    def _request(self, request):
        return requests.get(request)


if __name__ == '__main__':
    inspire = Inspire('html')
    print(inspire.publication_list('Joshua Isaacson', output='bibtex'))
    print(inspire.search('f a Joshua Isaacson', output='bibtex'))
    print(inspire.get_citation('Su:2014wpa'))

    test_str = ("\\somecommand{test} blabla nonsense lorem ipsum \\cite{key1} "
                "and \\cite{key2, key3, key4} and \\citep{key5} \\cite{key4}")

    inspire._find_cite(test_str)
