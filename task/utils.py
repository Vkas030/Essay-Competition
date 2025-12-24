# tasks/utils/evaluator.py
import re
from spellchecker import SpellChecker

# language_tool_python can be slow to import; handle ImportError gracefully
try:
    import language_tool_python
    TOOL_AVAILABLE = True
    tool = language_tool_python.LanguageTool("en-US")
except Exception:
    TOOL_AVAILABLE = False
    tool = None

spell = SpellChecker()

MAX_SCORE = 100
POINTS_PER_ERROR = 2  # adjust as you like


def _tokenize_words(text):
    """
    Return list of words (lowercased) ignoring punctuation.
    Keeps contractions like "don't".
    """
    return re.findall(r"\b[\w']+\b", text.lower())


def evaluate_essay(text, suggestions_limit=8):
    """
    Returns a dict:
    {
      "score": float,
      "grammar_errors": int,
      "spelling_errors": int,
      "total_errors": int,
      "word_count": int,
      "spelling_list": [ "word1", ... ],
      "grammar_examples": [
         { "message": "...", "offset": 12, "length": 5, "replacements": ["..."] }, ...
      ]
    }
    - grammar_errors excludes matches coming from the spelling rule (MORFOLOGIK_RULE),
      so spelling is counted only by spellchecker.
    """
    if text is None:
        text = ""

    words = _tokenize_words(text)
    word_count = len(words)

    # ------------------------
    # Spelling (SpellChecker)
    # ------------------------
    # SpellChecker expects lowercased words
    misspelled_set = set(spell.unknown(words))
    spelling_errors = len(misspelled_set)
    spelling_list = sorted(list(misspelled_set))

    # ------------------------
    # Grammar (LanguageTool)
    # ------------------------
    grammar_examples = []
    grammar_errors = 0

    if TOOL_AVAILABLE and text.strip():
        # language_tool_python returns Match objects
        matches = tool.check(text)

        for m in matches:
            # m.ruleId commonly 'MORFOLOGIK_RULE' for spelling suggestions.
            rule_id = getattr(m, "ruleId", None)
            # Skip matches that are spelling (we handle spelling via SpellChecker)
            if rule_id == "MORFOLOGIK_RULE":
                continue

            # Some matches are trivial whitespace issues; optionally filter them out:
            # keep them for now since they are useful grammar/style feedback.

            grammar_errors += 1

            # Collect a compact example with replacements (limit total suggestions returned)
            if len(grammar_examples) < suggestions_limit:
                grammar_examples.append({
                    "message": getattr(m, "message", ""),
                    "offset": getattr(m, "offset", None),
                    "length": getattr(m, "length", None),
                    "replacements": getattr(m, "replacements", [])[:5],
                    "ruleId": rule_id
                })
    else:
        # If LanguageTool not available, grammar_errors stays 0 and grammar_examples empty
        grammar_errors = 0
        grammar_examples = []

    # ------------------------
    # Totals & Score
    # ------------------------
    total_errors = spelling_errors + grammar_errors
    score = MAX_SCORE - (total_errors * POINTS_PER_ERROR)
    if score < 0:
        score = 0

    return {
        "score": round(score, 2),
        "grammar_errors": grammar_errors,
        "spelling_errors": spelling_errors,
        "total_errors": total_errors,
        "word_count": word_count,
        "spelling_list": spelling_list,         # list of misspelled words
        "grammar_examples": grammar_examples,   # example grammar matches with suggestions
    }
