먼저 [README](/README.md)를 읽고 이 프로젝트의 방향성을 이해하세요.

**도구**

- `uv`: 파이썬 환경 및 실행을 위한 CLI 도구.

**Don't**: `python` 및 `pip`를 직접 실행하지 마세요.
**Do**: `uv run` 및 `uv add`를 사용하세요.

- `psql`: Postgres 상태 조회 관리 CLI 도구.
아래 예제처럼 `-h localhost -U postgres` 인자를 넣어야 사용이 가능합니다.

```bash
psql -h localhost -U postgres -c "select 1"
 ?column? 
----------
        1
(1 row)
```
