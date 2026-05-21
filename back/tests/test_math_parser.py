from decimal import Decimal
from app.services.rule_resolver import MathSafeParser


def test_math_parser_basic_arithmetic():
    parser = MathSafeParser({})
    assert parser.evaluate("2 + 3") == Decimal("5")
    assert parser.evaluate("10 - 4") == Decimal("6")
    assert parser.evaluate("3 * 4") == Decimal("12")
    assert parser.evaluate("10 / 2") == Decimal("5")


def test_math_parser_constants():
    parser = MathSafeParser({})
    assert parser.evaluate("5") == Decimal("5")
    assert parser.evaluate("10.5") == Decimal("10.5")


def test_math_parser_variables():
    parser = MathSafeParser({"load_count": 3})
    assert parser.evaluate("load_count * 2") == Decimal("6")
    assert parser.evaluate("load_count + 1") == Decimal("4")
    assert parser.evaluate("load_count / 3") == Decimal("1")


def test_math_parser_nested_and_complex():
    parser = MathSafeParser({"load_count": 4})
    assert parser.evaluate("(load_count + 2) * 3") == Decimal("18")
    assert parser.evaluate("10 - (2 * 3)") == Decimal("4")
    assert parser.evaluate("((load_count * 2) + 2) / 2") == Decimal("5")


def test_math_parser_unary_operations():
    parser = MathSafeParser({"x": 5})
    assert parser.evaluate("-5") == Decimal("-5")
    assert parser.evaluate("-x") == Decimal("-5")
    assert parser.evaluate("10 + (-2)") == Decimal("8")


def test_math_parser_case_insensitivity():
    # The parser lowercases the formula string
    parser = MathSafeParser({"load_count": 3})
    assert parser.evaluate("LOAD_COUNT * 2") == Decimal("6")
    assert parser.evaluate("Load_Count + 5") == Decimal("8")


def test_math_parser_non_math_text_and_na():
    parser = MathSafeParser({})
    assert parser.evaluate("N/A") == Decimal("0")
    assert parser.evaluate("See notes") == Decimal("0")
    assert parser.evaluate("") == Decimal("0")
    assert parser.evaluate(None) == Decimal("0")
    assert parser.evaluate("   ") == Decimal("0")


def test_math_parser_division_by_zero():
    parser = MathSafeParser({"x": 10})
    # Current implementation logs error and returns Decimal("0") on Exception
    assert parser.evaluate("x / 0") == Decimal("0")


def test_math_parser_unknown_variable():
    parser = MathSafeParser({"load_count": 3})
    # Unknown variable results in ValueError in _eval, caught in evaluate
    assert parser.evaluate("unknown_var + 1") == Decimal("0")


def test_math_parser_syntax_error():
    parser = MathSafeParser({})
    # Syntax error like "2 ++ 3" should be caught and return 0
    assert parser.evaluate("2 ++ 3") == Decimal("0")


def test_math_parser_unsupported_elements():
    parser = MathSafeParser({})
    # Something like list or strings in the formula
    assert parser.evaluate("[1, 2, 3]") == Decimal("0")
    assert parser.evaluate("'hello'") == Decimal("0")
