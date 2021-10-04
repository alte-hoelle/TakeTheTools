from random import randint


def gen_random_ean13_no_checkbit(prefix: str = "99") -> str:
    """
    Generates a random barcode, respecting the length of the given prefix.
    """
    len_id = 12 - len(prefix)
    randint_upper_bound = int(9.99999999999 ** len_id)
    return prefix + str(randint(1, randint_upper_bound)).zfill(len_id)
