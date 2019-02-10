import numpy as np


class Tools:
    @staticmethod
    def calc_exp(x, a_zero, a_infinity, a_n, n):
        a = a_zero - a_infinity
        b = -1 * np.log((a_n - a_infinity) / (a_zero - a_infinity)) / n
        c = a_infinity
        return a * np.exp(-b * x) + c

    @staticmethod
    def sort_by_index(list_to_sort, index=1, descending=True):
        return sorted(list_to_sort, key=lambda x: x[index], reverse=descending)

    @staticmethod
    def sort_by_secondary_key(dict_to_sort, secondary_key=1, descending=True):
        return sorted(dict_to_sort.items(), key=lambda item: item[1][secondary_key], reverse=descending)

    @staticmethod
    def sort_by_score(verses, descending=True):
        return sorted(verses, key=lambda x: x.score, reverse=descending)

    @staticmethod
    def filter_unique_by_index(list_to_filter: list, unique_index: int):
        seen = set()
        unique_list = []
        if list_to_filter is not None and len(list_to_filter) > 0:
            for item in list_to_filter:
                if item[unique_index] not in seen:
                    unique_list.append(item)
                    seen.add(item[unique_index])
            return unique_list
        else:
            return []
