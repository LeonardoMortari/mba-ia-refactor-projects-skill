# Anti-pattern catalog

| ID | Detection signal | Severity |
|---|---|---|
| A01 | Hardcoded secret, password, token or key | CRITICAL |
| A02 | Request-controlled SQL or unsafe concatenation | CRITICAL |
| A03 | God class/module mixing routes, domain and persistence | HIGH |
| A04 | Fat controller with extensive business rules | HIGH |
| A05 | Global mutable connection, cache or state | HIGH |
| A06 | Related writes without transaction/rollback | HIGH |
| A07 | Dependent query inside a loop (N+1) | MEDIUM |
| A08 | Missing/duplicated validation or unsafe input contract | MEDIUM |
| A09 | Broad exception handling or internal error leakage | MEDIUM |
| A10 | Deprecated API without modern replacement | MEDIUM |
| A11 | Duplicated serialization or business rule | LOW |
| A12 | Magic values, dead imports or weak logging | LOW |

Findings require code evidence and a concrete recommendation. For deprecated APIs, name the compatible modern equivalent.
