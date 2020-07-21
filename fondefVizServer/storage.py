import os
from urllib.parse import urlsplit, unquote, urlunsplit

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class CustomManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
    max_post_process_passes = 10

    def hashed_name(self, name, content=None, filename=None):
        # `filename` is the name of file to hash if `content` isn't given.
        # `name` is the base name to construct the new hashed filename from.
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        if filename:
            filename = urlsplit(unquote(filename)).path.strip()
        filename = filename or clean_name
        opened = False
        if content is None:
            try:
                content = self.open(filename)
            except IOError:
                # Handle directory paths and fragments
                return name
            opened = True
        try:
            file_hash = self.file_hash(clean_name, content)
        finally:
            if opened:
                content.close()
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        if file_hash is not None:
            file_hash = ".%s" % file_hash
        hashed_name = os.path.join(path, "%s%s%s" %
                                   (root, file_hash, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name

        if '?#' in name and not unparsed_name[3]:
            unparsed_name[2] += '?'
        return urlunsplit(unparsed_name)
