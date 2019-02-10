import rethinkdb as r


class BritishAmericanConnection(object):
    connection = r.connect("localhost", 28015)
    DB = r.db("dict")
    british_american = DB.table("british_american")

    @classmethod
    # Populate British-to-American Database
    def populate_data(cls):
        british_words = cls.read_file_to_list("scripts/database/british.txt")
        american_words = cls.read_file_to_list("scripts/database/american.txt")
        pairs = list()
        for index, british_word in enumerate(british_words):
            pairs.append({"british": british_word, "american": american_words[index]})
        cls.british_american.insert(pairs).run(cls.connection)
        return cls.british_american.coerce_to("array").run(cls.connection)

    # Read txt file into a list
    @staticmethod
    def read_file_to_list(filename: str):
        with open(filename, 'r') as f:
            items = [line.strip() for line in f]
        return items

    # Convert a British word into its American form
    @classmethod
    def british_to_american(cls, british_word: str):
        american_words = cls.british_american.get_all(british_word, index="british")["american"].coerce_to("array").run(
            cls.connection)
        if len(american_words) > 0:
            return american_words[0]
        else:
            return british_word
