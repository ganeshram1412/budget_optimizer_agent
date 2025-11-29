"""
tools.py
--------

This module contains financial analysis utilities used by multiple agents
in the FSO-based financial planning workflow. These tools are intentionally
kept stateless and deterministic so they can be safely invoked by LLM agents.

The primary tool in this module:

    • spending_categorizer_and_analyser()

is responsible for computing the user’s cash-flow standing, categorizing
spending patterns, checking rule-of-thumb financial guidelines, and
returning a structured JSON object containing optimization insights.

The tool is designed to run on validated numeric inputs and is heavily used
by the **Budget Optimizer Agent** during Step 3 of the Orchestrator pipeline.

----------------------------------------------------------------------
spending_categorizer_and_analyser()
----------------------------------------------------------------------
Purpose:
    Evaluate a user's income vs. expenses and produce actionable
    optimization insights following commonly accepted personal finance
    heuristics including:
        • 50/30/20 rule (Needs/Wants/Savings)
        • Surplus/Deficit evaluation
        • High discretionary spending detection
        • Fixed expense risk checks
        • Goal funding adequacy

Input Assumptions:
    The Orchestrator or Data Collector agent ensures all input fields
    are sanitized and converted to INR float values before calling this tool.

Parameters:
    monthly_net_income_inr (float):
        The user’s monthly take-home income (after tax).

    fixed_expenses_inr (float):
        Non-discretionary, essential expenses.
        Examples: rent, mortgage, school fees, insurance premiums, EMIs.

    variable_expenses_inr (float):
        Flexible expenses that vary month-to-month.
        Examples: utilities, groceries, travel, fuel, mobile/data charges.

    discretionary_spending_inr (float):
        Wants-based spending.
        Examples: dining out, entertainment, shopping, subscriptions.

    target_savings_inr (float, optional):
        Target monthly savings required to stay on track for long-term goals.
        Defaults to 0. Used to compute “goal funding status”.

Returns:
    Dict[str, Any] containing:

        {
            "total_monthly_net_income_inr": float,
            "total_monthly_expenses_inr": float,
            "net_cash_flow_inr": float,
            "goal_funding_status": "On track" | "Shortfall",
            "funding_shortfall_inr": float,
            "optimization_areas": List[str]
        }

    Each optimization message is written in user-friendly natural language
    so downstream agents can embed them into FSO summaries.

Financial Logic Summary:
    • Surplus/Deficit = income – total expenses
    • If discretionary spending > 30% of income → flagged as overspending
    • If fixed expenses > 50% of income → flagged as high fixed cost load
    • Thin surplus (<10% of income) → flagged as low buffer
    • Negative surplus → marked as warning
    • Goal funding shortfall computed vs. target_savings_inr

This tool does NOT:
    • Modify or return the FSO directly
    • Handle currency parsing (done upstream)
    • Detect high-interest debt (done by other tools)

----------------------------------------------------------------------
"""

from typing import Dict, Any


def spending_categorizer_and_analyser(
    monthly_net_income_inr: float,
    fixed_expenses_inr: float,
    variable_expenses_inr: float,
    discretionary_spending_inr: float,
    target_savings_inr: float = 0.0
) -> Dict[str, Any]:
    """
    Analyze spending patterns and compute cash-flow insights using standard
    budgeting heuristics.

    This function categorizes expenses into Fixed, Variable, Discretionary
    and generates focused optimization suggestions based on:
        • 50/30/20 rule
        • Surplus/deficit position
        • Discretionary overspending
        • Heavy fixed-cost load
        • Safety of cash-flow buffer
        • Goal funding compared to surplus

    Parameters
    ----------
    monthly_net_income_inr : float
        Monthly take-home income after taxes (in INR).

    fixed_expenses_inr : float
        Essential/mandatory monthly commitments (rent, EMIs, insurance, etc.)

    variable_expenses_inr : float
        Monthly variable expenses (utilities, groceries, fuel, etc.)

    discretionary_spending_inr : float
        Wants-based spending (shopping, entertainment, dining out, etc.)

    target_savings_inr : float, optional
        Monthly savings required to meet long-term goals.

    Returns
    -------
    Dict[str, Any]
        A structured payload summarizing:
            • Total expenses
            • Net cash flow
            • Goal funding status
            • Funding shortfall
            • Optimization opportunities
    """
    
    # Calculate totals
    total_expenses = (
        fixed_expenses_inr
        + variable_expenses_inr
        + discretionary_spending_inr
    )
    net_cash_flow = monthly_net_income_inr - total_expenses
    
    optimization_suggestions = []

    # -----------------------------------------------------
    # 50/30/20 RULE — DISCRETIONARY SPENDING CHECK
    # -----------------------------------------------------
    if discretionary_spending_inr > (0.30 * monthly_net_income_inr):
        excess = discretionary_spending_inr - (0.30 * monthly_net_income_inr)
        optimization_suggestions.append(
            f"Your discretionary ('wants') spending is above recommended levels. "
            f"You could potentially reduce **₹{excess:,.2f}** to align with the 30% guideline."
        )

    # -----------------------------------------------------
    # CASH-FLOW HEALTH ANALYSIS
    # -----------------------------------------------------
    if net_cash_flow < 0:
        optimization_suggestions.insert(
            0,
            f"You are running a **monthly deficit of ₹{abs(net_cash_flow):,.2f}**. "
            "Immediate expense reduction or income adjustments are recommended."
        )
    elif net_cash_flow < 0.10 * monthly_net_income_inr:
        optimization_suggestions.append(
            "Your monthly surplus is small. Consider optimizing variable expenses "
            "like utilities, subscriptions, or grocery spend."
        )

    # -----------------------------------------------------
    # FIXED EXPENSE LOAD CHECK
    # -----------------------------------------------------
    if fixed_expenses_inr > (0.50 * monthly_net_income_inr):
        optimization_suggestions.append(
            "Your fixed expenses exceed 50% of your income. Consider reviewing rent, "
            "large EMIs, or refinancing options to reduce fixed burden."
        )

    # -----------------------------------------------------
    # GOAL FUNDING STATUS
    # -----------------------------------------------------
    goal_funding_status = (
        "On track" if net_cash_flow >= target_savings_inr else "Shortfall"
    )
    funding_shortfall = max(0, target_savings_inr - net_cash_flow)

    return {
        "total_monthly_net_income_inr": monthly_net_income_inr,
        "total_monthly_expenses_inr": total_expenses,
        "net_cash_flow_inr": net_cash_flow,
        "goal_funding_status": goal_funding_status,
        "funding_shortfall_inr": funding_shortfall,
        "optimization_areas": optimization_suggestions
    }