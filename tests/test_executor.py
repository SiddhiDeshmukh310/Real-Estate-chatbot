from backend.api.schemas import StructuredQuery
from backend.api.executor import execute_query

def test_execute_query_wakad():
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
    assert 'Wakad Overview' in res['summary']
    assert 'Wakad' in res['areas']
    assert len(res['chart']) == 5
    assert 'Wakad' in res['tables']

def test_execute_query_compare():
    struct = StructuredQuery(
        operation='compare',
        metric='flat_rate',
        localities=['Wakad', 'Akurdi'],
        start_year=2020,
        end_year=2024,
        group_by='location',
        is_valid=True
    )
    res = execute_query(struct)
    assert 'Comparison' in res['summary']
    assert len(res['areas']) == 2
