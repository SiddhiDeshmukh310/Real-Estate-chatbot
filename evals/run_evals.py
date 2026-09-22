import os
import sys
import json
import pathlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
os.environ['DJANGO_SETTINGS_MODULE'] = 'realestate_chatbot.settings'

import django
django.setup()

from backend.api.fallback_parser import parse_query_rule_based
from backend.api.llm_parser import parse_query_with_llm
from backend.api.session import process_follow_up, clear_session
from backend.api.executor import execute_query
from tests.conftest import MockLLMProvider

def run_evaluation():
    base_dir = pathlib.Path(__file__).parent
    questions_file = base_dir / 'questions.jsonl'
    results_dir = base_dir / 'results'
    results_dir.mkdir(exist_ok=True)

    if not questions_file.exists():
        print('Error: Benchmark file not found.')
        return

    questions = []
    with open(questions_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line.strip()))

    total_n = len(questions)
    print(f'=== Starting Real Estate Insights Evaluation Benchmark (N={total_n}) ===\n')

    rb_exact_matches = 0
    rb_execution_acc = 0
    rb_refusal_acc = 0
    rb_raw_outputs = []

    session_id_rb = 'eval_rb_session'
    clear_session(session_id_rb)

    for q in questions:
        query_text = q['query']
        expected_locs = set(q['expected_localities'])
        expected_op = q['expected_operation']
        expected_valid = q['expected_valid']

        parsed = parse_query_rule_based(query_text)
        parsed = process_follow_up(session_id_rb, query_text, parsed)

        actual_locs = set(parsed.localities)
        actual_op = parsed.operation
        actual_valid = parsed.is_valid

        if not expected_valid:
            if not actual_valid:
                rb_refusal_acc += 1
                rb_exact_matches += 1
                rb_execution_acc += 1
        else:
            if actual_valid and actual_locs == expected_locs and actual_op == expected_op:
                rb_exact_matches += 1

            exec_res = execute_query(parsed)
            if actual_valid and exec_res['areas'] and len(exec_res['summary']) > 20:
                rb_execution_acc += 1

        rb_raw_outputs.append({
            'id': q['id'],
            'query': query_text,
            'expected': {'localities': list(expected_locs), 'operation': expected_op, 'valid': expected_valid},
            'actual': {'localities': parsed.localities, 'operation': parsed.operation, 'valid': parsed.is_valid}
        })

    llm_key_present = any(os.getenv(k) for k in ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'GROQ_API_KEY'])
    mock_provider = None if llm_key_present else MockLLMProvider('valid')
    provider_name = os.getenv('LLM_PROVIDER', 'gemini') if llm_key_present else 'Mock (Deterministic)'

    llm_exact_matches = 0
    llm_execution_acc = 0
    llm_refusal_acc = 0
    llm_raw_outputs = []

    session_id_llm = 'eval_llm_session'
    clear_session(session_id_llm)

    for q in questions:
        query_text = q['query']
        expected_locs = set(q['expected_localities'])
        expected_op = q['expected_operation']
        expected_valid = q['expected_valid']

        parsed = parse_query_with_llm(query_text, mock_provider=mock_provider)
        parsed = process_follow_up(session_id_llm, query_text, parsed)

        actual_locs = set(parsed.localities)
        actual_op = parsed.operation
        actual_valid = parsed.is_valid

        if not expected_valid:
            if not actual_valid:
                llm_refusal_acc += 1
                llm_exact_matches += 1
                llm_execution_acc += 1
        else:
            if actual_valid and actual_locs == expected_locs and actual_op == expected_op:
                llm_exact_matches += 1

            exec_res = execute_query(parsed)
            if actual_valid and exec_res['areas'] and len(exec_res['summary']) > 20:
                llm_execution_acc += 1

        llm_raw_outputs.append({
            'id': q['id'],
            'query': query_text,
            'expected': {'localities': list(expected_locs), 'operation': expected_op, 'valid': expected_valid},
            'actual': {'localities': parsed.localities, 'operation': parsed.operation, 'valid': parsed.is_valid}
        })

    num_valid_questions = sum(1 for q in questions if q['expected_valid'])
    num_bad_questions = total_n - num_valid_questions

    rb_schema_pct = round((rb_exact_matches / total_n) * 100, 1)
    rb_exec_pct = round((min(rb_execution_acc, num_valid_questions) / num_valid_questions) * 100, 1)
    rb_refusal_pct = round((rb_refusal_acc / num_bad_questions) * 100, 1)

    llm_schema_pct = round((llm_exact_matches / total_n) * 100, 1)
    llm_exec_pct = round((min(llm_execution_acc, num_valid_questions) / num_valid_questions) * 100, 1)
    llm_refusal_pct = round((llm_refusal_acc / num_bad_questions) * 100, 1)

    summary_report = {
        'total_questions': total_n,
        'valid_questions': num_valid_questions,
        'refusal_questions': num_bad_questions,
        'rule_based': {
            'schema_exact_match_pct': rb_schema_pct,
            'execution_accuracy_pct': rb_exec_pct,
            'refusal_accuracy_pct': rb_refusal_pct
        },
        'llm_parser': {
            'provider': provider_name,
            'status': 'run' if llm_key_present else 'mock_run',
            'schema_exact_match_pct': llm_schema_pct,
            'execution_accuracy_pct': llm_exec_pct,
            'refusal_accuracy_pct': llm_refusal_pct
        }
    }

    with open(results_dir / 'eval_results.json', 'w', encoding='utf-8') as f:
        json.dump({'summary': summary_report, 'rule_based_outputs': rb_raw_outputs, 'llm_outputs': llm_raw_outputs}, f, indent=2)

    pct = 'percent'
    print('---------------------------------------------------------------------------------')
    print('Parser Variant               | Schema Exact Match | Exec Accuracy | Refusal Accuracy')
    print('---------------------------------------------------------------------------------')
    print(f'Rule-Based Baseline          | {rb_schema_pct:5.1f}%             | {rb_exec_pct:5.1f}%        | {rb_refusal_pct:5.1f}%')
    print(f'LLM Parser ({provider_name[:17]:17s})| {llm_schema_pct:5.1f}%             | {llm_exec_pct:5.1f}%        | {llm_refusal_pct:5.1f}%')
    print('---------------------------------------------------------------------------------\n')
    print(f'Results saved to {results_dir}')

if __name__ == '__main__':
    run_evaluation()
