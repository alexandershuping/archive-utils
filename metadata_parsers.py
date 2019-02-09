''' Parser classes for automatically reading data from certain filetypes '''

import zipfile  # epub
from lxml import etree  # epub


class AbstractParser:
    ''' Parser for a file type '''
    def __init__(self):
        pass

    @staticmethod
    def parse(filename):
        ''' parse the file and return a dict containing parsed info '''
        pass


class EpubParser(AbstractParser):
    ''' Parser for epub files
        Thanks to stackoverflow
        https://stackoverflow.com/questions/3114786/python-library-to-extract-epub-information
        for the solution. '''

    @staticmethod
    def parse(filename):
        ''' Parses a given epub file '''
        ns = {
            'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
            'pkg': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        compressed_epub = zipfile.ZipFile(filename)
        directory_tx = compressed_epub.read('META-INF/container.xml')
        directory = etree.fromstring(directory_tx)

        infofile_path = directory.xpath('n:rootfiles/n:rootfile/@full-path',
                                        namespaces=ns)[0]
        infofile_tx = compressed_epub.read(infofile_path)
        infofile_all = etree.fromstring(infofile_tx)
        infofile = infofile_all.xpath('/pkg:package/pkg:metadata',
                                      namespaces=ns)[0]

        conversion_dict = {
            'publication': {
            }
        }

        if infofile.xpath('dc:date/text()', namespaces=ns):
            conversion_dict['publication']['date'] = \
                infofile.xpath('dc:date/text()', namespaces=ns)[0]
        else:
            conversion_dict['publication']['date'] = None

        conversion_dict['publication']['authors'] = []
        for entry in infofile.xpath('dc:creator/text()', namespaces=ns):
            conversion_dict['publication']['authors'].append(
                {'name': entry, 'notes': 'primary author'}
            )

        for entry in infofile.xpath('dc:contributor/text()', namespaces=ns):
            conversion_dict['publication']['authors'].append(
                {'name': entry, 'notes': 'contributor'}
            )

        name_fix = {
            'languages': 'language',
            'identifiers': 'identifier',
            'titles': 'title',
            'publishers': 'publisher'
        }
        for field in name_fix.keys():
            conversion_dict['publication'][field] = []
            for entry in infofile.xpath('dc:{field}/text()'
                                        .format(field=name_fix[field]),
                                        namespaces=ns):
                conversion_dict['publication'][field].append(
                    {'name': entry, 'notes': ''}
                )

        return conversion_dict
