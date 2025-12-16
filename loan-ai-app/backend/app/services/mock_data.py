"""Mock data for development and testing"""
import asyncio
import random
from typing import Dict, Any

def get_loan_products():
    """Return mock loan products"""
    return [
        {
            "id": "1",
            "name": "Personal Loan",
            "description": "Unsecured personal loan for various purposes",
            "rate": 10.5,
            "max_amount": 500000,
            "min_amount": 10000,
            "tenure": "12-60 months"
        },
        {
            "id": "2",
            "name": "Home Loan",
            "description": "Mortgage loan for purchasing or constructing a home",
            "rate": 8.5,
            "max_amount": 10000000,
            "min_amount": 500000,
            "tenure": "5-30 years"
        },
        {
            "id": "3",
            "name": "Business Loan",
            "description": "Working capital and business expansion loans",
            "rate": 12.0,
            "max_amount": 5000000,
            "min_amount": 100000,
            "tenure": "12-84 months"
        },
        {
            "id": "4",
            "name": "Auto Loan",
            "description": "Vehicle financing for new and used cars",
            "rate": 9.0,
            "max_amount": 2000000,
            "min_amount": 50000,
            "tenure": "12-84 months"
        }
    ]

def get_credit_scores():
    """Return mock credit scores"""
    return {
        "default": 650,
        "applicant_001": 750,
        "applicant_002": 680,
        "applicant_003": 620,
    }

def get_risk_factors():
    """Return mock risk factors"""
    return [
        "Stable employment history",
        "Good credit history",
        "Adequate income-to-debt ratio"
    ]

class MockDataService:
    """Simulate external API calls (CRM, Credit Bureau, Offer Mart)"""
    
    @staticmethod
    async def get_credit_score(pan_number: str) -> int:
        """Simulate credit bureau API call"""
        await asyncio.sleep(0.5)  # Simulate API delay
        # Return random credit score between 650-850
        return random.randint(650, 850)
    
    @staticmethod
    async def check_existing_loans(pan_number: str) -> Dict[str, Any]:
        """Simulate CRM check for existing loans"""
        await asyncio.sleep(0.3)
        return {
            "existing_loans": random.choice([0, 50000, 100000, 200000]),
            "outstanding_emi": random.choice([0, 5000, 10000, 15000]),
            "active_loans_count": random.choice([0, 1, 2])
        }
    
    @staticmethod
    async def get_offer_eligibility(loan_amount: float, monthly_salary: float) -> Dict[str, Any]:
        """Simulate Offer Mart API for eligibility check"""
        await asyncio.sleep(0.4)
        max_eligible = monthly_salary * 10
        eligible = loan_amount <= max_eligible
        
        return {
            "eligible": eligible,
            "max_eligible_amount": max_eligible,
            "recommended_tenure": 36 if eligible else 0,
            "interest_rate": 12.5 if eligible else None
        }
