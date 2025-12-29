"""
Qualitative Coding with Qwen via OpenRouter API
Parallel comparison to GPT-4, Gemini, and Llama
"""

import pandas as pd
import json
import os
import re
import time
from openai import OpenAI
from typing import List, Dict

# Will be set when API token provided
OPENROUTER_API_KEY = None

# Reuse code definitions
codes_full = [
    {
        'title': 'Scholar',
        'category': 'Characterization',
        'definition': 'Applies when Du Bois is described as a scholar or intellectual, especially in connection to Black politics, racial identity, or social theory. When Du Bois is invoked through his ideas on social theory, he should be classified as a scholar, not an activist, unless it is call to action, related to his organizing, or other non-scholarly political activity. Do not apply when Du Bois is merely the focus the context of historical and academic study or his scholarship is only implied by loose connections to other scholars.',
        'examples': '"900-page anthology of black history and culture and a call to "condemn racial discrimination and appreciate the ... accomplishments of a long-suffering people." Its 150 contributors included Theodore Dreiser, Zora Neale Hurston, W.E.B. Du Bois and Langston Hughes."',
    },
    {
        "title": "Activist",
        "category": "Characterization",
        "definition": 'Apply this code when Du Bois is explicitly called an "activist" or "leader", or when his political or social activism is either explicitly noted or clearly implied through context. Examples include being mentioned in the context of leadership, activism, developing activist organizations, giving public speeches, participating in meetings with politicians and organizers, running for office, or promoting a candidate, organization, or initiative.',
        "examples": "Liberia in the antebellum era to W.E.B. Du Bois and the radical political refugees who gathered in Ghana in the 1950s and 1960s - sought freedom and identity in trans-Atlantic...",
    },
    {
        "title": "Monumental Memorialization",
        "category": "General Themes",
        "definition": "When an enduring cultural object is named after Du Bois. Such objects include prizes/awards, named professorships, buildings or rooms, geographical features, institutes, schools, or activist organizations. Do not apply when Du Bois is mentioned in the title of a book or theater production.",
        "examples": '"The Du Bois Center for African American Studies."\n"W. E. B. Du Bois High School."',
    },
    {
        "title": "Mention of Scholarly Work",
        "category": "General Themes",
        'definition': "Apply this code when academic works or major theoretical concepts by W.E.B. Du Bois are mentioned or quoted. This includes explicit naming or direct quotations of his writings and references to his key academic ideas, even if unnamed, provided they are clearly attributed to him. Only use when a quote comes from a scholarly work; use context to determine whether a quote comes from a scholarly work, such as a history or social theory, or some other piece, such as a letter or speech. Avoid using this code for general references to Du Bois's influence, body of writings, or activities outside of his scholarly work. Do not apply it when discussing others' work, unless Du Bois's scholarly concepts or writings are explicitly and centrally mentioned.",
        "examples": "This goes beyond W.E.B. Du Bois's notion of 'double consciousness.'",
    },
    {
        "title": "Social/Political Advocacy",
        "category": "General Themes",
        "definition": "This code applies when a passage mentions or implies any form of social or political activism, advocacy, critique, or discourse, including discussions about current or historical social problems. This includes not only direct activism of Du Bois and others, but also the framing and challenging of social norms, historical narratives, and racial or cultural identities. Apply this code when Du Bois's work, persona, or ideas are invoked in discussions that critically engage with Black identity, positionality, or broader systemic circumstances of Black people. Adjacency to other activists such as inclusion in a list, is insufficient; advocacy must be explicitly mentioned in the passage.",
        "examples": "Between me and the other world, there is ever an unasked question, W.E.B. Du Bois famously said back in 1897: 'How does it feel to be a problem?' White people are generally allowed to have problems, and they've historically been granted the power to define and respond to them. But people of color — in this 'land of the free'",
    },
    {
        "title": "Coalition Building",
        "category": "Canonization",
        "definition": "Du Bois is described as an agent establishing his reputation through organizational and institutional sponsorship.",
        "examples": "W.E.B. Du Bois, professor of Sociology and Economics at the University of Georgia\nDu Bois organized five meetings of the Pan African National Congress.\nW.E.B. Du Bois was chairman of the Peace Information Center.",
    },
    {
        "title": "Out of the Mouth of Academics",
        "category": "Canonization",
        "definition": "Apply this code when a specific member of an academic organization is engaging with Du Bois's work or Du Bois as representing a concept. Apply also when an activist organization has named itself or a subdivision of itself after Du Bois, such as an institute or named professorship. It is not sufficient to use this code when Du Bois is described as a member of an academic organization. This code represents when a member of an academic organization discusses Du Bois. It is not sufficient to pressume that the entity discussing or promoting Du Bois is academic.",
        "examples": "Black leaders such as Charles V. Hamilton, professor of political science at Columbia University, have been expressing concern about placing Negro children in 'educationally racist' white classrooms, an ap prehension expressed by W. E. B. Du Bois in the 1930's.",
    },
    {
        "title": "Out of the Mouth of Activists",
        "category": "Canonization",
        "definition": "Apply this code when an individual described as a leader, activist, or politician, or as member of a specific political or activist organization organization (e.g., political parties, the NAACP, the Black church, Black Lives Matter) references or draws upon W.E.B. Du Bois's work or legacy. This includes instances where the person's role as a leader, activist, or politician is implied through their actions or affiliations, even if not explicitly stated. The code also applies when governments, political parties, or activist organizations connect their agenda to Du Bois, such as commemorating Du Bois by naming initiatives (like foundations or prizes) after him. Do not apply Du Bois is mentioned as a member of an organization, unless a representative organization is referencing Du Bois' membership to connect their agenda to Du Bois.",
        "examples": "Du Bois later sold the house because he could not afford to keep it up, and the property was eventually turned over to the Du Bois Foundation, which dedicated it as a memorial park in 1969.\nChairman of the state NAACP Howard Roberts reflected on Du Bois legacy.",
    },
    {
        "title": "Collective Synecdoche",
        "category": "Canonization",
        "definition": "Mentioned with other famous intellectuals, activists, or public figures in order to represent some facet of a culture, era, or ideology. Examples include representing race scholarship, civil rights activism, left political leaders, Black excellence, and 20th century political commentators.",
        "examples": "…and the former home of luminaries like Jackie Robinson, W.E.B. Du Bois and Ella Fitzgerald, is now a historic district, New York City's 102nd.\nHe recalls that he read James Baldwin, Ralph Ellison, Langston Hughes, Richard Wright and W.E.B. Du Bois when he was an adolescent in an effort to come to terms with his racial identity.",
    },
]


def get_code_definitions(codes, fields=["title", "category", "definition"]):
    """Generate code definitions text."""
    string = ''
    field_label = {
        "title": "Title",
        "category": "Category",
        "definition": "Definition",
        "examples": "Example(s)",
    }
    for code in codes:
        for field in fields:
            if field in code and code[field]:
                string += '%s: %s\n' % (field_label[field], code[field])
        string += '\n'
    return string


def generate_prompt_per_code(code, with_justification=True):
    """Generate prompt for per-code approach."""
    task_description = """You are tasked with applying qualitative codes to articles, book reviews, and opinion pieces referencing W.E.B. Du Bois. The purpose of this task is to track how Du Bois is represented in news media over time.

Below I will explain how to apply the code:

"""

    instructions = """I will give you a passage and ask you to return the correct codes to me. """

    if with_justification:
        formatting = f"""When you evaluate the passage, provide a justification of why you did or did not apply the code.

Then list the code in the following fashion if you applied the code:

**Justification:** [insert 2-3 sentence reasoning for applying the code here]

**Codes Applied:**
- {code['title']}

Otherwise format it this way:

**Justification:** [insert 2-3 sentence reasoning for not applying the code here]

**Codes Applied:**
    - None

Do not write anything in your reply after listing the "Codes Applied:"
"""
    else:
        formatting = f"""After analyzing the passage, list the code in the following fashion if you applied the code:

**Codes Applied:**
- {code['title']}

Otherwise format it like this:

**Codes Applied:**
    - None

Do not write anything before or after listing the "Codes Applied:"
"""

    prompt = task_description + get_code_definitions([code], fields=["title", "definition"]) + '\n' + instructions + formatting
    return prompt


def initialize_openrouter(api_key):
    """Initialize OpenRouter API."""
    global OPENROUTER_API_KEY
    OPENROUTER_API_KEY = api_key
    print("✓ OpenRouter API initialized")


def make_openrouter_call(prompt, message, model="qwen/qwen-2.5-72b-instruct", temperature=0.0, max_retries=3):
    """Make a single OpenRouter API call."""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Passage to analyze:\n{message}"}
                ],
                temperature=temperature,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def make_and_save_openrouter_calls(prompt, messages, path, model="qwen/qwen-2.5-72b-instruct", temperature=0):
    """Make OpenRouter API calls and save responses."""

    if not os.path.exists(path):
        os.makedirs(path)

    indices = messages.index.tolist()
    all_messages_and_replies = []

    total = len(indices)
    completed = 0
    skipped = 0

    for msg in messages:
        i = indices.pop(0)

        # Check if already completed
        if os.path.exists(f"{path}/message_{i}.txt"):
            skipped += 1
            continue

        try:
            print(f"  Processing message {i} ({completed + 1}/{total})...")
            reply = make_openrouter_call(prompt, msg, model=model, temperature=temperature)

            all_messages_and_replies.append({"role": "user", "content": msg})
            all_messages_and_replies.append({"role": "assistant", "content": reply})

            with open(f"{path}/message_{i}.txt", "w") as f:
                f.write(f"User: {msg}\n")
                f.write(f"Assistant: {reply}\n")

            completed += 1
            time.sleep(0.1)  # Small delay to avoid rate limits

        except Exception as e:
            print(f"  ✗ Error processing message {i}: {str(e)}")
            continue

    with open(f"{path}/all_messages.json", "w") as f:
        json.dump(all_messages_and_replies, f, indent=4)

    print(f"  Completed: {completed}, Skipped: {skipped}, Total: {total}")


def code_to_path(code):
    """Convert code name to path."""
    code = code.lower()
    code = re.sub(r'[^a-zA-Z0-9]+', '-', code)
    return code


def run_per_code_qwen(api_key, model="qwen/qwen-2.5-72b-instruct", with_justification=True):
    """Run per-code coding with Qwen via OpenRouter."""

    print("\n" + "=" * 80)
    print(f"QWEN PER-CODE CODING (with_justification={with_justification})")
    print(f"Model: {model}")
    print("=" * 80)

    initialize_openrouter(api_key)

    # Load passages
    passages = pd.read_csv("data/raw/passages.csv")
    passages_include = range(9, 120)
    messages = passages.loc[passages.index.isin(passages_include), 'passage']

    just_str = 'with-justification' if with_justification else 'without-justification'
    base_path = f'results/raw/output_qwen/per-code-{just_str}_t=0_model=qwen-2.5-72b'

    # Process each code
    for code in codes_full:
        code_title = code_to_path(code['title'])
        code_path = f'{base_path}/{code_title}'

        print(f"\nProcessing code: {code['title']}")

        if not os.path.exists(code_path):
            os.makedirs(code_path)

        prompt = generate_prompt_per_code(code, with_justification=with_justification)
        make_and_save_openrouter_calls(prompt, messages, code_path, model=model, temperature=0)

    # Save parameters
    params = {
        'model': model,
        'temperature': 0,
        'with_justification': with_justification,
        'codes': [code['title'] for code in codes_full]
    }

    with open(f'{base_path}/params.json', 'w') as f:
        json.dump(params, f, indent=4)

    print(f"\n✓ Completed Qwen per-code coding")
    return base_path


if __name__ == "__main__":
    print("\nQwen (via OpenRouter) Coding Workflow")
    print("Requires OpenRouter API key (free at https://openrouter.ai)")
    print("\nUsage:")
    print("  from openrouter_coding_workflow import run_per_code_qwen")
    print("  run_per_code_qwen('YOUR_OPENROUTER_API_KEY')")
