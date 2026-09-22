from backend.api.fallback_parser import parse_query_rule_based

def test_fallback_wakad():
    res = parse_query_rule_based('Tell me about Wakad')
    assert res.is_valid is True
    assert 'Wakad' in res.localities

def test_fallback_compare():
    res = parse_query_rule_based('Compare Wakad vs Akurdi')
    assert res.is_valid is True
    assert 'Wakad' in res.localities
    assert 'Akurdi' in res.localities
    assert res.operation == 'compare'

def test_fallback_best():
    res = parse_query_rule_based('Best investment area in Pune')
    assert res.is_valid is True
    assert len(res.localities) == 4
    assert res.operation == 'top_n'
