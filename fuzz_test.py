import requests
from fuzzingbook.Fuzzer import RandomFuzzer

BASE_URL = "http://localhost:5001/api/client/data"
HEADERS = {"Content-Type": "application/json"}

# Log in to get session (for testing, actual login required first)
def get_auth_session():
    session = requests.Session()
    login_data = {"username": "testuser", "password": "Test@123456"}
    session.post("http://localhost:5001/login", data=login_data)
    return session

def fuzz_endpoint():
    session = get_auth_session()
    fuzzer = RandomFuzzer(min_length=5, max_length=50)
    vulnerabilities = []

    print("Starting fuzz testing...")
    for i in range(100):
        payload = fuzzer.fuzz()
        try:
            response = session.post(
                BASE_URL,
                json={"data": payload},
                headers=HEADERS,
                timeout=5
            )
            # Check for unexpected status codes
            if response.status_code not in [200, 400]:
                vulnerabilities.append({
                    "payload": payload,
                    "status_code": response.status_code,
                    "response": response.text
                })
        except Exception as e:
            vulnerabilities.append({
                "payload": payload,
                "error": str(e)
            })

    # Output results
    if vulnerabilities:
        print(f"Found {len(vulnerabilities)} potential vulnerabilities:")
        for v in vulnerabilities:
            print(f"- Payload: {v['payload']} | Error: {v.get('status_code') or v.get('error')}")
        exit(1)
    else:
        print("Fuzz testing found no vulnerabilities")

if __name__ == "__main__":
    fuzz_endpoint()