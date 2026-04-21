from agents.base_agent import BaseAgent
import json
from typing import Dict, List

class SecurityTestingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Sam",
            role="Application Security Engineer",
            goal="Identify and report security vulnerabilities, ensure OWASP Top 10 compliance, and validate security controls",
            backstory="Sam is a certified CISSP and OSCP with 10 years in application security. Expert in OWASP, penetration testing, threat modelling, SAST/DAST, and secure code review."
        )

    def run_security_analysis(self, code_files: List[Dict], architecture: Dict) -> Dict:
        all_code = "\n\n".join([
            f"=== {f.get('path')} ===\n{f.get('content', '')[:2000]}"
            for f in code_files[:10]  # Limit to avoid token overflow
        ])

        security_reqs = architecture.get("security_requirements", [])

        prompt = f"""Perform a comprehensive security analysis of this codebase.

SECURITY REQUIREMENTS: {json.dumps(security_reqs, indent=2)}

CODE SAMPLE:
{all_code}

Check for OWASP Top 10 and return JSON:
{{
  "overall_status": "PASSED | FAILED",
  "security_score": 87,
  "owasp_checks": [
    {{
      "category": "A01:2021 - Broken Access Control",
      "status": "PASSED | FAILED | WARNING",
      "findings": ["Finding 1", "Finding 2"],
      "severity": "Critical | High | Medium | Low | Info"
    }},
    {{
      "category": "A02:2021 - Cryptographic Failures",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A03:2021 - Injection",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A04:2021 - Insecure Design",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A05:2021 - Security Misconfiguration",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A06:2021 - Vulnerable Components",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A07:2021 - Auth & Session Management",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A08:2021 - Data Integrity Failures",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A09:2021 - Security Logging",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }},
    {{
      "category": "A10:2021 - SSRF",
      "status": "PASSED",
      "findings": [],
      "severity": "Info"
    }}
  ],
  "critical_issues": [],
  "high_issues": [],
  "medium_issues": [],
  "recommendations": ["Recommendation 1"],
  "remediation_required_before_prod": true/false
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=4096)
        try:
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            return json.loads(output)
        except:
            return {
                "overall_status": "FAILED",
                "security_score": 0,
                "error": "Security analysis parsing failed",
                "raw": output[:500],
                "remediation_required_before_prod": True
            }

    def generate_security_test_scripts(self, architecture: Dict) -> Dict:
        endpoints = []
        for module in architecture.get("modules", []):
            endpoints.extend(module.get("api_endpoints", []))

        prompt = f"""Generate security test scripts for these API endpoints.

ENDPOINTS: {json.dumps(endpoints[:10], indent=2)}

Return JSON with test scripts:
{{
  "test_files": [
    {{
      "path": "tests/security/test_auth.py",
      "content": "# Pytest security tests - real code",
      "description": "Authentication & authorization tests"
    }},
    {{
      "path": "tests/security/test_injection.py",
      "content": "# SQL injection & XSS tests",
      "description": "Injection vulnerability tests"
    }}
  ],
  "notes": "How to run these tests"
}}

Return ONLY valid JSON."""

        output = self._call_llm(self._system_prompt(), prompt, max_tokens=4096)
        try:
            if "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
                if output.startswith("json"):
                    output = output[4:].strip()
            return json.loads(output)
        except:
            return {"test_files": [], "notes": output}
