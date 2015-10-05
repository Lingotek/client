from tinydb import TinyDB, where
import os
from constants import CONF_DIR, DB_FN

class DocumentManager:
    def __init__(self, path):
        db_file = os.path.join(path, CONF_DIR, DB_FN)
        self._db = TinyDB(db_file)

    def doc_exists(self, file_name, title):
        entries = self._db.search((where('file_name') == file_name) & (where('name') == title))
        if entries:
            return True
        else:
            return False

    def is_doc_new(self, file_name):
        file_name_exists = self._db.search(where('file_name') == file_name)
        if not file_name_exists:
            return True
        return False

    def is_doc_modified(self, file_name):
        entry = self._db.get(where('file_name') == file_name)
        last_modified = os.stat(file_name).st_mtime
        if entry and entry['added'] < last_modified and entry['last_mod'] < last_modified:
            return True
        return False

    def add_document(self, title, create_date, doc_id, sys_mtime, last_mod, file_name):
        entry = {'name': title, 'added': create_date, 'id': doc_id,
                 'sys_last_mod': sys_mtime, 'last_mod': last_mod, 'file_name': file_name}
        self._db.insert(entry)

    # def update_document(self, doc_id, last_mod, sys_mtime, file_name, title=None):
    #     entry = {'last_mod': last_mod, 'sys_last_mod': sys_mtime, 'file_name': file_name}
    #     if title:
    #         entry['name'] = title
    #     self._db.update(entry, where('id') == doc_id)

    # def update_document_locale(self, file_name, locales):
    #     pass

    def update_document(self, field, new_val, doc_id):
        if type(new_val) is list:
            self._db.update(_update_entry_list(field, new_val), where('id') == doc_id)
        else:
            self._db.update({field: new_val}, where('id') == doc_id)

    def get_doc_by_prop(self, prop, expected_value):
        """ get documents by the specified property """
        entry = self._db.get(where(prop) == expected_value)
        return entry

    def get_all_entries(self):
        return self._db.all()

    def get_doc_ids(self):
        """ returns all the ids of documents that user has added """
        doc_ids = []
        for entry in self._db.all():
            doc_ids.append(entry['id'])
        return doc_ids

    def remove_element(self, doc_id):
        self._db.remove(where('id') == doc_id)

def _update_entry_list(field, new_val):
    """
    updates a list in an entry
    """
    def transform(element):
        try:
            element[field]
        except KeyError:
            element[field] = []
        element[field].extend(new_val)

    return transform