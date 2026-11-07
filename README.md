# PromptSolution

> 저장소 이름: AIIncidentKnowledgeBase · 프로젝트 이름: PromptSolution

> **연구 상태 안내(2026-11-08):** 이 저장소는 오류 기록 도구(CLI, 템플릿, 분류 체계, 예시)이며 **연구 결과나 효과 측정은 없다.** 아래 '왜 필요한가'와 로드맵의 효과(같은 실수의 반복 감소, 해결 시간 단축 등)는 시험하지 않은 설계상의 기대이며 근거가 없다. 분류 체계 10종도 설계자의 판단이고 실제 기록이나 문헌과 대조하지 않았다. 이 저장소는 새롭다는 주장을 하지 않는다. 그 위에 상태 문서를 AI(Claude)가 초안으로 더했고, 사람의 검토 전이다. 진행 기록은 [docs/00-progress-log.md](docs/00-progress-log.md).

**기업용 AI의 오류를 기록·분류하고, 원인과 수정된 프롬프트, 대응 방법을 팀원과 공유하는 솔루션.**

*Record, classify and share enterprise-AI failures: what went wrong, why, the fixed prompt, and how to mitigate it.*

## 현재 상태 (2026-11-08)

| 단계 | 상태 |
|---|---|
| 도구(`add`, `list`, `show`, `search`, `status`, `report`, `validate`), 기록 템플릿, 분류 체계 10종, 팀 워크플로 문서, 로드맵, 예시 3건 | 있음. 단위 시험 7개가 통과하고 예시 3건은 `validate`를 통과한다(2026-11-08, Python 3.13에서만 확인했다) |
| 효과 측정(재발률, 해결 시간 등 로드맵 v0.4의 지표) | 하지 않았다. 측정 도구도 없다 |
| 분류 체계의 타당성(10종의 겹침과 빠짐) | 확인하지 않았다. 겹치는 분류가 있다고 [분류 문서](docs/taxonomy.md)와 진행 기록에 적었다 |
| 연구 질문과 선행연구 조사 | 없다. 이 저장소는 연구가 아니라 도구로 다룬다(AI 제안, 사람 검토 전) |
| 회사 인수인계 키트(CompanyToAI)와의 연결 | 후보만 적었다. 로드맵 v1.0 항목이며 구현하지 않았다 |

단계별 기록과 사람이 정할 일은 [docs/00-progress-log.md](docs/00-progress-log.md)에 있다.

## 왜 필요한가
회사에서 AI를 쓰면 같은 실수가 팀마다, 사람마다 반복됩니다. 누군가 프롬프트를 고쳐도 그 지식은 채팅창과 개인 메모에 묻힙니다.
PromptSolution은 오류 한 건을 **증상 → 원인 → 문제 프롬프트 → 수정된 프롬프트 → 대응 방법**의 한 레코드로 남겨 팀의 자산으로 만듭니다.

레코드는 사람이 읽을 수 있는 JSON 파일(`INC-0001.json`)이라 Git으로 변경 이력, 리뷰, 공유를 그대로 쓸 수 있습니다.

## 빠른 시작
Python 3.9+ 만 있으면 됩니다(외부 의존성 없음).

```bash
pip install -e .

# 오류 등록
promptsolution add --title "존재하지 않는 환불 규정 인용" --category hallucination \
  --severity high --model company-llm --symptom "없는 조항 번호를 인용함" --tags 환불,정책

# 목록 / 상세 / 검색
promptsolution list --status open
promptsolution show INC-0001
promptsolution search 환불

# 원인 분석 후 수정 내용 기록하며 해결 처리
promptsolution status INC-0001 resolved --fixed-prompt "근거 문서에 없으면 '문서에 없음'이라고 답하세요."

# 팀 공유용 리포트 / 스키마 검사
promptsolution report -o reports/weekly.md
promptsolution validate
```

기본 저장 위치는 `./incidents` 입니다(`--dir` 로 변경). `--dir` 는 하위 명령 **앞**에 씁니다: `promptsolution --dir examples/incidents list`. 사용 예시는 [examples/incidents](examples/incidents) 에 있습니다.
설치 없이: `PYTHONPATH=src python -m promptsolution --help`

## 기록 항목
| 필드 | 설명 |
|---|---|
| category | 오류 분류 10종 ([taxonomy](docs/taxonomy.md)) |
| severity / status | low~critical / open, mitigated, resolved, wontfix |
| symptom | 어떤 오류가 났는지 |
| root_cause | 왜 났는지 |
| bad_prompt / fixed_prompt | 문제의 프롬프트와 수정본 |
| mitigation | 프롬프트 외 대응(검수 단계, 규칙, 데이터 보강 등) |
| tags / reporter / model | 검색·책임·재현 정보 |

`resolved` 로 바꾸려면 `fixed_prompt` 또는 `mitigation` 이 반드시 있어야 합니다. "고쳤다"만 남는 기록을 막기 위해서입니다.

## 문서
- [오류 분류 체계](docs/taxonomy.md)
- [팀 운영 워크플로](docs/workflow.md)
- [로드맵 — 프로젝트로 발전시키는 방향](docs/roadmap.md)
- [기록 템플릿](templates/incident.md)
- [진행 기록(AI 초안)](docs/00-progress-log.md)

## 테스트
```bash
python -m unittest discover tests
```

## 보안 주의
오류 기록에는 고객 정보나 사내 기밀이 섞이기 쉽습니다. 프롬프트·출력을 기록하기 전에 마스킹하고, 실제 `incidents/` 폴더는 공개 저장소에 올리지 마세요(`.gitignore` 에서 제외됨).

## 라이선스
MIT
