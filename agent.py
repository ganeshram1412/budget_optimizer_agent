"""
budget_optimizer_agent.py  
--------------------------

This module defines the **Budget Optimizer Agent**, a key component of the
FSO-driven financial planning workflow. It analyzes a client’s income and
expenses based on their Working/Retired status and updates the 
Financial State Object (FSO) with budget insights, surplus/deficit 
calculations, cash-flow patterns, withdrawal risk, and actionable 
recommendations.

---------------------------------------------------------
AGENT ROLE
---------------------------------------------------------
The Budget Optimizer Agent acts as a:
- Cash-flow analyst  
- Spending structure evaluator  
- Surplus/deficit identifier  
- Withdrawal-rate evaluator for retirees  
- Optimization strategist  

All computations and tool calls must be done strictly using the FSO subset 
passed by the Orchestrator.

---------------------------------------------------------
FSO MANDATE
---------------------------------------------------------
INPUT:
    A JSON-encoded Financial State Object containing at minimum:
        • user_status  (Working / Retired)  
        • monthly_net_income  OR monthly_pension_or_drawdown  
        • commitments, EMIs, investments, savings_per_month  
        • emergency_fund_amount  
        • any existing deficit/surplus context  

OUTPUT:
    A fully updated FSO (JSON), with a new key:

        FSO["budget_analysis_summary"] = {
            "cash_flow_status": "...",
            "surplus_or_deficit_amount": number,
            "withdrawal_rate_safety": {...},         # for retirees
            "optimization_suggestions": [...],
            "high_interest_debt_flag": bool
        }

---------------------------------------------------------
WORKFLOW LOGIC
---------------------------------------------------------

1. Extract all relevant income-/expense-related fields from the FSO.
2. Branch logic:
    a. **Working Clients**
        - Compute net cash flow (income - expenses).
        - Identify surplus or deficit.
        - Generate targeted optimization suggestions:
            • Reduce high-interest EMIs  
            • Optimize discretionary spending  
            • Align investments with goals  
            • Strengthen emergency fund  
    b. **Retired Clients**
        - Use monthly_pension_or_drawdown to compute:
            • Annual drawdown  
            • Withdrawal rate vs. recommended safe rate  
        - Evaluate whether emergency_fund_amount is sufficient.
3. Call the `spending_categorizer_and_analyser` tool to classify 
   spending patterns and assist the analysis.
4. Append all results into FSO["budget_analysis_summary"].
5. Add a boolean flag:
        FSO["debt_flag"] = True
   if high-interest debt categories are detected.
6. Return ONLY the updated FSO JSON string.

---------------------------------------------------------
CONSTRAINTS
---------------------------------------------------------
• Never output explanation text — output ONLY the updated FSO.
• All currency amounts must be shown in ₹ INR or $ USD.
• All computation logic must be performed internally by the LLM.
• No additional natural language outside the FSO is allowed.

---------------------------------------------------------
AGENT SUMMARY
---------------------------------------------------------
This agent serves as the foundation for spending insights, debt flags, and
cashflow-based decision making that directly inform risk assessment, 
goal feasibility, debt management, and tax planning agents downstream.

"""

# budget_optimizer_agent.py - FSO Integrated and Status-Aware

from google.adk.agents.llm_agent import Agent
from .tools import spending_categorizer_and_analyser 
import json 

# --- OPTIMIZED AGENT INSTRUCTION (FSO Integrated) ---
optimized_agent_instruction = """
You are the **Budget Optimizer Coach**. Your mission is to analyze the client's cash flow 
and update the FSO. Maintain an encouraging, practical, and structured tone. Use ₹ INR for all amounts.

============================================
FSO PROCESS MANDATE
============================================

1.  **FSO Input/Output:**  
    You receive the FSO as a JSON string.  
    Your ONLY output MUST be the **UPDATED FSO**.

2.  **Data Extraction:**  
    Extract all required fields from the FSO, including:
        • user_status (Working or Retired)  
        • monthly_net_income OR monthly_pension_or_drawdown  
        • commitments, EMIs, investment_contributions  
        • savings_per_month  
        • emergency_fund_amount  

3.  **Conditional Cash-Flow Analysis:**

    • If **Working**:  
        - Compute Net Disposable Cash Flow  
        - Identify Surplus / Deficit  
        - Provide concise, actionable optimization suggestions  
          focused on increasing savings and reducing inefficient spend.

    • If **Retired**:  
        - Compute annual drawdown  
        - Determine Withdrawal Rate  
        - Assess safety relative to common thresholds (3-5%)  
        - Consider emergency_fund sufficiency  
        - Generate sustainability recommendations

4.  **Tool Execution:**  
    Call the `spending_categorizer_and_analyser` tool with the extracted FSO fields.

5.  **FSO Update:**  
    Add results under:
        FSO["budget_analysis_summary"]

    Also set:
        FSO["debt_flag"] = True
    if high-interest debts are detected.

6.  **Final Output:**  
    Return ONLY the updated FSO JSON.  
    No explanations. No assistant text. No formatting.
"""

# --- AGENT DEFINITION ---
budget_optimizer_agent_tool = Agent(
    model='gemini-2.5-flash',
    name='budget_optimizer_agent',
    description=(
        "Analyzes the user’s income, expenses, EMIs, and status (Working/Retired) "
        "from the FSO, computes surplus/deficit or withdrawal rate, calls the "
        "spending analysis tool, and updates the FSO with a structured "
        "budget_analysis_summary."
    ),
    instruction=optimized_agent_instruction,
    tools=[spending_categorizer_and_analyser],
    output_key="financial_state_object"
)