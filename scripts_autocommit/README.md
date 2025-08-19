# AutoCommit 설정 가이드
- AutoCommit은 커밋 시 자동으로 메시지를 생성해주는 도구입니다.
- OpenAI API를 기반으로 커밋 메시지를 생성하며, git commit만 입력하면 자동으로 메시지를 완성합니다.

## 준비사항
- conda 또는 miniconda가 설치된 환경이어야 합니다.
- OpenAI API 키가 필요합니다.

## 최초 세팅시 

1. scripts_autocommit 디렉토리를 본인이 작업할 레포지토리 최상단에 위치시킵니다.
2. cd scripts_autocommit 으로 해당 디렉토리 내로 이동합니다.
3. cp .env.example .env 으로 .env를 생성합니다.
4. .env 파일 내 OPENAI_API_KEY 항목에 본인의 OpenAI API 키를 입력합니다.
5. bash setup_git_hook.sh
6. pip install -r requirements.txt
	- 기본적으로 openai와 python-dotenv만 설치됩니다.
	- Base 환경에 설치해도 무방하지만, 별도 가상환경을 사용하셔도 괜찮습니다.

## 사용법
- git commit 명령어를 입력하면 자동으로 커밋 메시지가 생성됩니다.
- 자동 생성된 메시지가 적절하지 않을 경우, 직접 수정할 수 있습니다.