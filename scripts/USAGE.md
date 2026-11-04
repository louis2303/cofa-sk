# 보조 도구 사용 안내

필요할 때만 실행한다. 모든 도구는 Python 3 표준 라이브러리 기반이다. 실행 중 필수 의존성 설치나 인터넷 요청을 하지 않는다.

```bash
python scripts/preflight.py --root .
python scripts/data_profile.py path/to/data.csv
python scripts/data_profile.py path/to/data.json --max-rows 200000
python -m unittest discover -s tests -v
python scripts/check_results.py evidence.json --root .
```

- **preflight.py**: Python/Node/npm/Git의 PATH, 작업 디렉터리 쓰기 가능 여부와 주요 파일 유무를 점검한다. Node/npm/Git 부재는 비치명적 WARN이다. 생성한 임시 파일은 자동 삭제한다.
- **data_profile.py**: CSV/JSON 배열을 읽어 행 수, 컬럼, 결측, 중복, 숫자 판별 비율을 출력한다. 비율은 **해당 열의 실제 비결측 값 전체**를 분모로 계산한다. 기본 최대 100,000행이며 대용량 데이터는 메모리 사용량에 주의한다. 데이터 원본을 수정하지 않는다.
- **check_results.py**: 사용자가 작성한 테스트 실행 증거 JSON을 검사한다. **테스트를 실행하지 않으며**, 기록 내용이 진실인지 검증할 수 없다. 테스트 0건, 빈 규칙, 비정상 종료, 요구 산출물 미존재 시 FAIL 처리한다.

```json
{
  "checks": [
    {"command": "python -m unittest discover -s tests -v", "test_count": 9, "exit_code": 0, "status": "passed"}
  ],
  "required_outputs": ["Docs/Prd.md"]
}
```

실제 과제에서 **방금 직접 실행한 테스트 결과**로 위 증거를 작성할 것. 예시는 통과 증명이 아니다. 단순 서류용 형식을 채워 PASS를 만드는 데 사용하지 않는다. 시험에서 허용되지 않은 자동화 도구를 실행하지 않는다.
