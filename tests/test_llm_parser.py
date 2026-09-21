from backend.api.llm_parser import parse_query_with_llm

def test_mock_valid_llm_parser(mock_llm_valid):
    res = parse_query_with_llm('Analyze Wakad', mock_provider=mock_llm_valid)
    assert res.is_valid is True
    assert 'Wakad' in res.localities
    assert res.operation == 'locality_summary'

def test_mock_invalid_schema(mock_llm_invalid):
    res = parse_query_with_llm('Analyze Wakad', mock_provider=mock_llm_invalid)
    assert res.is_valid is True  # Falls back to rule-based parser on invalid LLM output
    assert 'Wakad' in res.localities

def test_mock_out_of_whitelist(mock_llm_out_of_whitelist):
    res = parse_query_with_llm('Analyze Mumbai', mock_provider=mock_llm_out_of_whitelist)
    assert res.is_valid is False
