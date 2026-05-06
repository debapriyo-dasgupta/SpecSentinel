"""
specsentinel/engine/signal_extractor.py

Parses an OpenAPI 3.x specification and extracts "signals" —
structured observations about what is missing, inconsistent, or risky.
Each signal is then used to query the vector DB for matching rules.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Signal:
    """A single observable issue or characteristic extracted from an API spec."""
    signal_id:   str
    category:    str          # maps to vector DB collection
    description: str          # natural language query for vector DB
    context:     dict = field(default_factory=dict)   # spec path, endpoint, etc.
    evidence:    str = ""     # what exactly was found (or missing)


class OpenAPISignalExtractor:
    """
    Extracts compliance signals from a parsed OpenAPI 3.x specification dict.

    Usage:
        spec = yaml.safe_load(open("myapi.yaml"))
        extractor = OpenAPISignalExtractor(spec)
        signals = extractor.extract_all()
    """

    def __init__(self, spec: dict):
        self.spec = spec
        self.paths  = spec.get("paths", {}) or {}
        self.components = spec.get("components", {}) or {}
        self.info   = spec.get("info", {}) or {}
        self.security_schemes = (
            spec.get("components", {}).get("securitySchemes", {}) or {}
        )
        self.global_security = spec.get("security", [])

    def extract_all(self) -> list[Signal]:
        """Run all signal extractors and return the combined list."""
        signals: list[Signal] = []
        signals.extend(self._check_security())
        signals.extend(self._check_design())
        signals.extend(self._check_error_handling())
        signals.extend(self._check_documentation())
        signals.extend(self._check_governance())
        return signals

    # ── Security Signals ──────────────────────────────────────────────────────

    def _check_security(self) -> list[Signal]:
        signals = []

        # 1. No security schemes defined at all
        if not self.security_schemes:
            signals.append(Signal(
                signal_id="SEC-001",
                category="security",
                description="no authentication scheme defined, missing OAuth2 JWT API key security scheme",
                evidence="components.securitySchemes is empty or absent",
            ))
        else:
            # Check for weak or missing scheme types
            scheme_types = [v.get("type", "") for v in self.security_schemes.values()]
            if "oauth2" not in scheme_types and "http" not in scheme_types:
                signals.append(Signal(
                    signal_id="SEC-002",
                    category="security",
                    description="missing OAuth2 or JWT bearer authentication, only API key present",
                    evidence=f"Scheme types found: {scheme_types}",
                ))

        # 2. No global security requirement
        if not self.global_security:
            signals.append(Signal(
                signal_id="SEC-003",
                category="security",
                description="missing global security requirement, endpoints not secured by default",
                evidence="spec.security array is empty or absent",
            ))

        # 3. Per-endpoint: missing 401 / 403 / 429 responses
        for path, path_item in self.paths.items():
            for method, operation in _iter_operations(path_item):
                op_security = operation.get("security", self.global_security)
                responses   = operation.get("responses", {})
                resp_codes  = set(str(k) for k in responses.keys())

                # If endpoint has security, it needs 401
                if op_security and "401" not in resp_codes:
                    signals.append(Signal(
                        signal_id="SEC-004",
                        category="security",
                        description="missing 401 Unauthorized response on authenticated endpoint",
                        context={"path": path, "method": method},
                        evidence=f"Security defined but no 401 in responses: {resp_codes}",
                    ))

                # If endpoint has scopes, it needs 403
                has_scopes = _operation_has_scopes(operation, self.security_schemes)
                if has_scopes and "403" not in resp_codes:
                    signals.append(Signal(
                        signal_id="SEC-005",
                        category="security",
                        description="missing 403 Forbidden response on scope-restricted endpoint",
                        context={"path": path, "method": method},
                        evidence=f"Scoped security defined but no 403 in responses: {resp_codes}",
                    ))

                # Rate limiting: 429 missing
                if "429" not in resp_codes:
                    signals.append(Signal(
                        signal_id="SEC-006",
                        category="security",
                        description="missing 429 Too Many Requests response, no rate limiting documented",
                        context={"path": path, "method": method},
                        evidence=f"Response codes present: {resp_codes}",
                    ))

        # 4. Sensitive fields in response schemas (basic check)
        sensitive_patterns = re.compile(
            r"password|secret|token|private_key|credit_card|ssn|social_security",
            re.IGNORECASE,
        )
        for schema_name, schema in (self.components.get("schemas", {}) or {}).items():
            props = schema.get("properties", {}) or {}
            for prop_name in props:
                if sensitive_patterns.search(prop_name):
                    prop_def = props[prop_name]
                    if not prop_def.get("writeOnly") and not prop_def.get("readOnly"):
                        signals.append(Signal(
                            signal_id="SEC-007",
                            category="security",
                            description="sensitive data field exposed in response schema without writeOnly protection",
                            context={"schema": schema_name, "property": prop_name},
                            evidence=f"Property '{prop_name}' in schema '{schema_name}' lacks writeOnly:true",
                        ))

        return _deduplicate(signals)

    # ── Design Signals ────────────────────────────────────────────────────────

    def _check_design(self) -> list[Signal]:
        signals = []

        # 1. No versioning in paths
        paths_list = list(self.paths.keys())
        versioned  = [p for p in paths_list if re.match(r"^/v\d+/", p)]
        if paths_list and not versioned:
            signals.append(Signal(
                signal_id="DES-001",
                category="design",
                description="missing API versioning in paths, no /v1/ or /v2/ prefix found",
                evidence=f"Sample paths: {paths_list[:3]}",
            ))

        for path, path_item in self.paths.items():
            for method, operation in _iter_operations(path_item):

                # 2. Missing operationId
                if not operation.get("operationId"):
                    signals.append(Signal(
                        signal_id="DES-002",
                        category="design",
                        description="missing operationId on endpoint, no unique operation identifier",
                        context={"path": path, "method": method},
                        evidence="operationId field absent",
                    ))

                # 3. Missing tags
                if not operation.get("tags"):
                    signals.append(Signal(
                        signal_id="DES-003",
                        category="design",
                        description="untagged endpoint, missing tags for API grouping and documentation",
                        context={"path": path, "method": method},
                        evidence="tags array is empty or absent",
                    ))

                # 4. Verb in path (non-RESTful naming)
                verb_pattern = re.compile(
                    r"/(get|create|update|delete|list|fetch|retrieve|add|remove|"
                    r"post|put|modify|set|check|do|make|handle|process)/",
                    re.IGNORECASE,
                )
                if verb_pattern.search(path):
                    signals.append(Signal(
                        signal_id="DES-004",
                        category="design",
                        description="verb in API path, non-RESTful resource naming convention",
                        context={"path": path, "method": method},
                        evidence=f"Path contains verb: {path}",
                    ))

                # 5. GET with request body
                if method == "get" and operation.get("requestBody"):
                    signals.append(Signal(
                        signal_id="DES-005",
                        category="design",
                        description="GET request with request body, improper HTTP method usage",
                        context={"path": path, "method": method},
                        evidence="GET operation defines requestBody",
                    ))

                # 6. Collection endpoint without pagination
                responses = operation.get("responses", {})
                if method == "get" and _response_is_array(responses):
                    params = [p.get("name", "") for p in (operation.get("parameters") or [])]
                    paging = {"page", "limit", "offset", "cursor", "per_page", "size"}
                    if not paging.intersection(set(params)):
                        signals.append(Signal(
                            signal_id="DES-006",
                            category="design",
                            description="collection endpoint missing pagination parameters, no page limit offset cursor",
                            context={"path": path, "method": method},
                            evidence=f"Parameters: {params}, no pagination found",
                        ))

        # 7. No reusable components defined
        if not self.components.get("schemas"):
            signals.append(Signal(
                signal_id="DES-007",
                category="design",
                description="no reusable schema components defined, inline schemas only",
                evidence="components.schemas is empty or absent",
            ))

        # 8. Naming convention inconsistency (mix of camelCase and snake_case)
        all_props = _collect_all_property_names(self.components)
        if all_props and _has_mixed_conventions(all_props):
            signals.append(Signal(
                signal_id="DES-008",
                category="design",
                description="inconsistent naming conventions mixing camelCase and snake_case across schemas",
                evidence=f"Sample properties: {list(all_props)[:10]}",
            ))

        return _deduplicate(signals)

    # ── Error Handling Signals ────────────────────────────────────────────────

    def _check_error_handling(self) -> list[Signal]:
        signals = []

        # 1. No standard error schema
        schemas = self.components.get("schemas", {}) or {}
        error_schema_names = [k for k in schemas if "error" in k.lower() or "problem" in k.lower()]
        if not error_schema_names:
            signals.append(Signal(
                signal_id="ERR-001",
                category="error_handling",
                description="missing standardized error response schema, no RFC 7807 problem details schema",
                evidence="No 'Error' or 'Problem' schema found in components.schemas",
            ))
        else:
            # Check if error schema has RFC 7807 fields
            err_schema = schemas.get(error_schema_names[0], {})
            props = err_schema.get("properties", {}) or {}
            rfc_fields = {"type", "title", "status", "detail"}
            missing_rfc = rfc_fields - set(props.keys())
            if missing_rfc:
                signals.append(Signal(
                    signal_id="ERR-002",
                    category="error_handling",
                    description="error schema missing RFC 7807 fields: type title status detail instance",
                    evidence=f"Missing fields: {missing_rfc} from schema '{error_schema_names[0]}'",
                ))

        # 2. Inconsistent error responses (not using $ref to shared component)
        error_response_schemas = []
        for path, path_item in self.paths.items():
            for method, operation in _iter_operations(path_item):
                for code, response in (operation.get("responses", {}) or {}).items():
                    if str(code).startswith("4") or str(code).startswith("5"):
                        content = response.get("content", {})
                        for media, media_obj in content.items():
                            schema = media_obj.get("schema", {})
                            if schema.get("$ref"):
                                error_response_schemas.append(schema["$ref"])
                            elif schema:
                                error_response_schemas.append("inline")

        if error_response_schemas:
            inline_count = error_response_schemas.count("inline")
            if inline_count > 0 and inline_count < len(error_response_schemas):
                signals.append(Signal(
                    signal_id="ERR-003",
                    category="error_handling",
                    description="inconsistent error response schema, mix of inline and referenced error schemas",
                    evidence=f"{inline_count} inline vs {len(error_response_schemas) - inline_count} ref-based error schemas",
                ))
            elif inline_count == len(error_response_schemas) and inline_count > 1:
                signals.append(Signal(
                    signal_id="ERR-004",
                    category="error_handling",
                    description="all error responses use inline schemas, no reusable error component",
                    evidence=f"{inline_count} inline error schemas detected",
                ))

        return _deduplicate(signals)

    # ── Documentation Signals ─────────────────────────────────────────────────

    def _check_documentation(self) -> list[Signal]:
        signals = []

        for path, path_item in self.paths.items():
            for method, operation in _iter_operations(path_item):

                # Missing summary
                if not operation.get("summary"):
                    signals.append(Signal(
                        signal_id="DOC-001",
                        category="documentation",
                        description="missing endpoint summary, undocumented operation",
                        context={"path": path, "method": method},
                        evidence="summary field absent",
                    ))

                # Missing description
                if not operation.get("description"):
                    signals.append(Signal(
                        signal_id="DOC-002",
                        category="documentation",
                        description="missing endpoint description, no operation detail documentation",
                        context={"path": path, "method": method},
                        evidence="description field absent",
                    ))

                # Missing request body examples
                req_body = operation.get("requestBody", {})
                if req_body:
                    content = req_body.get("content", {})
                    for media, media_obj in content.items():
                        if not media_obj.get("example") and not media_obj.get("examples"):
                            signals.append(Signal(
                                signal_id="DOC-003",
                                category="documentation",
                                description="missing request body example in API documentation",
                                context={"path": path, "method": method},
                                evidence="No example or examples in requestBody content",
                            ))

        # Schema property descriptions
        schemas = self.components.get("schemas", {}) or {}
        undoc_props = 0
        for schema_name, schema in schemas.items():
            for prop_name, prop_def in (schema.get("properties", {}) or {}).items():
                if not prop_def.get("description"):
                    undoc_props += 1

        if undoc_props > 0:
            signals.append(Signal(
                signal_id="DOC-004",
                category="documentation",
                description="schema properties missing description field, undocumented data model",
                evidence=f"{undoc_props} properties lack description across all schemas",
            ))

        return _deduplicate(signals)

    # ── Governance Signals ────────────────────────────────────────────────────

    def _check_governance(self) -> list[Signal]:
        signals = []

        # 1. Missing info.version
        if not self.info.get("version"):
            signals.append(Signal(
                signal_id="GOV-001",
                category="governance",
                description="missing API version in info section, no lifecycle version tracking",
                evidence="info.version field is absent",
            ))

        # 2. Missing contact info
        if not self.info.get("contact"):
            signals.append(Signal(
                signal_id="GOV-002",
                category="governance",
                description="missing contact information in API info, no team ownership documented",
                evidence="info.contact is absent",
            ))

        # 3. Missing license
        if not self.info.get("license"):
            signals.append(Signal(
                signal_id="GOV-003",
                category="governance",
                description="missing license information, API usage terms undefined",
                evidence="info.license is absent",
            ))

        # 4. Deprecated endpoints without deprecation flag
        deprecation_keywords = re.compile(r"deprecated|legacy|old|obsolete|sunset", re.IGNORECASE)
        for path, path_item in self.paths.items():
            for method, operation in _iter_operations(path_item):
                desc = operation.get("description", "") or ""
                summary = operation.get("summary", "") or ""
                if deprecation_keywords.search(desc + summary) and not operation.get("deprecated"):
                    signals.append(Signal(
                        signal_id="GOV-004",
                        category="governance",
                        description="endpoint appears deprecated but missing deprecated flag in spec",
                        context={"path": path, "method": method},
                        evidence=f"Description suggests deprecation but deprecated:true not set",
                    ))

        # 5. No servers defined
        if not self.spec.get("servers"):
            signals.append(Signal(
                signal_id="GOV-005",
                category="governance",
                description="missing servers definition, no environment URLs documented",
                evidence="spec.servers array is absent",
            ))

        return _deduplicate(signals)


# ── Utility helpers ───────────────────────────────────────────────────────────

def _iter_operations(path_item: dict):
    """Yield (method, operation_dict) pairs for a path item."""
    http_methods = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
    for method, operation in (path_item or {}).items():
        if method.lower() in http_methods and isinstance(operation, dict):
            yield method.lower(), operation


def _operation_has_scopes(operation: dict, security_schemes: dict) -> bool:
    """Check if the operation uses OAuth2 scopes."""
    op_security = operation.get("security", [])
    for req in op_security:
        for scheme_name, scopes in req.items():
            scheme = security_schemes.get(scheme_name, {})
            if scheme.get("type") == "oauth2" and scopes:
                return True
    return False


def _response_is_array(responses: dict) -> bool:
    """Heuristic: check if 200 response returns an array schema."""
    ok_resp = responses.get("200", {}) or {}
    for media, media_obj in (ok_resp.get("content", {}) or {}).items():
        schema = media_obj.get("schema", {})
        if schema.get("type") == "array":
            return True
        if schema.get("$ref", "").lower().endswith("list"):
            return True
    return False


def _collect_all_property_names(components: dict) -> set:
    """Collect all schema property names for convention analysis."""
    names = set()
    for schema in (components.get("schemas", {}) or {}).values():
        names.update((schema.get("properties") or {}).keys())
    return names


def _has_mixed_conventions(names: set) -> bool:
    """Detect if both camelCase and snake_case are used."""
    camel = sum(1 for n in names if re.search(r"[a-z][A-Z]", n))
    snake = sum(1 for n in names if "_" in n)
    return camel > 0 and snake > 0 and min(camel, snake) >= 2


def _deduplicate(signals: list[Signal]) -> list[Signal]:
    """Remove duplicate signals by signal_id + context."""
    seen, unique = set(), []
    for s in signals:
        key = f"{s.signal_id}:{s.context.get('path','')}{s.context.get('method','')}"
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique
