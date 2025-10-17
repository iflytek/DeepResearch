# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
Explanation of Included Variables:
- now: Current time
- chapter_outline: Outline of one chapter
"""

PROMPT = '''You are an expert in query evaluation. Using the following definitions and rules, assess whether each category applies to the user’s query (true or false).

Current time: {now}

<evaluation_types>
freshness – Whether the query requires the most up-to-date information.
plurality – Whether the query requires multiple examples, methods, or items.
completeness – Whether the query requires comprehensive coverage of multiple explicitly mentioned elements.
</evaluation_types>

<rules>
1. If the query involves specific years, stages, time periods, cycles, or event progress, it requires a freshness check, emphasizing “specific timeliness” rather than just “latest.”
2. If the query includes hints such as “list,” “what are,” “multiple,” or requires multiple methods or examples as output, it requires plurality.
3. If the query explicitly lists multiple named elements and requires an answer for each, it requires completeness.
</rules>

<examples>
<example-1>
"query": "Who invented calculus? What were the respective contributions of Newton and Leibniz?",
"output": {{
  "freshness": false,
  "plurality": false,
  "completeness": true
}}
</example-1>

<example-2>
"query": "What are the main differences between Romanticism and Realism in 19th-century literature?",
"output": {{
  "freshness": false,
  "plurality": false,
  "completeness": true
}}
</example-2>

<example-3>
"query": "What are the current mortgage rates at Bank of America, Wells Fargo, and JPMorgan Chase in the United States?",
"output": {{
  "freshness": true,
  "plurality": false,
  "completeness": true
}}
</example-3>

Following the above definitions, rules, and examples, strictly output the result in the following JSON format (no explanation needed):
{{
  "freshness": true/false,
  "plurality": true/false,
  "completeness": true/false
}}

## User query:
{chapter_outline}
'''