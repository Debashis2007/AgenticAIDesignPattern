"""Immigration knowledge base with visa timelines, requirements, and data."""

from __future__ import annotations

# Visa category timelines (in months, as of 2024-2026)
VISA_TIMELINES = {
    "h1b": {
        "name": "H-1B Specialty Occupation",
        "processing_time": "3-6 months",
        "validity": "3 years (renewable to 6)",
        "requirements": [
            "Bachelor's degree or higher",
            "Job offer from US employer",
            "Labor Condition Application (LCA)",
            "Petitioner (employer) files I-129"
        ],
        "key_dates": {
            "cap_season": "April",
            "processing_start": "April 1",
            "final_action_dates_vary": "Typically 6-12 months after filing"
        }
    },
    "l1": {
        "name": "L-1 Intracompany Transferee",
        "processing_time": "2-4 months",
        "validity": "Up to 5 years (L1A) or 2 years (L1B)",
        "requirements": [
            "Currently employed by same company for 1+ year",
            "Transfer to US parent, subsidiary, or affiliate",
            "Managerial, executive, or specialized knowledge role",
            "Company must have continuous operations in both countries"
        ]
    },
    "eb_green_card": {
        "name": "Employment-Based Green Card",
        "processing_time": "1-3 years (varies by category)",
        "validity": "Permanent residence",
        "requirements": [
            "Job offer from US employer",
            "Labor Certification (PERM) for EB2/EB3",
            "I-140 petition approval",
            "I-485 green card application"
        ],
        "categories": {
            "eb1": "Priority Workers (EB1A - Extraordinary ability, EB1B - Outstanding professors/researchers)",
            "eb2": "Professionals with advanced degrees or exceptional ability",
            "eb3": "Skilled workers, professionals, other workers"
        }
    },
    "o1": {
        "name": "O-1 Extraordinary Ability",
        "processing_time": "2-4 months",
        "validity": "3 years (extendable)",
        "requirements": [
            "Extraordinary ability in sciences, arts, education, business, or athletics",
            "Evidence: awards, publications, media coverage, or peer recognition"
        ]
    },
    "niw": {
        "name": "National Interest Waiver (EB2 without PERM)",
        "processing_time": "1-2 years",
        "validity": "Green card path",
        "requirements": [
            "Advanced degree or exceptional ability",
            "Work in area of substantial intrinsic merit",
            "Waiver benefits US national interest more than standard PERM"
        ]
    }
}

# Common timelines and bottlenecks
PROCESSING_INSIGHTS = {
    "concurrent_filing": {
        "description": "I-140 and I-485 filed together (if eligible)",
        "benefit": "Can start work and travel authorization earlier",
        "eligibility": "Must have current priority date or filing fee receipt"
    },
    "priority_date": {
        "description": "Date application is received (crucial for green cards)",
        "importance": "Determines visa availability under annual caps",
        "note": "Check USCIS visa bulletin monthly for current dates"
    },
    "country_quotas": {
        "note": "India and China have 7% cap, causing long backlogs for skilled workers",
        "india_backlog": "5-10+ years for EB2/EB3",
        "china_backlog": "1-2 years for EB2/EB3",
        "other_countries": "1-2 years typically"
    }
}

# Risk factors and red flags
COMMON_ISSUES = {
    "timeline_stress": {
        "issue": "Worried about long timelines",
        "solutions": [
            "Explore faster pathways (H1B -> L1 -> Green Card)",
            "Consider employer sponsorship for EB1B (outstanding professor pathway)",
            "Network to find employers sponsoring NIW or O-1"
        ]
    },
    "conflicting_info": {
        "issue": "Hearing different advice from lawyers, HR, online forums",
        "solutions": [
            "Consult with qualified immigration attorney (often free initial consultation)",
            "Reference official USCIS.gov resources",
            "Verify current processing times on USCIS case tracker",
            "Join verified communities (lawful forums, not anonymous advice)"
        ]
    },
    "employer_communication": {
        "issue": "Unsure how to discuss immigration goals with employer",
        "solutions": [
            "Frame it as retention and talent development opportunity",
            "Provide cost-benefit analysis (sponsorship cost vs. hiring externally)",
            "Share timeline expectations and commitment to company",
            "Offer to handle legal coordination to reduce HR burden"
        ]
    }
}

# Visa strategy decision tree
VISA_SELECTION_GUIDE = {
    "currently_on_student_visa_f1": {
        "short_term": "OPT (Optional Practical Training) - 12-36 months work authorization",
        "medium_term": "H1B sponsorship (need employer, subject to cap lottery)",
        "long_term": "Employer sponsors green card (EB3 -> EB2 -> EB1B possible)"
    },
    "currently_on_h1b": {
        "advantages": "Work authorization, portable to new employers (after 180 days)",
        "next_steps": [
            "Start green card sponsorship process (EB3 or EB2)",
            "Explore internal transfers via L1 if company has subsidiaries",
            "Build profile for O-1 or NIW if eligible"
        ]
    },
    "currently_on_l1": {
        "advantages": "Flexible, renewable, easy to transfer within company",
        "next_steps": [
            "Start green card sponsorship (EB1B for managers/specialized knowledge)",
            "Easier concurrent filing if eligible"
        ]
    },
    "outside_us_seeking_entry": {
        "fastest": "L1 (if company has US operations)",
        "most_direct": "H1B (requires cap, lottery-based)",
        "alternative": "Start with O-1 if have extraordinary ability",
        "note": "Green card process from abroad similar to from US"
    }
}


def get_visa_info(visa_type: str) -> dict | None:
    """Retrieve information about a specific visa type."""
    return VISA_TIMELINES.get(visa_type.lower())


def get_strategy_for_situation(situation: str) -> dict | None:
    """Get visa strategy recommendations for a life situation."""
    return VISA_SELECTION_GUIDE.get(situation.lower())
