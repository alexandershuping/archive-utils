#!/usr/bin/env python3

''' Archives files by standardizing their names, moving them to appropriate
    locations, and adding relevant metadata to the database.
'''

from database import ArchiveDB
from metadata_parsers import EpubParser
from mime_types import MIMELookup
from tag_info import TagLookup

import datetime
import subprocess
import os


SAFE_CHARACTERS = 'abcdefghijklmnopqrstuvwxyz' \
    + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
    + '0123456789.'

PUNCTUATION_CHARACTERS = '-_'

KNOWN_EXTENSIONS = {
    # IMAGES
    'jpg': None,
    'png': None,

    # VIDEOS
    'mkv': None,
    'mp4': None,
    'en.vtt': None,  # Captions

    # VIDEOGAMES
    'iso': None,

    # BOOKS
    'epub': EpubParser,
    'mobi': None,
    'pdf': None
}

BASE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/..'
BUCKET_DIR = '{BASE}/inbox'.format(BASE=BASE_DIR)


class ArchiveUtils:
    ''' Utilities for archives '''
    @staticmethod
    def intake():
        ''' Parses files '''
        long_extensions = []
        print('Parsing files from the intake bucket...')
        parsed_intake = ArchiveUtils.parse_intake_bucket()
        print('Found {num} elements'.format(num=len(parsed_intake.keys())))
        for lead in parsed_intake.keys():
            print('  [  element] {lead}'.format(lead=lead))
            print('  [sanitized] {san}'.format(
                san=ArchiveUtils.sanitize(lead)))
            for extension in parsed_intake[lead]:
                if len(extension) > 4 and \
                  extension not in KNOWN_EXTENSIONS.keys():
                    long_extensions.append((lead, extension))
                print('    >  [part] {ext}'.format(ext=extension))

            choice = input('Add this file to the database? [y/n] >')
            if choice.lower() == 'y':
                print('\n >> Using "{name}" as node name. <<'.format(
                    name=lead))
                name_to_use = lead
                choice = input('Is this ok? [y/n] >')
                if choice.lower() != 'y':
                    in_name = input('New name (leave empty to cancel) >')
                    if in_name:
                        name_to_use = in_name
                    
                db_node = {'name': name_to_use, 'leaves': []}

                prime_type = MIMELookup.priority_batch_lookup(
                    parsed_intake[lead])

                target_directory = '{root}/main/{ftype}/{name}'.format(
                    root=BASE_DIR, ftype=prime_type, name=name_to_use
                )

                if os.path.exists(target_directory):
                    # ''' TODO '''
                    print('Node already exists. TODO: implement node-add code')
                    continue
                else:
                    # print('mkdir {tdir}'.format(tdir=target_directory))
                    os.makedirs(target_directory)

                for extension in parsed_intake[lead]:
                    leaf_path = '{rdir}/{archive_date}_{sname}.{ext}'.format(
                        rdir=target_directory,
                        archive_date=datetime.datetime.now().strftime(
                            '%Y-%m-%d_%H-%M-%S_%f'
                        ),
                        sname=ArchiveUtils.sanitize(name_to_use),
                        ext=extension
                    )

                    db_leaf = {
                        'name': extension,
                        'path': leaf_path,
                        'type': MIMELookup.extension_to_mime(extension)
                    }

                    # print('{bucket}/{node}.{leaf}'.format(
                    #     bucket=BUCKET_DIR,
                    #     node=lead,
                    #     leaf=extension
                    # ) + ' -> {dest}'.format(dest=leaf_path))
                    os.rename('{bucket}/{node}.{leaf}'.format(
                        bucket=BUCKET_DIR,
                        node=lead,
                        leaf=extension
                    ), leaf_path)

                    if extension in KNOWN_EXTENSIONS.keys():
                        if KNOWN_EXTENSIONS[extension]:
                            db_leaf['tags'] = \
                                KNOWN_EXTENSIONS[extension].parse(leaf_path)

                    db_node['leaves'].append(db_leaf)

                ArchiveDB.insert(db_node) # TODO finish this function

        if long_extensions:
            print('\n\n===WARNING===\nSome files have unknown, long extensions'
                  + '. Please check the below filenames, and remove any'
                  + ' extraneous periods:\n')
            for long_extension in long_extensions:
                print('  > {fname}.[{fext}]'.format(
                    fname=long_extension[0],
                    fext=long_extension[1]
                ))

        print('\n')

    @staticmethod
    def parse_intake_bucket():
        ''' Finds all files in the intake bucket, then parses them into
            an easier-to-use dict of files
        '''
        parsed_intake = {}

        filenames = subprocess.check_output('ls "{BUCKET}"'.format(
            BUCKET=BUCKET_DIR),
            shell=True
            ).split(b'\n')[:-1]

        for fname in filenames:
            fname = fname.decode('UTF-8')
            in_leader = True
            f_lead = ''
            f_extension = ''
            for char in fname:
                if in_leader:
                    if char == '.':
                        in_leader = False
                    else:
                        f_lead = f_lead + char
                else:
                    f_extension = f_extension + char

            if f_lead in parsed_intake.keys():
                if f_extension in parsed_intake[f_lead]:
                    fname2 = f_lead + '_duplicate.' + f_extension
                    print('WARNING: duplicate file {fname}!'.format(
                            fname=fname)
                          + ' Renamed to {fname_2}!'.format(
                            fname_2=fname2)
                          )
                parsed_intake[f_lead].append(f_extension)
            else:
                parsed_intake[f_lead] = [f_extension]

        return parsed_intake

    @staticmethod
    def sanitize(name):
        ''' Sanitizes a file name to remove extraneous characters '''
        sanitized_name = ''
        for char in name:
            if char in SAFE_CHARACTERS:
                sanitized_name = sanitized_name + char
            else:
                if sanitized_name[-1] in PUNCTUATION_CHARACTERS:
                    continue  # suppress multipule punctuations in a row
                else:
                    if char in PUNCTUATION_CHARACTERS:
                        sanitized_name = sanitized_name + char
                    else:
                        sanitized_name = sanitized_name + '_'

        if sanitized_name[-1] in PUNCTUATION_CHARACTERS:
            return sanitized_name[:-1]

        return sanitized_name


ArchiveUtils.intake()
