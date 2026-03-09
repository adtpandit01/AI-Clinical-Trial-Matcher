import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

def fetch_trials_from_api(condition: str, page_size: int = 5):

    params = {
        "query.term": condition,
        "pageSize": page_size
    }

    response = requests.get(BASE_URL, params=params)

    print("STATUS CODE:", response.status_code)
    print("RESPONSE TEXT:", response.text[:500])  # print first 500 chars

    if response.status_code != 200:
        raise Exception("Failed to fetch trials from API")

    data = response.json()

    trials = []

    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})

        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        eligibility = protocol.get("eligibilityModule", {})

        trials.append({
            "nct_id": identification.get("nctId"),
            "title": identification.get("briefTitle"),
            "condition": ", ".join(protocol.get("conditionsModule", {}).get("conditions", [])),
            "phase": status_module.get("phase"),
            "eligibility_text": eligibility.get("eligibilityCriteria")
        })

    return trials