# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

from typing import Dict, Tuple, List, Optional
from enum import StrEnum


class AnalysisTag(StrEnum):
    """Enumeration class for analysis type tags, uniformly managing all valid tags to avoid magic strings"""
    INDUSTRY = "Industry Research"
    COMPANY = "Company Research"
    COMPREHENSIVE = "Comprehensive Analysis"

    @classmethod
    def get_all_tags(cls) -> List[str]:
        """Get a list of strings for all tags, used for quick verification/traversal"""
        return [tag.value for tag in cls]

    @classmethod
    def is_valid_tag(cls, tag: str) -> bool:
        """Check if the given tag is valid"""
        return tag in cls.get_all_tags()


# Analysis data structure: (analysis logic steps: str, detailed analysis content: str)
AnalysisData = Tuple[str, str]
# Analysis dictionary: Key is the value of AnalysisTag enumeration, value is AnalysisData
AnalysisDict = Dict[str, AnalysisData]


def init_analysis_data() -> AnalysisDict:
    """Initialize the analysis data dictionary to centrally manage configurations for all analysis types"""
    return {
        AnalysisTag.INDUSTRY.value: (
            "Define the industry scope and growth drivers → Quantify current market status and competitive landscape → Deconstruct representative business models and strategic advantages → Assess future trends, opportunities, and risks",
            """1. Industry Overview  
Define the industry scope and core characteristics. Apply the **PEST** framework to outline the development background, emphasizing key factors such as policy environment, economic drivers, evolving social demand, and technological innovation. Assess the **industry life cycle stage** to determine maturity and highlight major growth drivers.
2. Market Landscape  
Analyze the latest available data on **market size, growth rate, and user base**, along with key **sub-segment dynamics**. Use frameworks such as **Porter’s Five Forces** and **SWOT** analysis. For technology-driven sectors, include additional insights into **core technologies and innovation trends**.
3. Leading Players Analysis  
Identify **top incumbents and emerging challengers** in the industry. Compare their **market share, strategic positioning, business models, marketing approaches, and user perception**, with emphasis on **core competitive advantages** and differentiation factors.
4. Industry Outlook  
Integrate insights from policy, technology, consumer, and capital perspectives, combined with expert opinions and industry reports, to forecast the next **3–5 years** of development. Highlight **market growth potential, technological evolution, and emerging business models**, providing forward-looking guidance for strategic planning."""
        ),
        AnalysisTag.COMPANY.value: (
            "Research the company background → Analyze industry landscape and emerging trends → Consolidate financial performance and key indicators → Identify core business segments and growth drivers → Integrate market dynamics to highlight potential risks",
            """## 1. Company Profile
Introduce the company’s **basic information**, including name, ownership structure, and key milestones. Summarize its **core businesses**, product portfolio, business model, and market positioning.
2. Industry and Market Environment  
- **Industry Analysis:** Summarize the current state and scale of the industry within its **upstream and downstream value chain**. Assess the development stage based on technology, policy, and consumer trends.  
- **Market Analysis:** Evaluate **market drivers** (technology, policy, consumer demand, macroeconomic environment), geographic presence, **market share, sales performance, and growth potential**.  
- **Competitive Landscape:** Compare major competitors by **market share, product features, technological barriers, R&D investment, and customer base**, identifying relative strengths and weaknesses.
3. Business Model and Financial Quality 
- **Business Model:** Examine the company’s **core revenue drivers and diversified income streams** (product sales, advertising, service fees, etc.). Analyze **cost structure** (fixed vs. variable costs, R&D and marketing expenses) and profitability model.  
- **Financial Quality:** Present key **financial indicators over the past 3–5 years**, including profitability (revenue, net income, ROE/ROA), solvency, operating efficiency, growth metrics (revenue and profit growth rates), and cash flow health.
4. Business Segments and Growth Potential  
Assess the **market performance and competitive advantages** of core business lines. Identify **current and emerging profit drivers**, and evaluate **future growth prospects** in line with corporate strategy.
5. Investment Value and Risk Assessment  
Combine industry outlook and market dynamics to derive a **reasonable valuation and investment view**. Highlight potential risks related to **policy changes, intensifying competition, or business transformation**."""
        ),
        AnalysisTag.COMPREHENSIVE.value: (
            "Identify user intent → Define problem type and analytical dimensions → Fill knowledge gaps and set priorities → Build an overall analytical framework and actionable plan → Design content aligned with real needs",
            """| Analysis Type | Writing Approach (**Choose Based on Analytical Intent**) | Usage Notes |
|--------------------|-----------------------------------------------------------|-----------------|
| **Status Diagnosis** | 1. Problem Definition & Current Overview: Use key indicators to outline the present situation, define analytical boundaries, and clarify the core issue.<br>2. Development Path Review: Trace major shifts and milestone events that shaped the current state.<br>3. Multi-Level Cause Analysis: Build a structured causal framework to explain the underlying drivers across different layers.<br>4. Empirical Validation: Use representative cases to substantiate causal logic and enhance credibility.<br>5. Trend Insights & Strategic Suggestions: Derive future trends from causal analysis and provide actionable strategic guidance. | When the background is already known, the development review can be omitted. If the focus is on solutions, start directly with cause analysis and recommendations. |
| **Evaluation & Forecasting** | 1. Framework Establishment: Define the objectives, scope, and evaluation criteria to form a baseline for analysis.<br>2. Comprehensive Assessment: Develop a multidimensional indicator system and perform comparative analysis to reach objective conclusions.<br>3. Scenario Modeling & Forecasting: Construct alternative development paths based on key variables and assess uncertainties.<br>4. Decision Recommendations: Translate predictive results into prioritized and actionable decision plans. | If only comparative findings are required, skip the framework setup. If forecasting is the main goal, begin with scenario modeling. |
| **Planning & Design** | 1. Goal Setting & Current Review: Clarify core goals and value orientation while taking stock of available resources.<br>2. Gap Identification & Needs Analysis: Compare current conditions against target requirements to pinpoint improvement priorities.<br>3. Task Breakdown & Implementation Planning: Translate objectives into executable tasks and outline the roadmap for delivery.<br>4. Risk Management & Safeguards: Identify major risks and design mitigation measures and contingency plans.<br>5. Monitoring & Iterative Optimization: Establish monitoring mechanisms and ensure continuous refinement. | If objectives are already clear, start with gap analysis. For execution-oriented work, begin with task planning. |
| **Information Mapping** | 1. Scope Definition & Criteria Setting: Specify collection boundaries, screening criteria, and presentation expectations.<br>2. Classification & Highlighting: Structure information by logical dimensions, emphasizing key facts and insights.<br>3. Supplementary Notes & Sources: Provide contextual explanations and cite reliable sources. | For basic compilations, classification may be omitted. For practical use, emphasize structured and navigable presentation. |
| **Comprehensive (Fallback) Analysis** | 1. Background & Core Proposition: Define the main issue and the intended outcome.<br>2. Evidence & Validation: Substantiate claims with data, theory, and case evidence.<br>3. Multi-Angle Argumentation: Examine the topic through multiple perspectives to build a cohesive line of reasoning.<br>4. Implementation Path & Risk Management: Present feasible action steps and address potential risks with countermeasures.<br>5. Conclusion & Actionable Insights: Synthesize findings into clear, practical recommendations. | The entry point can vary: start from the proposition for conclusion-driven work, from implementation for execution-focused work, or from argumentation for analysis-heavy studies. |""")}


def get_analysis_data(tag: str, analysis_dict: Optional[AnalysisDict] = None) -> AnalysisData:
    """
    Retrieve analysis data by tag.

    Args:
        tag: The analysis tag to retrieve data for
        analysis_dict: Optional analysis dictionary, if not provided, will initialize a new one

    Returns:
        AnalysisData tuple containing (logic_steps, detailed_content)

    Raises:
        ValueError: If the tag is invalid or not found in the analysis data
    """
    # Use provided analysis_dict or initialize a new one
    analysis_data = analysis_dict or init_analysis_data()

    # Validate tag
    if not AnalysisTag.is_valid_tag(tag):
        raise ValueError(f"Invalid analysis tag: {tag}. Valid tags are: {', '.join(AnalysisTag.get_all_tags())}")

    # Check if tag exists in the analysis data
    if tag not in analysis_data:
        raise ValueError(f"Analysis data not found for tag: {tag}")

    return analysis_data[tag]


# Example usage
if __name__ == "__main__":
    try:
        # Get industry analysis data
        industry_tag = AnalysisTag.INDUSTRY.value
        industry_logic, industry_details = get_analysis_data(industry_tag)

        print(f"Analysis for {industry_tag}:")
        print("Logic steps:")
        print(industry_logic)
        print("\nDetailed content:")
        print(industry_details)  # Print first 200 characters

        # Try to get non-existent tag (will raise error)
        # invalid_data = get_analysis_data("无效标签")
    except ValueError as e:
        print(f"Error: {e}")