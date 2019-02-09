''' Stores information on tags and provides id lookup '''

_LEAF_TAGS = {
    1: 'published_tag',
}

_PUBLICATION_TAGS = {
    1: 'multi_author_tag',
    2: 'multi_publisher_tag',
    3: 'multi_language_tag',
    4: 'multi_identifier_tag',
    5: 'mutli_title_tag',
}

_TAG_TYPES = {
    'leaf': _LEAF_TAGS,
    'publication': _PUBLICATION_TAGS,
}


class TagLookup:
    ''' Tag lookup functionality '''

    @staticmethod
    def id_to_table_name(tag_id, tag_type):
        ''' Looks up a table name by a tag id '''
        if tag_type not in _TAG_TYPES.keys():
            return None

        if tag_id not in _TAG_TYPES[tag_type]:
            return None

        return _TAG_TYPES[tag_type][tag_id]

    @staticmethod
    def table_name_to_id(table_name):
        ''' Looks up tag id and type by table name
            returns data in the form of a tuple (id, type)
        '''
        for tag_type, lookup_table in _TAG_TYPES:
            for tid, tname in lookup_table:
                if tname == table_name:
                    return (tid, tag_type)

        return None
