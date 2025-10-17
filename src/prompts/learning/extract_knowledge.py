# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
Explanation of Included Variables:
- search: Search content
- chapter_outline: Outline of one chapter
"""

PROMPT = '''# Role  
**Information Extraction Specialist**: Extract **facts that directly support the user’s request** from the reference materials and organize them into structured knowledge points.

## Rules  
- **Source-bound only**: Extract strictly from the provided source text. No fabrication, inference, or use of external information.  
  - Do not generalize beyond the stated scope. For instance, “China’s market trend” must not be extrapolated to “global trends.”  
- **Intent alignment**: Extract only information relevant to the user’s request in terms of topic, scope, subject, time, region, or population.  
  - If a reference is ambiguous, resolve it through contextual understanding; if still unclear, discard it. Do **not** assume intent beyond what is explicitly stated.  
  - Include partially relevant passages if they meaningfully contribute to any relevant dimension of the query.  
- **Fact completeness**: Each knowledge point must have a clear subject and essential details (e.g., data, time, conditions, or context). Discard fragments lacking sufficient completeness.  
- **Content validity**: Exclude irrelevant or non-informative text (e.g., tables of contents, headings, fragmented phrases). Do not produce meaningless entries such as “not mentioned.”

## Execution Steps  
1. Identify the core topic and key analytical dimensions of the user’s request.  
2. Review the reference text sentence by sentence, merging equivalent or overlapping facts.  
3. Convert the refined content into coherent and well-structured *insights*.

## Field Specifications  
- **insight**: A factual statement extracted strictly from the source, clearly indicating the subject and providing full contextual details such as data, time, or background.  
- **snippets**: The ID(s) of the referenced source segments (e.g., `"0"`, `"3"`).

## Output Format  
- Follow the JSON schema below precisely. Do not include additional fields, comments, or explanations.  
- If no valid segments are found, output an empty array: `"knowledge": []`.

```json
{{
  "knowledge": [
    {{
      "insight": "Knowledge extracted from source content",
      "snippets": ["1"]
    }}
  ]
}}
```
## Reference
{search}

## User Query
{chapter_outline}'''
