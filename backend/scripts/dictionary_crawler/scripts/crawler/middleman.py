import time

from ..database.database import Synlink


class MiddleMan:
    @classmethod
    def setup(cls, connection, verbose=True):
        cls.connection = connection
        cls.verbose = verbose
        cls.timing = time.time()

    @classmethod
    def update(cls, crawler_id, word_list, relation_pairs, synonym_list):
        if cls.verbose:
            print("Lock acquired by dictionary_crawler", crawler_id)
            current_time = time.time()
            print("Idle for", current_time - cls.timing, "s")
            cls.timing = current_time
        word_count = 0
        if len(word_list) > 0:
            for word in word_list:
                if not cls._word_is_in_db(word):
                    cls._add_keyword(word)
                    word_count += 1
            cls.connection.commit()

        relation_count = 0
        if len(relation_pairs) > 0:
            for relation in relation_pairs:
                parent_record = cls._get_record(relation[0])
                child_record = cls._get_record(relation[1])
                forward_exists, backward_exists = cls._relation_exists(parent_record, child_record)
                if not forward_exists:
                    cls._append_relationship_link(parent_record, child_record)
                    relation_count += 1
                if not backward_exists:
                    cls._append_relationship_link(child_record, parent_record)
                    relation_count += 1
            cls.connection.commit()

        synonym_count = 0
        if len(synonym_list) > 0:
            for synonym in synonym_list:
                parent_record = cls._get_record(synonym[0])
                child_record = cls._get_record(synonym[1])
                exists = cls._synonym_exists(parent_record, child_record)
                if not exists:
                    cls._append_syn_link(parent_record, child_record, synonym[2])
                    synonym_count += 1
            cls.connection.commit()

        if cls.verbose:
            print("Added", word_count, "words")
            print("Added", relation_count, "relation pairs")
            print("Added", synonym_count, "synonym pairs")

    @classmethod
    def _append_relationship_link(cls, word_record, related_word_record):
        word_record.related_children.append(related_word_record)

    @classmethod
    def _append_syn_link(cls, word_record, synonym_record, relevance):
        word_record.syn_links.append(Synlink(word_record, synonym_record, relevance))

    @classmethod
    def _word_is_in_db(cls, word):
        dummy = cls.connection.word_is_in_db(word)
        return dummy

    @classmethod
    def _relation_exists(cls, parent_record, child_record):
        dummy1 = cls.connection.relation_exists(parent_record, child_record)
        dummy2 = cls.connection.relation_exists(child_record, parent_record)
        return dummy1, dummy2

    @classmethod
    def _synonym_exists(cls, parent_record, child_record):
        dummy = cls.connection.synonym_exists(parent_record, child_record)
        return dummy

    @classmethod
    def _get_record(cls, word):
        dummy = cls.connection.get_record(word)
        return dummy

    @classmethod
    def _add_keyword(cls, word):
        cls.connection.add_keyword(word)
