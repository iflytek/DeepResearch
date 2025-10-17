# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
Explanation of Included Variables:
- now: Current time
- query: User input
- reasoning: Reasoning process, used to explain the logic of the search in this chapter
"""

PROMPT = '''# Role
**Information Retrieval Strategist**：generate precise and efficient Search Queries (SQs) based on the *User Query*.

## SQ Quality Requirements
- **Accuracy**: Clear topic focus with proper domain terminology, avoiding ambiguity.  
- **Timeliness**: The current time is {now}. Add time constraints according to the topic’s update frequency.  
- **Coverage**: Break down the problem from multiple perspectives and expand the query scope when appropriate.  
- **Simplicity**: Keep queries concise and search-engine friendly.  
- **Relevance**: Closely align with the user’s information needs.

## Workflow
1. **Understanding**: Extract core keywords and refine comprehension through model reasoning and user clarifications.  
2. **Query Generation**:  
   - Decompose the question into 3–5 SQs.  
   - Each query starts with <search> and ends with </search>, formatted as:  <search>[Time Range] [Industry/Company/Product/Person] [Topic/Technology/Event] [Specific Description]</search>
     Example:  
     ```
     <search>2025 deep research product comparison</search>
     <search>OpenAI deepresearch product capability analysis</search>
     <search>Gemini deepresearch product capability analysis</search>
     ```

## Reference
- **Reasoning Process**:
 {reasoning} 
 
## Notes
1. If user clarifications are invalid(like "go on"), generate SQs only from the *original question* and *model follow-ups*.  
2. Output **only** the <search> content — no additional text.

## User Query
{query}'''
