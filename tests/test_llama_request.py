import os
import json
import time

from backend.model import llama_request

def load_test_prompts():
    with open(os.path.join(os.path.dirname(__file__), 'prompts/test_single_prompts.json'), encoding='utf-8') as f:
        data = json.load(f)
    return data["prompts"]

def assert_scam_score(expected_scam_score, actual_scam_score, tolerance):
    if abs(expected_scam_score - actual_scam_score) > tolerance:
        raise AssertionError(f"Expected scam score: {expected_scam_score}, but got: {actual_scam_score}. Tolerance: {tolerance}")

def run_llama_tests():
    prompts = load_test_prompts()
    for prompt in prompts:
        start_time = time.time()
        output = llama_request.run_llama_request(prompt["prompt"])
        elapsed = time.time() - start_time
        completionText = json.loads(output["completion_message"]["content"]["text"])

        assert_scam_score(prompt["scam_score"], completionText["scam_score"], 3)

        print(f"{elapsed:.2f} seconds taken for prompt '{prompt['prompt']}'")
        if elapsed > 20:
            print(f"Warning: Slow response for prompt '{prompt['prompt']}' - {elapsed:.2f} seconds")


if __name__ == "__main__":
    run_llama_tests()