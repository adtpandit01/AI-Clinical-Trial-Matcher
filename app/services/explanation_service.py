from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()


# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create client
client = Groq(api_key=GROQ_API_KEY)


def generate_explanation(patient_text, trial_title, trial_condition, eligibility_text):

    prompt = f"""
You are a medical AI assistant helping match patients to clinical trials.

PATIENT:
{patient_text}

CLINICAL TRIAL TITLE:
{trial_title}

CONDITION:
{trial_condition}

ELIGIBILITY CRITERIA (summary):
{eligibility_text[:600]}

Explain in ONE short sentence why this trial may match the patient.
Only use the information above. Do not invent details.
"""

    try:

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=60
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:

        print("GROQ ERROR:", e)

        return "This trial may match based on condition similarity."