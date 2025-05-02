import json
from flask import Blueprint, request, jsonify, render_template
import requests
import time

from models import TestCase

compiler = Blueprint('compiler', __name__)

JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com"
HEADERS = {
    "X-RapidAPI-Key": "d289cc1b2dmshea218e2511ffa85p121067jsnbf5c89b32b88",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "Content-Type": "application/json"
}

LANGUAGE_MAP = {
    "python": 71,
    "java": 62,
    "c": 50,
    "cpp": 54
}


@compiler.route('/editor', methods=['GET'])
def code_editor():
    return render_template('code_editor.html')


@compiler.route('/compile', methods=['POST'])
def compile_code():
    """Compile and execute code against test cases using Judge0 API"""
    data = request.json

    print("Received JSON Data:", json.dumps(data, indent=4))

    required_keys = ['code', 'language_id', 'question_id']
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing required fields: 'code', 'language_id', 'question_id'"}), 400

    code = data['code']
    language_id = str(data['language_id'])
    question_id = data['question_id']

    test_cases = TestCase.query.filter_by(question_id=question_id).all()
    if not test_cases:
        return jsonify({"error": "No test cases found for this question."}), 404

    results = []
    passed_all = True

    for test in test_cases:
        stdin_value = (test.input_data or "").strip()
        expected_output = (test.expected_output or "").strip()

        payload = {
            "language_id": language_id,
            "source_code": code,
            "stdin": stdin_value,
        }

        try:

            response = requests.post(f"{JUDGE0_API_URL}/submissions?base64_encoded=false&wait=false",
                                     json=payload, headers=HEADERS, timeout=10)

            if response.status_code != 201:
                return jsonify({"error": "Failed to submit code", "details": response.text}), 500

            token = response.json().get("token")
            if not token:
                return jsonify({"error": "No token received from Judge0", "details": response.json()}), 500

            result_url = f"{JUDGE0_API_URL}/submissions/{token}?base64_encoded=false"
            for _ in range(5):
                time.sleep(1.5)
                result_response = requests.get(result_url, headers=HEADERS, timeout=10)
                result_data = result_response.json()

                if "status" in result_data and result_data["status"].get("id") in [3, 4, 6]:
                    break

            output = (result_data.get("stdout") or "").strip()
            stderr = (result_data.get("stderr") or "").strip()
            compile_output = (result_data.get("compile_output") or "").strip()
            status_description = result_data.get("status", {}).get("description", "Unknown Status")

            final_output = output if output else stderr if stderr else compile_output if compile_output else "[No Output]"

            output_normalized = final_output.strip()
            expected_output_normalized = expected_output.strip()

            test_result = (output_normalized == expected_output_normalized)

            results.append({
                "input": stdin_value,
                "expected": expected_output,
                "output": final_output,
                "status": "Passed" if test_result else "Failed",
                "error": stderr or compile_output if not test_result else None,
                "execution_status": status_description
            })

            if not test_result:
                passed_all = False

        except requests.RequestException as e:
            return jsonify({"error": "Compiler Service Unavailable", "details": str(e)}), 503

    return jsonify({
        "status": "All Test Cases Passed" if passed_all else "Some Test Cases Failed",
        "results": results,
        "raw_output": results[0]["output"] if results else "[No Output]"
    })
