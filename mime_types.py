''' Well-known MIME types associated with certain extensions '''

_MIME_TYPES = {
    # E-book types
    'epub': 'application/epub+zip',
    'mobi': 'application/x-mobipocket-ebook',
    'zip': 'application/zip',
    'pdf': 'application/pdf',

    # Image types
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',

    # Multimedia (audio + video) types
    'mkv': 'video/webm',
    'mp4': 'video/mp4',
    'ogg': 'audio/ogg',
    'mp3': 'audio/mpeg',

    # Youtube captions
    'en.vtt': 'text/plain',
}

_TYPE_PRIORITY = {
    'video/webm': 700,
    'video/mp4': 701,

    'application/epub+zip': 500,
    'application/x-mobipocket-ebook': 450,
    'application/pdf': 300,

    'audio/ogg': 250,
    'audio/mpeg': 251,

    'image/jpeg': 200,
    'image/gif': 201,
    'image/png': 202,

    'application/zip': 0,

    'text/plain': -100,
}


class MIMELookup:
    ''' MIME-type lookup functionality '''

    @staticmethod
    def extension_to_mime(extension):
        ''' Retrieves the mime-type associated with an extension '''
        if extension not in _MIME_TYPES:
            return None
        else:
            return _MIME_TYPES[extension]

    @staticmethod
    def mime_to_extension(mime):
        ''' Retrieves the extension associated with a MIME-type '''
        for extension, mime_type in _MIME_TYPES:
            if mime == mime_type:
                return extension
        return None

    @staticmethod
    def priority_batch_lookup(types):
        ''' Uses priority rules to determine the "primary" MIME-type to use
            for any given set of file extensions '''

        best_type = MIMELookup.extension_to_mime(types[0])
        type_priority = -10000

        for to_check in types:
            to_check = MIMELookup.extension_to_mime(to_check)
            if to_check not in _TYPE_PRIORITY:
                continue

            if _TYPE_PRIORITY[to_check] > type_priority:
                type_priority = _TYPE_PRIORITY[to_check]
                best_type = to_check

        return best_type
