"""
Qualitative Coding with Google Gemini API
Adapted from "Scalable Qualitative Coding with LLMs" by Zackary Okun Dunivin

This script replicates the original analysis using Gemini instead of GPT.
"""

import pandas as pd
import json
import os
import re
import glob
import time
import google.generativeai as genai
from typing import List, Dict

# ============================================================================
# CONFIGURATION
# ============================================================================

# API key will be set when provided by user
GEMINI_API_KEY = None

# Code definitions (same as original)
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

# ============================================================================
# PROMPT GENERATION FUNCTIONS
# ============================================================================

def get_code_definitions(codes, fields=["title", "category", "definition"]):
    """Generate code definitions text from code list."""
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


def generate_full_codebook_prompt(with_justification=True):
    """Generate prompt for full codebook approach."""
    task_description_preface = """You are tasked with applying qualitative codes to articles, book reviews, and opinion pieces referencing W.E.B. Du Bois. The purpose of this task is to track how Du Bois is represented in news media over time. There are 3 categories of code and 9 codes in total. You should apply every code you identify within a passage. Most passages will only relate to a few codes and it is unlikely that you will encounter more than 5 in a single passage. The categories and codes are as follows:

Characterization of Du Bois (2 codes)
1. Scholar
2. Activist

General Themes (3 codes)
1. Monumental Memorialization
2. Mention of Scholarly Work
3. Social/Political Advocacy

Canonization Processes (4 codes)
1. Coalition Building
2. Out of the Mouth of Academics
3. Out of the Mouth of Activists
4. Collective Synecdoche

Below I will explain how to apply each code:
"""

    code_definitions = get_code_definitions(codes_full)
    instructions_zero_shot = """I will give you a passage and ask you to return the correct codes to me. """

    if with_justification:
        formatting = """When you evaluate the passage, provide a 1 sentence justification of why you did or did not apply each code. You can format like this:

After you list all codes and justifications, list all applied codes in the following fashion:

1. **Characterization of Du Bois**:
   - Scholar: Applicable [justification here].
   - Activist: Not directly applicable [justification here].

2. **General Themes**:
    - Monumental Memorialization: Not applicable [justification here].
    - Social/Political Advocacy: Applicable [justification here].

**Codes Applied**:
- Scholar
- Social/Political Advocacy

Do not write anything in your reply after listing the "Codes Applied:" """
    else:
        formatting = """

After analyzing the passage, list all applied codes in the following fashion:

**Codes Applied**:
- Activist
- Monumental Memorialization
- Social/Political Advocacy
- Out of the Mouths of Academics

Do not write anything in your reply before listing the "Codes Applied"

Do not write anything in your reply after listing the "Codes Applied:" """

    return '\n'.join([task_description_preface, code_definitions, instructions_zero_shot, formatting])


def generate_prompt_per_code(code, with_justification=True):
    """Generate prompt for per-code approach."""
    task_description_preface_per_code = """You are tasked with applying qualitative codes to articles, book reviews, and opinion pieces referencing W.E.B. Du Bois. The purpose of this task is to track how Du Bois is represented in news media over time.

Below I will explain how to apply the code:

"""

    instructions_per_code = """I will give you a passage and ask you to return the correct codes to me. """

    if with_justification:
        formatting = f"""When you evaluate the passage, provide a justification of why you did or did not apply the code.

Then list the code in the following fashion if you applied the code:

**Justification:** [insert 2-3 sentence reasoning for applying the code here]

**Codes Applied:**
- {code['title']}

Otherwise you can format it this:

**Justification:** [insert 2-3 sentence reasoning for not applying the code here]

**Codes Applied:**
    - None

Do not write anything in your reply after listing the "Codes Applied:"
"""
    else:
        formatting = f"""After analyzing the passage, list the code in the following fashion if you applied the code:

**Codes Applied:**
- {code['title']}

Otherwise you can format it like this:

**Codes Applied:**
    - None

Do not write anything in your reply before listing the "Codes Applied:"

Do not write anything in your reply after listing the "Codes Applied:"
"""

    prompt = task_description_preface_per_code + get_code_definitions([code], fields=["title", "definition"]) + '\n' + instructions_per_code + formatting

    return prompt


# ============================================================================
# GEMINI API FUNCTIONS
# ============================================================================

def initialize_gemini(api_key):
    """Initialize Gemini API with the provided key."""
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key
    genai.configure(api_key=api_key)
    print("✓ Gemini API initialized successfully")


def make_gemini_call(prompt, message, model_name="gemini-2.5-flash-lite", temperature=0.0, top_p=1.0, max_retries=3):
    """Make a single Gemini API call with retry logic."""

    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "max_output_tokens": 8192,
    }

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )

    # Combine system prompt and user message
    full_prompt = f"{prompt}\n\nPassage to analyze:\n{message}"

    for attempt in range(max_retries):
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise


def make_and_save_gemini_calls(prompt, messages, path, temperature=0, top_p=1, model="gemini-2.5-flash-lite"):
    """Make Gemini API calls and save responses."""

    if not os.path.exists(path):
        os.makedirs(path)

    indices = messages.index.tolist()
    all_messages_and_replies = []

    total = len(indices)
    completed = 0
    skipped = 0

    for msg in messages:
        i = indices.pop(0)

        # Check if we have already retrieved this call
        if os.path.exists(f"{path}/message_{i}.txt"):
            skipped += 1
            continue

        try:
            print(f"  Processing message {i} ({completed + 1}/{total})...")
            reply = make_gemini_call(prompt, msg, model_name=model, temperature=temperature, top_p=top_p)

            # Add to conversation history
            all_messages_and_replies.append({"role": "user", "content": msg})
            all_messages_and_replies.append({"role": "assistant", "content": reply})

            # Save each message and reply as its own text file
            with open(f"{path}/message_{i}.txt", "w") as message_file:
                message_file.write(f"User: {msg}\n")
                message_file.write(f"Assistant: {reply}\n")

            completed += 1

            # Rate limiting: Free tier limit is 15 requests per minute
            # Need 4+ seconds between requests to stay under limit
            time.sleep(4.5)

        except Exception as e:
            print(f"  ✗ Error processing message {i}: {str(e)}")
            continue

    # Write all messages and replies
    with open(f"{path}/all_messages.json", "w") as json_file:
        json.dump(all_messages_and_replies, json_file, indent=4)

    print(f"  Completed: {completed}, Skipped: {skipped}, Total: {total}")


def code_to_path(code):
    """Convert code name to valid path name."""
    code = code.lower()
    code = re.sub(r'[^a-zA-Z0-9]+', '-', code)
    return code


# ============================================================================
# MAIN CODING FUNCTIONS
# ============================================================================

def run_full_codebook_coding(model="gemini-2.5-flash-lite", temperature=0, top_p=1, with_justification=True):
    """Run full codebook coding approach."""
    print("\n" + "=" * 80)
    print(f"FULL CODEBOOK CODING (with_justification={with_justification})")
    print("=" * 80)

    # Load passages
    passages_path = "data/raw/passages.csv"
    coded_articles = pd.read_csv(passages_path)

    # Test set indices
    passages_include = range(9, 120)
    messages = coded_articles.loc[coded_articles.index.isin(passages_include), 'passage']

    # Generate prompt
    prompt = generate_full_codebook_prompt(with_justification=with_justification)

    # Determine condition name
    just_str = 'with-justification' if with_justification else 'without-justification'
    condition = f'full-codebook-{just_str}'

    # Create output path
    path = f'results/raw/output_gemini/full-codebook_{just_str}_t={temperature}_top_p={top_p}_model=gemini'

    # Save parameters
    params = {
        'prompt': prompt,
        'condition': condition,
        'temperature': temperature,
        'top_p': top_p,
        'model': model,
        'codes': [code['title'] for code in codes_full],
        'with_justification': with_justification
    }

    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path}/params.json', 'w') as f:
        json.dump(params, f, indent=4)

    # Make API calls
    print(f"\nMaking Gemini API calls for {len(messages)} passages...")
    make_and_save_gemini_calls(prompt, messages, path, temperature=temperature, top_p=top_p, model=model)

    print(f"✓ Completed full codebook coding")
    return path


def run_per_code_coding(model="gemini-2.5-flash-lite", temperature=0, top_p=1, with_justification=True):
    """Run per-code coding approach."""
    print("\n" + "=" * 80)
    print(f"PER-CODE CODING (with_justification={with_justification})")
    print("=" * 80)

    # Load passages
    passages_path = "data/raw/passages.csv"
    coded_articles = pd.read_csv(passages_path)

    # Test set indices
    passages_include = range(9, 120)
    messages = coded_articles.loc[coded_articles.index.isin(passages_include), 'passage']

    # Determine condition name
    just_str = 'with-justification' if with_justification else 'without-justification'
    base_path = f'results/raw/output_gemini/per-code-{just_str}_t={temperature}_top_p={top_p}_model=gemini'

    # Individual calls per code
    for code in codes_full:
        code_title = code_to_path(code['title'])
        code_path = f'{base_path}/{code_title}'

        print(f"\nProcessing code: {code['title']}")

        if not os.path.exists(code_path):
            os.makedirs(code_path)

        prompt = generate_prompt_per_code(code, with_justification=with_justification)
        make_and_save_gemini_calls(prompt, messages, code_path, temperature=temperature, top_p=top_p, model=model)

    # Save parameters
    params = {
        'temperature': temperature,
        'top_p': top_p,
        'model': model,
        'with_justification': with_justification,
        'codes': [code['title'] for code in codes_full]
    }

    with open(f'{base_path}/params.json', 'w') as f:
        json.dump(params, f, indent=4)

    print(f"✓ Completed per-code coding")
    return base_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(api_key, conditions_to_run='all'):
    """
    Main function to run Gemini coding.

    Args:
        api_key: Gemini API key
        conditions_to_run: 'all', 'full-only', 'per-code-only', or list of specific conditions
    """

    print("=" * 80)
    print("GEMINI QUALITATIVE CODING WORKFLOW")
    print("=" * 80)

    # Initialize Gemini
    initialize_gemini(api_key)

    # Model parameters
    model = "gemini-2.5-flash-lite"
    temperature = 0
    top_p = 1

    paths_created = []

    if conditions_to_run == 'all' or conditions_to_run == 'per-code-only':
        # Per-code with justification
        path = run_per_code_coding(model=model, temperature=temperature, top_p=top_p, with_justification=True)
        paths_created.append(path)

        # Per-code without justification
        path = run_per_code_coding(model=model, temperature=temperature, top_p=top_p, with_justification=False)
        paths_created.append(path)

    if conditions_to_run == 'all' or conditions_to_run == 'full-only':
        # Full codebook with justification
        path = run_full_codebook_coding(model=model, temperature=temperature, top_p=top_p, with_justification=True)
        paths_created.append(path)

        # Full codebook without justification
        path = run_full_codebook_coding(model=model, temperature=temperature, top_p=top_p, with_justification=False)
        paths_created.append(path)

    print("\n" + "=" * 80)
    print("CODING COMPLETE!")
    print("=" * 80)
    print(f"\nGenerated {len(paths_created)} condition outputs:")
    for path in paths_created:
        print(f"  - {path}")

    return paths_created


if __name__ == "__main__":
    print("\nThis script requires a Gemini API key to run.")
    print("Please provide your API key when calling main(api_key)")
    print("\nExample usage:")
    print("  from gemini_coding_workflow import main, initialize_gemini")
    print("  main('YOUR_API_KEY_HERE')")
