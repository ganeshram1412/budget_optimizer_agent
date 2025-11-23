# tools.py (Adding to your existing tools)
from typing import Dict, Any

def spending_categorizer_and_analyser(
    monthly_net_income_inr: float,
    fixed_expenses_inr: float,
    variable_expenses_inr: float,
    discretionary_spending_inr: float,
    target_savings_inr: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates the user's net monthly cash flow and identifies potential areas 
    for budget optimization based on standard financial rules.
    """
    
    total_expenses = fixed_expenses_inr + variable_expenses_inr + discretionary_spending_inr
    net_cash_flow = monthly_net_income_inr - total_expenses
    
    # --- Optimization Analysis ---
    
    optimization_suggestions = []
    
    # 1. 50/30/20 Rule Check (Needs/Wants/Savings)
    # The tool uses a simplified model based on the three categories provided:
    # Needs (Fixed) + Wants (Discretionary) + Variable (Mix)
    
    # Check if discretionary spending is too high (Wants)
    # If Discretionary spending exceeds 30% of Net Income, flag it for review.
    if discretionary_spending_inr > (0.30 * monthly_net_income_inr):
        excess_wants = discretionary_spending_inr - (0.30 * monthly_net_income_inr)
        optimization_suggestions.append(f"**Discretionary Spending** (Wants) is high. Potential to save **₹{excess_wants:,.2f}** by aligning with the 30% rule.")
        
    # Check if net cash flow is negative or low
    if net_cash_flow < 0:
        optimization_suggestions.insert(0, "**WARNING**: You are currently running a **monthly deficit** of ₹{net_cash_flow:,.2f}. Immediate expense cuts are required.")
    elif net_cash_flow < 0.10 * monthly_net_income_inr:
        optimization_suggestions.append("Your cash flow surplus is thin. Look for efficiencies in **Variable Expenses** like utility bills or non-essential subscriptions.")
        
    # Check if fixed expenses are manageable (e.g., should be < 50% of income)
    if fixed_expenses_inr > (0.50 * monthly_net_income_inr):
         optimization_suggestions.append("Your **Fixed Expenses** (rent/EMI/etc.) consume over 50% of income. Review housing costs or consider refinancing opportunities.")

    # --- Goal Funding Status ---
    goal_funding_status = "On track" if net_cash_flow >= target_savings_inr else "Shortfall"
    funding_shortfall = max(0, target_savings_inr - net_cash_flow)
    
    return {
        "total_monthly_net_income_inr": monthly_net_income_inr,
        "total_monthly_expenses_inr": total_expenses,
        "net_cash_flow_inr": net_cash_flow,
        "goal_funding_status": goal_funding_status,
        "funding_shortfall_inr": funding_shortfall,
        "optimization_areas": optimization_suggestions
    }