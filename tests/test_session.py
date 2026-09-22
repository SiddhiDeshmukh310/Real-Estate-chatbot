from backend.api.schemas import StructuredQuery
from backend.api.session import process_follow_up, clear_session

def test_session_follow_up():
    session_id = 'test_sess_1'
    clear_session(session_id)
    
    q1 = StructuredQuery(
        operation='locality_summary',
        metric='flat_rate',
        localities=['Aundh'],
        start_year=2020,
        end_year=2024,
        group_by='year',
        is_valid=True
    )
    process_follow_up(session_id, 'Analyze Aundh', q1)
    
    # Follow up query
    q2_stub = StructuredQuery(operation='locality_summary', localities=['Wakad'], is_valid=True)
    res = process_follow_up(session_id, 'what about the same for Wakad?', q2_stub)
    
    assert res.localities == ['Wakad']
    assert res.operation == 'locality_summary'
