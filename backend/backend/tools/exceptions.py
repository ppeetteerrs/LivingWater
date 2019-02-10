# This class handles exceptions. All exceptions raised will be passed through the API to the client

class DebugException(Exception):
    exception_dict = {
        101: "Don't be naughty, type something with meaning >.<",  # "Invalid input, please check your sentence",
        301: "Keyword not found in Database",
        302: "Invalid Synonym Level. Level must be integer between 1 and 3",
        303: "No Synonym Link found",
        304: "Invalid base word",
        305: "Relationship already exists",
        306: "Relationship count is not 2",
        307: "Relationship not deleted",
        308: "Relationships don't exist",
        309: "Invalid synonym",
        310: "Synonym is the same as base word...",
        311: "Keyword already exists",
        # 500 series: Verse database
        501: "Cannot find verse, please check spelling and capitalization",
        502: "Verse in this location already exists",
        503: "Why are you editing a non-existent record??",
        504: "Keyword levels can only be 1, 2 or 3",
        505: "Invalid Verse Location, Check Again",
        506: "Invalid Bible Version, Check Again",
        507: "Cannot Parse Bible Location, Check Again"
    }

    def __init__(self, code, message=""):
        self.code = code
        self.title = self.exception_dict[self.code]
        self.message = message

    def __str__(self):
        if self.message is "":
            return "Exception " + str(self.code) + " " + self.title
        else:
            return "Exception " + str(self.code) + " " + self.title + ": " + self.message
