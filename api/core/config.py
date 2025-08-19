# api/core/config.py
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 기본 실행 환경
    env: str = Field("development", alias="ENV")

    # CORS
    allowed_origins: str = Field("*", alias="ALLOWED_ORIGINS")

    # Redis
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db_sess: int = Field(0, alias="REDIS_DB_SESS")
    redis_password: str | None = Field(None, alias="REDIS_PASSWORD")

    # Postgres
    postgres_host: str = Field("localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_database: str = Field("chatbot", alias="POSTGRES_DATABASE")
    postgres_user: str = Field("chatbot", alias="POSTGRES_USER")
    postgres_password: str = Field("chatbot", alias="POSTGRES_PASSWORD")
    postgres_scheme: str = Field("postgresql+asyncpg", alias="POSTGRES_SCHEME")

    # 벡터/임베딩/키
    pgvector_collection: str = Field("kb_default", alias="PGVECTOR_COLLECTION")
    embedding_model: str = Field("upskyy/bge-m3-korean", alias="EMBEDDING_MODEL")
    openai_api_key: SecretStr | None = Field(None, alias="OPENAI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",                 # 필요 시 ".env.test" 등으로 변경 가능
        env_file_encoding="utf-8",
        case_sensitive=False,            # 대소문자 구분 없이 매핑
        extra="ignore",                  # 정의되지 않은 키는 무시(에러 방지)
    )

    # 기존 코드가 settings.ALLOWED_ORIGINS로 접근하더라도 깨지지 않게 호환 프로퍼티 제공
    @property
    def ALLOWED_ORIGINS(self) -> str:
        return self.allowed_origins


settings = Settings()
