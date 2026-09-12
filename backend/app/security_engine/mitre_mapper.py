from typing import Dict, Tuple
from app.security_engine.types import ThreatVectorType

MITRE_TECHNIQUE_CATALOG: Dict[ThreatVectorType, Tuple[str, str, str]] = {
    ThreatVectorType.LOGIN_ANOMALY: ("Initial Access", "T1078.004", "Valid Accounts: Cloud Accounts (Impossible Travel)"),
    ThreatVectorType.BRUTE_FORCE: ("Credential Access", "T1110.001", "Brute Force: Password Guessing / Spraying"),
    ThreatVectorType.SUSPICIOUS_USER_ACTIVITY: ("Privilege Escalation", "T1078", "Valid Accounts: Unauthorized Role Elevation"),
    ThreatVectorType.FAILED_AUTH_ANALYSIS: ("Defense Evasion", "T1556", "Modify Authentication Process / Token Replay"),
    ThreatVectorType.API_MISUSE: ("Discovery", "T1059", "Command and Scripting Interpreter / API Enumeration"),
    ThreatVectorType.DATA_ACCESS_ANOMALY: ("Exfiltration", "T1020", "Automated Exfiltration: Mass Data Extraction"),
}


class MitreAttackMapper:
    """Maps detected security vectors to standard MITRE ATT&CK Enterprise Framework."""

    @classmethod
    def get_mapping(cls, vector: ThreatVectorType) -> Tuple[str, str, str]:
        return MITRE_TECHNIQUE_CATALOG.get(
            vector,
            ("Initial Access", "T1078", "Valid Accounts"),
        )
