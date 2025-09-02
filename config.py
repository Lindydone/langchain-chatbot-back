from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field("development", alias="ENV")

    # CORS
    allowed_origins: str = Field("*", alias="ALLOWED_ORIGINS")

    model_provider: str = Field("openai", alias="MODEL_PROVIDER")  # "openai" | "server" 
    model_name: str = Field("gpt-4o-mini", alias="MODEL_NAME")
    # Redis
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db_sess: int = Field(0, alias="REDIS_DB_SESS")
    redis_password: str = Field("", alias="REDIS_PASSWORD")

    # Postgres
    postgres_host: str = Field("localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_database: str = Field("chatbot", alias="POSTGRES_DATABASE")
    postgres_user: str = Field("chatbot", alias="POSTGRES_USER")
    postgres_password: str = Field("chatbot", alias="POSTGRES_PASSWORD")
    postgres_scheme: str = Field("postgresql+asyncpg", alias="POSTGRES_SCHEME")

    db_set: str = Field("keep", alias="DB_SET") 
     
    # 벡터/임베딩/키
    embedding_model: str = Field("upskyy/bge-m3-korean", alias="EMBEDDING_MODEL")
    openai_api_key: SecretStr | None = Field(None, alias="OPENAI_API_KEY")

    # OpenSearch
    os_scheme: str = Field("http", alias="OS_SCHEME")
    os_host: str = Field("opensearch", alias="OS_HOST")
    os_port: int = Field(9200, alias="OS_PORT")
    os_index: str = Field("rag_chunks", alias="OS_INDEX")
    os_use_auth: bool = Field(False, alias="OS_USE_AUTH")
    os_username: str | None = Field(None, alias="OS_USERNAME")
    os_password: SecretStr | None = Field(None, alias="OS_PASSWORD")

    prompt_budget: int   = Field(6000, alias="PROMPT_BUDGET")
    reply_reserve: int   = Field(500,  alias="REPLY_RESERVE")
    history_ratio: float = Field(0.7,  alias="HISTORY_RATIO")

    model_config = SettingsConfigDict(
        env_file=".env",                
        env_file_encoding="utf-8",
        case_sensitive=False,            # 대소문자 구분 없이 매핑
        extra="ignore",                  # 정의되지 않은 키는 무시(에러 방지)
    )


    @property
    def ALLOWED_ORIGINS(self) -> str:
        return self.allowed_origins



settings = Settings()
