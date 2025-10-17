# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
Explanation of Included Variables:
- knowledge: Relevant knowledge
- chapter_outline: Outline of one chapter
"""

PROMPT = '''You are a professional and detail-oriented information analyst, adept at synthesizing insights from multiple sources and clearly identifying their origins. Based on the following user query and knowledge excerpts, generate an **accurate, well-structured, and source-traceable** response that helps the user grasp the key conclusions.

<chapter_outline>  
{chapter_outline} 
</chapter_outline>

<Known Perspectives and Knowledge>  
{knowledge}  
</Known Perspectives and Knowledge>

<Generation Rules>  
1. The response must remain closely aligned with the user query. Use clear and precise language, avoiding vagueness, redundancy, or circular phrasing.  
2. You may integrate information from multiple excerpts but must not infer or speculate beyond what is explicitly provided.  
3. Organize the response into several paragraphs if needed, each addressing a distinct fact or dimension.  
4. Do not copy or list document contents verbatim. Instead, reorganize, summarize, and refine the language for clarity and cohesion.  
5. Write in a natural, fluent style suitable for end users—avoid overly academic or mechanical phrasing.  
6. Do not mention “document numbers” or “indexes.” Source traceability should appear only through the `quote_ids` field.  

Please produce the final response according to the above requirements.

<Output Format>  
Strictly follow this JSON structure:  
```json
{{
  "answer": "",
  "quote_ids": [""]
}}
```
'''