# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License

"""
Explanation of Included Variables:
- above: Context summary
- description: The positioning or role of the chart in this report
- reference: Reference knowledge
"""

SYSTEM_PROMPT = '''Read the following reference materials carefully and generate an ECharts graph based on the title and description:
**Automatically detect the user's primary language and ensure all responses are in that language.**

## Output Content
### Statistical Chart
- Please generate the JSON configuration required for drawing an ECharts graph based on the title and description. Ensure that the data in the chart is strictly derived from the reference materials; do not fabricate data. You may attempt to correctly label key nodes in the graph.
- You will use the following tool
**Tool**
<echarts> Generate an HTML chart page based on the ECharts JSON configuration
	<input_schema>ECharts JSON configuration object</input_schema>
</echarts>

**Tool Call Details**
	1. Please use the above tool to generate an ECharts graph based on the title and description. Write its name and parameters in the XML format specified above.
	2. All parameters are mandatory unless otherwise stated.
	3. You only need to call the above tool.
	4. You only need to provide the parameters required for the tool call; no explanatory notes are needed.'''

PROMPT = '''## Chart Description
{description}

## Previous Context
{above}

## Reference Materials
{reference}'''
