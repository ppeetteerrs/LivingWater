import rethinkdb as r

from backend.tools import DebugTools


class DictConnection(object):
    connection = r.connect("localhost", 28015)
    DB = r.db("dict")
    keyword = DB.table("keywords")
    keyword_relations = DB.table("related_keywords")
    synlinks = DB.table("synlinks")
    syn_decay = 0.7
    related_word_decay = 0.9

    @classmethod
    def get_word_list_syns_and_related(cls, base_word_list: [], add_base_word=True):

        # Get Base Word Records
        all_syn_ids = set()
        # {base word : [id, base word]}
        base_word_records_dict: {str: [str, str]} = cls.keyword.get_all(r.args(base_word_list), index="word").group(
            "word").run(cls.connection)
        # {base word id: {word, syns: { syn_id: weight }}}
        base_word_dict: {str: {str, {str: float}}} = {}

        for key, base_word_record in base_word_records_dict.items():
            base_word_id = base_word_record[0]["id"]
            base_word_dict[base_word_id] = {"word": base_word_record[0]["word"], "syns": {}}
            if add_base_word:
                base_word_dict[base_word_id]["syns"][base_word_id] = 1
                all_syn_ids.add(base_word_id)

        # Get all relevant syns and bases
        _id_args = r.args(list(base_word_dict.keys()))
        # [{"base_id", "syn_id", "weight"}]
        syn_ids = cls.synlinks.get_all(_id_args, index="base_id").coerce_to("array").run(
            cls.connection)
        # [{"base_id", "syn_id", "weight"}]
        base_ids = cls.synlinks.get_all(_id_args, index="syn_id").coerce_to("array").run(
            cls.connection)
        all_syn_ids |= (set([syn_id["syn_id"] for syn_id in syn_ids] + [base_id["base_id"] for base_id in base_ids]))

        for syn_id_record in syn_ids:
            # add to base_word syns_id list
            if syn_id_record["syn_id"] in base_word_dict[syn_id_record["base_id"]]["syns"]:
                # if synlink is already added, take larger weight
                original = base_word_dict[syn_id_record["base_id"]]["syns"][syn_id_record["syn_id"]]
                base_word_dict[syn_id_record["base_id"]]["syns"][syn_id_record["syn_id"]] = max(
                    syn_id_record["weight"] * cls.syn_decay, original)
            else:
                base_word_dict[syn_id_record["base_id"]]["syns"][syn_id_record["syn_id"]] = syn_id_record[
                                                                                                "weight"] * cls.syn_decay
        for base_id_record in base_ids:
            # add to base_word syns_id list
            if base_id_record["base_id"] in base_word_dict[base_id_record["syn_id"]]["syns"]:
                # if synlink is already added, take larger weight
                original = base_word_dict[base_id_record["syn_id"]]["syns"][base_id_record["base_id"]]
                base_word_dict[base_id_record["syn_id"]]["syns"][base_id_record["base_id"]] = max(
                    base_id_record["weight"] * cls.syn_decay, original)
            else:
                base_word_dict[base_id_record["syn_id"]]["syns"][base_id_record["base_id"]] = base_id_record[
                                                                                                  "weight"] * cls.syn_decay

        # {"id": { "id", "word" }}
        syn_records = cls.keyword.get_all(r.args(all_syn_ids)).group("id").run(cls.connection)

        # [{"parent_id", "child_id"}]
        related_word_ids = cls.keyword_relations.get_all(r.args(all_syn_ids), index="parent_id").pluck("parent_id",
                                                                                                       "child_id").coerce_to(
            "array").run(cls.connection)

        # key: id of the root synonym
        # value: ids of the related words
        related_words_dict = {}
        for item in related_word_ids:
            if item["parent_id"] not in related_words_dict:
                related_words_dict[item["parent_id"]] = []
            related_words_dict[item["parent_id"]].append(item["child_id"])

        related_word_records = dict(cls.keyword.get_all(
            r.args([related_word_id_item["child_id"] for related_word_id_item in related_word_ids])).group("id").run(
            cls.connection))

        base_word_weight_dict = {}
        for base_word_id, val in base_word_dict.items():
            # for each base word
            base_word_word = val["word"]
            syns_dict = val["syns"]
            weight_dict = {}
            for syn_id, weight in syns_dict.items():
                # for synonyms:
                syn_record = syn_records[syn_id][0]
                weight_dict[syn_record["word"]] = {"id": syn_record["id"], "weight": weight, "parent": None}
                if syn_id in related_words_dict:
                    # If there are related words for the synonym
                    for syn_related_word_id in related_words_dict[syn_id]:
                        related_word_record = related_word_records[syn_related_word_id][0]
                        if related_word_record["word"] not in weight_dict:
                            weight_dict[related_word_record["word"]] = {"id": related_word_record["id"],
                                                                        "weight": weight * cls.related_word_decay,
                                                                        "parent": syn_record["word"]}
                base_word_weight_dict[base_word_word] = weight_dict
        return base_word_weight_dict

    @classmethod
    def get_word_record(cls, word: str):
        result = cls.keyword.get_all(word, index="word").coerce_to("array").run(cls.connection)
        if len(result) <= 0:
            raise DebugTools.exceptions(301, word)
        return result[0]

    @classmethod
    def word_exists_in_db(cls, word: str):
        result = cls.keyword.get_all(word, index="word").coerce_to("array").run(cls.connection)
        return len(result) > 0

    @classmethod
    def change_syn_record(cls, word_1: str, word_2: str, level: int):
        # Check for invalid levels
        if level > 3 or level < 1 or not isinstance(level, int):
            raise DebugTools.exceptions(302)
        word_1_record = cls.get_word_record(word_1)
        word_2_record = cls.get_word_record(word_2)

        # Update existing links
        response_syn = cls.synlinks.get_all([word_1_record["id"], word_2_record["id"]], index="compound_id").update(
            {"weight": level / 3}).run(
            cls.connection)
        response_base = cls.synlinks.get_all([word_2_record["id"], word_1_record["id"]], index="compound_id").update(
            {"weight": level / 3}).run(
            cls.connection)
        print("response_syn:", response_syn)
        print("response_base:", response_base)
        if response_syn["replaced"] + response_syn["unchanged"] == 0 and response_base["unchanged"] + response_base[
            "unchanged"] == 0:
            # both does not exist
            response = cls.synlinks.insert(
                [{"base_id": word_1_record["id"], "syn_id": word_2_record["id"], "weight": level / 3},
                 {"base_id": word_2_record["id"], "syn_id": word_1_record["id"], "weight": level / 3}]).run(
                cls.connection)
            return "Added synlink " + word_1 + " <=> " + word_2
        elif response_syn["replaced"] + response_syn["unchanged"] == 0:
            # response_syn does not exist
            response = cls.synlinks.insert(
                {"base_id": word_1_record["id"], "syn_id": word_2_record["id"], "weight": level / 3}).run(
                cls.connection)
            return "Added synlink " + word_1 + " => " + word_2
        elif response_base["replaced"] + response_base["unchanged"] == 0:
            # response_base does not exist
            response = cls.synlinks.insert(
                {"base_id": word_2_record["id"], "syn_id": word_1_record["id"], "weight": level / 3}).run(
                cls.connection)
            return "Added synlink " + word_2 + " => " + word_1
        else:
            # both exists
            return "Updated bidirectional synlink between " + word_1 + " and " + word_2

    @classmethod
    def modify_related_words(cls, word_1: str, word_2: str, add_relation: bool):
        # cls.keyword_relations.index_create("compound_id", lambda row: [row["parent_id"], row["child_id"]]).run(cls.connection)
        word_1_record = cls.get_word_record(word_1)
        word_2_record = cls.get_word_record(word_2)
        response_parent_query = cls.keyword_relations.get_all([word_1_record["id"], word_2_record["id"]],
                                                              index="compound_id")
        response_parent = response_parent_query.coerce_to("array").run(cls.connection)
        parent_item = {"parent_id": word_1_record["id"], "child_id": word_2_record["id"]}
        response_child_query = cls.keyword_relations.get_all([word_2_record["id"], word_1_record["id"]],
                                                             index="compound_id")
        response_child = response_child_query.coerce_to("array").run(cls.connection)
        child_item = {"parent_id": word_2_record["id"], "child_id": word_1_record["id"]}
        if len(response_parent) > 0 and len(response_child) > 0:
            # Both exists in db
            if add_relation:
                raise DebugTools.exceptions(305, word_1 + " <=> " + word_2)
            else:
                child_deleted = response_child_query.delete().run(cls.connection)["deleted"]
                parent_deleted = response_parent_query.delete().run(cls.connection)["deleted"]
                if child_deleted + parent_deleted == 2:
                    return "Removed relationship " + word_1 + " <=> " + word_2
                else:
                    raise DebugTools.exceptions(306, child_deleted + parent_deleted)
        elif len(response_parent) > 0:
            # parent exists
            if add_relation:
                cls.keyword_relations.insert(child_item).run(cls.connection)
                return "Added relationship " + word_1 + " => " + word_2
            else:
                parent_deleted = response_parent_query.delete().run(cls.connection)["deleted"]
                if parent_deleted == 1:
                    return "Removed relationship " + word_1 + " => " + word_2
                else:
                    raise DebugTools.exceptions(307, word_1 + " => " + word_2)
        elif len(response_child) > 0:
            # parent exists
            if add_relation:
                cls.keyword_relations.insert(parent_item).run(cls.connection)
                return "Added relationship " + word_2 + " => " + word_1
            else:
                child_deleted = response_child_query.delete().run(cls.connection)["deleted"]
                if child_deleted == 1:
                    return "Removed relationship " + word_2 + " => " + word_1
                else:
                    raise DebugTools.exceptions(307, word_2 + " => " + word_1)
        else:
            # Both not exist
            if add_relation:
                cls.keyword_relations.insert(child_item).run(cls.connection)
                cls.keyword_relations.insert(parent_item).run(cls.connection)
                return "Added relationship " + word_1 + " <=> " + word_2
            else:
                print(response_child)
                raise DebugTools.exceptions(308, word_1 + " <=> " + word_2)

    @classmethod
    def remove_syn_record(cls, word_1: str, word_2: str):
        word_1_record = cls.get_word_record(word_1)
        word_2_record = cls.get_word_record(word_2)
        response_syn = cls.synlinks.get_all([word_1_record["id"], word_2_record["id"]],
                                            index="compound_id").delete().run(
            cls.connection)
        response_base = cls.synlinks.get_all([word_2_record["id"], word_1_record["id"]],
                                             index="compound_id").delete().run(
            cls.connection)
        if response_syn["deleted"] > 0 and response_base["deleted"] > 0:
            # both deleted
            return "Deleted synlink " + word_1 + " <=>" + word_2
        elif response_syn["deleted"] > 0:
            # syn deleted
            return "Deleted synlink " + word_1 + " =>" + word_2
        elif response_base["deleted"] > 0:
            # base deleted
            return "Deleted synlink " + word_2 + " =>" + word_1
        else:
            # no synlink
            raise DebugTools.exceptions(303, word_1 + " <=> " + word_2)

    @classmethod
    def copy_word(cls, new_word: str, copy: str):
        # Check if new word is same as copied word
        if new_word == copy:
            copy = None
        # Check if keyword already exists
        if cls.word_exists_in_db(new_word):
            # Keyword already exists
            raise DebugTools.exceptions(311, new_word)
        elif new_word is None or new_word == "":
            # Invalid keyword
            raise DebugTools.exceptions(304, new_word)
        else:
            new_id = cls.keyword.count().run(cls.connection) + 1
            # Add keyword to dictionary
            cls.keyword.insert({"word": new_word, "id": new_id}).run(cls.connection)
            if copy is None or copy == "":
                return "Added keyword " + new_word
            elif not cls.word_exists_in_db(copy):
                return "Added keyword " + new_word + " but copy keyword does not exist"
            else:
                # Get synlinks and related words of copied word
                copy_word_id = cls.get_word_record(copy)["id"]
                copy_word_synlinks_forward = cls.synlinks.get_all(copy_word_id, index="base_id").coerce_to("array").run(
                    cls.connection)
                copy_word_synlinks_backward = cls.synlinks.get_all(copy_word_id, index="syn_id").coerce_to("array").run(
                    cls.connection)
                copy_word_related_words_forward = cls.keyword_relations.get_all(copy_word_id, index="child_id").coerce_to(
                    "array").run(cls.connection)
                copy_word_related_words_backward = cls.keyword_relations.get_all(copy_word_id, index="parent_id").coerce_to(
                    "array").run(cls.connection)

                # Compile synlinks and related words for new word
                new_syn_records = []
                new_related_records = []
                for synlink in copy_word_synlinks_forward:
                    # Append forward synlinks
                    new_syn_records.append(
                        {"base_id": new_id, "syn_id": synlink["syn_id"], "weight": synlink["weight"]})
                for synlink in copy_word_synlinks_backward:
                    # Append backward synlinks
                    new_syn_records.append(
                        {"base_id": synlink["base_id"], "syn_id": new_id, "weight": synlink["weight"]})

                for related_word in copy_word_related_words_forward:
                    # Append forward related words
                    new_related_records.append({"child_id": new_id, "parent_id": related_word["parent_id"]})
                for related_word in copy_word_related_words_backward:
                    # Append backward related words
                    new_related_records.append({"child_id": related_word["child_id"], "parent_id": new_id})

                syn_count = cls.synlinks.insert(new_syn_records).run(cls.connection)["inserted"]
                related_count = cls.keyword_relations.insert(new_related_records).run(cls.connection)["inserted"]

                print("{} synlinks and {} related word links added".format(syn_count, related_count))
                return "Added keyword {}, {} synonym links and {} related word links.".format(new_word, syn_count, related_count)

    @classmethod
    def delete_word(cls, word: str):
        # Check if keyword already exists
        if not cls.word_exists_in_db(word):
            # Keyword already exists
            raise DebugTools.exceptions(301, word)
        elif word is None or word is "":
            # Invalid keyword
            raise DebugTools.exceptions(304, word)
        else:
            # Copy synlinks and related words
            word_id = cls.get_word_record(word)["id"]
            cls.keyword.get(word_id).delete().run(cls.connection)
            print("Keyword {} deleted".format(word))
            syns_deleted = cls.synlinks.get_all(word_id, index="base_id").delete().run(
                cls.connection)["deleted"]
            syns_deleted += cls.synlinks.get_all(word_id, index="syn_id").delete().run(
                cls.connection)["deleted"]
            related_deleted = cls.keyword_relations.get_all(word_id, index="child_id").delete().run(cls.connection)["deleted"]
            related_deleted += cls.keyword_relations.get_all(word_id, index="parent_id").delete().run(cls.connection)["deleted"]
            print("{} synlinks and {} related word links deleted".format(syns_deleted, related_deleted))
            return "Deleted keyword " + word + ". {} synonyms and {} related word links deleted.".format(syns_deleted, related_deleted)
