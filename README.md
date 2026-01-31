# Team Agents

멀티 에이전트 과제 수행 시스템

## 목적

소프트웨어 엔지니어의 관점에서 다양한 과제를 AI 주도로 해결하고 개선하기 위한 프로젝트입니다.

## 개발환경

**애플 실리콘 기반 macOS 이외의 플랫폼/아키텍처는 테스트되지 않았습니다.**

### Claude Code

공동 작업자입니다. 같이 의논하고 고민하고 해결하는데 사용합니다.

설치: [Claude Code Overview](https://code.claude.com/docs/en/overview)

설치 확인:

```bash
claude --version # 2.1.27 (Claude Code)
```

### uv

파이썬 기반 환경의 프로젝트를 관리 하기 위한 도구입니다.

설치: [Installing uv](https://docs.astral.sh/uv/getting-started/installation/)

설치 확인:

```bash
uv --version # uv 0.9.28 (0e1351e40 2026-01-29)
```

### Docker

상태를 Postgres에 저장하고 모니터링하기 위한 컨테이너 관리 도구입니다.

설치: [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

설치 확인:

```bash
docker --version # Docker version 28.3.2, build 578ccf6
```

실행:

```bash
docker compose up -d
```
