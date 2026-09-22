from backend.api.executor import execute_query
from backend.api.schemas import StructuredQuery

def test_utf8_formatting_no_broken_bytes():
    struct = StructuredQuery(
        operation='locality_summary',
        metric='flat_rate',
        localities=['Wakad'],
        start_year=2020,
        end_year=2024,
        group_by='year',
        is_valid=True
    )
    res = execute_query(struct)
    summary = res['summary']
    assert '\ufffd' not in summary
    assert '₹' in summary
