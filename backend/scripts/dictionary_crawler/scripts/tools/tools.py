import string


def clean(word):
    if word is None:

        return None

    else:

        try:
            if word.strip().startswith("<"):
                return None
            else:
                # Remove all punctuations
                no_punc = word.translate(str.maketrans('', '', string.punctuation))
        except Exception:
            print("\nError removing punctuations from word", word, "\n")
            return None

        # Remove all whitespaces
        no_white = no_punc.strip()

        # Lowercase
        lowercase = no_white.lower()

        return lowercase
