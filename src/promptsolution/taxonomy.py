"""Controlled vocabularies for incident records. Keep in sync with docs/taxonomy.md."""

CATEGORIES = {
    "hallucination": "근거 없는 사실·수치·출처를 만들어 냄",
    "instruction-ignored": "프롬프트의 명시적 지시나 제약을 무시함",
    "format-violation": "요구한 출력 형식(JSON, 표, 길이 등)을 어김",
    "context-missing": "필요한 회사/업무 맥락이 없어서 틀린 답을 함",
    "outdated-info": "낡은 정보를 현재 사실처럼 말함",
    "over-refusal": "정상 업무인데 불필요하게 거절하거나 회피함",
    "unsafe-output": "개인정보·기밀·부적절한 내용을 출력함",
    "reasoning-error": "계산·논리·순서 추론이 틀림",
    "tool-misuse": "도구/검색/함수 호출을 잘못 사용함",
    "inconsistency": "같은 입력에 답이 달라지거나 이전 답과 모순됨",
}

SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES = ["open", "mitigated", "resolved", "wontfix"]

REQUIRED_FIELDS = [
    "id", "title", "created", "category", "severity", "status",
    "model", "symptom", "root_cause", "bad_prompt", "fixed_prompt", "mitigation",
]
