"""
RightLeftAI brand knowledge base — injected into every agent's context.
Update this as products evolve.
"""

BRAND_CONTEXT = """
COMPANY: RightLeftAI (RLAI)
WEBSITE: https://rightleft.ai
TAGLINE: "AI Solutions That Think Differently"
POSITIONING: India's expert AI solutions company specialising in Computer Vision, Document Intelligence, Voice AI, and L&D/Marketing AI.

PRODUCTS:

1. LOVAIC (Computer Vision Platform)
   - Image & video analytics at pixel level
   - Use cases: Quality control, surveillance, retail analytics, medical imaging, defect detection
   - Industries: Manufacturing, Healthcare, Retail, Security, Agriculture
   - USP: Pixel-level precision that generic CV tools miss
   - More info: https://rlaipm.rightleft.ai/

2. SatyaDocAI (Document Forgery Detection)
   - AI-powered document authenticity verification
   - Detects forged documents: IDs, certificates, contracts, invoices
   - Use cases: KYC, loan processing, recruitment verification, insurance claims
   - Industries: BFSI (Banking/Finance), HR, Insurance, Government
   - USP: Catches forgeries that human eyes and basic tools miss

3. AI Voice Agent Suite
   - SalesBuddy: AI voice agent for sales calls, lead qualification
   - EvalBuddy: AI voice agent for HR interviews, assessments
   - VoiceBuddy: Conversational AI chatbot from ingested knowledge base
   - Use cases: 24/7 customer support, sales automation, recruitment automation
   - Industries: Any with high call volume or customer interaction

4. AI Avatar L&D & Marketing Solution
   - AI Avatar-based Learning & Development content
   - Auto-generate marketing video ads using AI avatars
   - Use cases: Corporate training, product demos, social media ads
   - Industries: EdTech, Corporate HR, D2C Brands, FMCG

TONE OF VOICE: Expert but approachable. Data-driven. Forward-thinking. Indian business context with global relevance.
AVOID: Generic AI buzzwords without substance. Overpromising. Jargon without explanation.
ALWAYS: Tie AI benefits to real business outcomes (cost savings, accuracy %, time savings).
"""

PRODUCT_MAPPING = {
    "banking": ["SatyaDocAI", "SalesBuddy", "LOVAIC"],
    "finance": ["SatyaDocAI", "SalesBuddy", "EvalBuddy"],
    "insurance": ["SatyaDocAI", "LOVAIC", "SalesBuddy"],
    "healthcare": ["LOVAIC", "SatyaDocAI", "VoiceBuddy"],
    "manufacturing": ["LOVAIC", "VoiceBuddy"],
    "retail": ["LOVAIC", "SalesBuddy", "AI Avatar Marketing"],
    "hr": ["EvalBuddy", "AI Avatar L&D", "VoiceBuddy"],
    "education": ["AI Avatar L&D", "EvalBuddy", "VoiceBuddy"],
    "government": ["SatyaDocAI", "LOVAIC", "VoiceBuddy"],
    "real_estate": ["SatyaDocAI", "SalesBuddy"],
    "ecommerce": ["LOVAIC", "SalesBuddy", "AI Avatar Marketing"],
    "logistics": ["LOVAIC", "SatyaDocAI"],
    "telecom": ["VoiceBuddy", "SalesBuddy", "EvalBuddy"],
    "fmcg": ["AI Avatar Marketing", "LOVAIC", "SalesBuddy"],
}

PAIN_POINTS = {
    "SatyaDocAI": [
        "Document fraud costs Indian banks ₹1000+ crore annually",
        "Manual KYC verification takes 3-7 days and misses 30% of forgeries",
        "Insurance claim fraud due to fake documents is rising 20% YoY",
    ],
    "LOVAIC": [
        "Manual quality inspection misses 15-20% of defects on production lines",
        "Security surveillance requires 24/7 human monitoring — expensive and error-prone",
        "Retail shrinkage (theft) causes 2-3% revenue loss — CV can reduce it by 60%",
    ],
    "SalesBuddy": [
        "Sales teams waste 60% of time on unqualified leads",
        "Average lead response time is 47 hours — AI responds in 2 seconds",
        "70% of leads go cold because follow-up is inconsistent",
    ],
    "AI Avatar L&D": [
        "Corporate training video production costs ₹2-5 lakh per module",
        "Employee training completion rates are <40% for traditional formats",
        "Marketing video ads cost ₹5-20 lakh for a professional shoot",
    ],
}
