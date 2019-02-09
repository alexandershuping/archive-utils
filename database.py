''' Manages the archive index database '''

from tag_info import TagLookup

import sqlite3


class ArchiveDB:
    ''' Manages the archive index database '''

    @staticmethod
    def insert(node):
        ''' Inserts a node into the database '''
        database = sqlite3.connect('../main/db/database.kexi')
        cur = database.cursor()

        cur.execute(
            'SELECT NODE_ID from nodes WHERE NAME=?;',
            (node['name'],)
        )

        extant_ids = cur.fetchall()

        cur.execute(
            'INSERT INTO nodes (NAME) values (?);',
            (node['name'],)
        )

        cur.execute(
            'SELECT NODE_ID from nodes WHERE NAME=?;',
            (node['name'],)
        )

        our_id = None

        for nid in cur.fetchall():
            if nid not in extant_ids:
                our_id = nid

        node['id'] = our_id

        for leaf in node['leaves']:
            cur.execute(
                'INSERT INTO leaves (NAME, NODE, PATH, TYPE) ' +
                'VALUES (?,?,?,?);',
                (leaf['name'], our_id, leaf['path'], leaf['type'])

            )

            if 'tags' not in leaf.keys():
                continue

            for tag_name, tag_val in leaf['tags']:
                if tag_name == 'publication':
                    ArchiveDB._parse_publication(tag_val, leaf, node, cur)

    @staticmethod
    def _parse_publication(publication, leaf, node, cur):
        for publisher in publication['publishers']:
            pid = ArchiveDB._query_publisher_by_name(publisher)
            if not pid:
                ArchiveDB._add_publisher(publisher, cur)
            elif len(pid) > 1:
                print('Multiple publishers found with the name {name}.'.format(
                    name=publisher
                ))
                for dex, publisher_id in enumerate(pid):
                    # TODO left off here (see below)

    @staticmethod
    def _add_publisher(publisher, cur):
        cur.execute(
            'INSERT INTO publishers (NAME) values (?);',
            (publisher,)
        )

    @staticmethod
    def _query_publisher_by_name(name, cur):
        cur.execute(
            'SELECT PUBLISHER_ID FROM publishers WHERE NAME=?;',
            (name,)
        )
        flattened = []
        for item in cur.fetchall():
            flattened.append(item[0])
        return flattened

    @staticmethod
    def _query_author_by_name(name, cur):
        cur.execute(
            'SELECT AUTHOR_ID FROM authors WHERE NAME=?;',
            (name,)
        )
        flattened = []
        for item in cur.fetchall():
            flattened.append(item[0])
        return flattened

    @staticmethod
    def _get_publications_by_publisher(publisher_id, cur):
        cur.execute(
            'SELECT PUBLICATION_ID FROM publications WHERE PUBLISHER=?',
            (publisher_id,)
        )
        pubs = []
        for item in cur.fetchall():
            pubs.append(item[0])

        cur.execute(
            'SELECT PUBLICATION FROM multi_publisher_tag WHERE PUBLISHER=?',
            (publisher_id,)
        )

        for item in cur.fetchall():
            if item[0] not in pubs:
                pubs.append(item[0])

        return pubs

    @staticmethod
    def _get_publications_by_author(author_id, cur):
        cur.execute(
            'SELECT PUBLICATION_ID FROM publications WHERE AUTHOR=?',
            (author_id,)
        )
        pubs = []
        for item in cur.fetchall():
            pubs.append(item[0])

        cur.execute(
            'SELECT PUBLICATION FROM multi_author_tag WHERE AUTHOR=?',
            (author_id,)
        )

        for item in cur.fetchall():
            if item[0] not in pubs:
                pubs.append(item[0])

        return pubs

    @staticmethod
    def _get_publication_info(publication_id, cur):
        cur.execute(
            'SELECT NODE, TITLE, AUTHOR, PUBLISHER, DATE, LANGUAGE, ' +
            'IDENTIFIER, NOTES FROM publications WHERE PUBLICATION_ID=?',
            (publication_id,)
        )

        node, title, author, publisher, date, language, identifier, notes = \
            cur.fetchone()

        cur.execute(
            'SELECT TAG_ID FROM publication_tags WHERE PUBLICATION=?;',
            (publication_id,)
        )

        for tag in cur.fetchall():
            tag = tag[0]
            if tag == 1:
                # TODO left off here (see below)

        return {
            'node_id': node,
            'title': title,
            'author_id': author,
            'publisher_id': publisher,
        }

    @staticmethod
    def _multi_tag_get(table_name, field_type, publication, cur):
        cur.execute(
            'SELECT {field}, NOTES FROM {table} WHERE PUBLICATION=?;'.format(
                field=field_type, table=table_name
            ),
            (publication,)
        )

        for tag in cur.fetchall():
            # TODO left off here
