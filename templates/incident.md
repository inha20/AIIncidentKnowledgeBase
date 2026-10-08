# AI 오류 기록 템플릿

CLI 대신 문서로 먼저 정리하거나 이슈 트래커에 붙여 넣을 때 사용합니다. 항목은 `promptsolution add` 옵션과 1:1 대응합니다.

```
제목(title):
분류(category): hallucination | instruction-ignored | format-violation | context-missing |
               outdated-info | over-refusal | unsafe-output | reasoning-error |
               tool-misuse | inconsistency
심각도(severity): low | medium | high | critical
모델(model):
보고자(reporter):
태그(tags): 쉼표로 구분

증상(symptom):
  - 기대한 결과:
  - 실제 결과:

원인(root_cause):
  - 맥락 부족 / 지시 모호 / 형식 불명확 / 모델 한계 중 무엇인가

문제 프롬프트(bad_prompt):   ※ 민감정보 마스킹

수정된 프롬프트(fixed_prompt):

대응 방법(mitigation):
  - 프롬프트 외 조치(검수 단계, 규칙, 데이터 보강 등)

검증:
  - 원래 입력으로 재시험 결과:
  - 유사 입력 재시험 결과:
```
