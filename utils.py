import re


# ─────────── Manage Mirror ───────────
def mirror_name(name: str) -> str:
    """
    Mirrors left/right identifiers used in Blender naming conventions.
    Works for:
        - .L <-> .R
        - _L <-> _R
        - .l <-> .r
        - _l <-> _r
        - .Left / _Left <-> .Right / _Right
        - Lt <-> Rt, Lf <-> Rf
    """
    # Long-word tokens to protect first
    long_pairs = [
        ("Left", "Right"),
        ("left", "right"),
        ("LEFT", "RIGHT"),
        ("Lt", "Rt"),
        ("lt", "rt"),
        ("LT", "RT"),
        ("Lf", "Rf"),
        ("lf", "rf"),
        ("LF", "RF"),
    ]

    # Separator boundaries (start, end, or non-letter/digit)
    sep_before = r"(^|[^A-Za-z0-9])"
    sep_after = r"([^A-Za-z0-9]|$)"

    # Phase 1: protect left tokens with placeholders
    for idx, (l, r) in enumerate(long_pairs):
        placeholder = f"__TMP_{idx}__"
        name = re.sub(sep_before + re.escape(l) + sep_after,
                      lambda m: m.group(1) + placeholder + m.group(2),
                      name)
        # swap right to left
        name = re.sub(sep_before + re.escape(r) + sep_after,
                      lambda m: m.group(1) + l + m.group(2),
                      name)
        # restore placeholder → right
        name = name.replace(placeholder, r)

    # Phase 2: suffix and short letter variants
    suffix_patterns = [
        (r"([._])L(\b|$)", r"\1__TMP_R__\2"),
        (r"([._])R(\b|$)", r"\1L\2"),
        (r"__TMP_R__", "R"),

        (r"([._])l(\b|$)", r"\1__TMP_r__\2"),
        (r"([._])r(\b|$)", r"\1l\2"),
        (r"__TMP_r__", "r"),
    ]
    for pat, rep in suffix_patterns:
        name = re.sub(pat, rep, name)
    return name


# ─────────── Manage Case ───────────
def apply_case(name: str, mode: str) -> str:
    mode = mode.upper()
    if mode == "UPPER": return name.upper()
    if mode == "LOWER": return name.lower()
    if mode == "TITLE": return "_".join(part.title() for part in name.split("_"))
    return name


# ─────────── Manage Sequence ───────────
def generate_sequence(base: str, start: str, index: int, last: str = "") -> str:
    """
    Generate a sequence string supporting:
      - Numeric: '1', '2', ...
      - Uppercase letters: 'A', 'B', 'C', ...
      - Lowercase letters: 'a', 'b', 'c', ...
    """
    start = start.strip() or "1"
    seq_str = ""

    if start.isdigit():
        seq_str = str(int(start) + index)
    elif len(start) == 1 and start.isalpha():
        is_lower = start.islower()
        start_val = ord(start.upper()) - ord('A')
        seq_str = _index_to_letters(start_val + index)
        if is_lower:
            seq_str = seq_str.lower()
    else:
        seq_str = str(index + 1)

    return f"{base}{seq_str}{last}"


def _index_to_letters(index: int) -> str:
    letters = ""
    index += 1  # A = 1
    while index > 0:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters