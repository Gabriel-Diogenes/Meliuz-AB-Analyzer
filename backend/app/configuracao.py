from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DIRETORIO_BACKEND = Path(__file__).resolve().parent.parent

MODELOS_GEMINI_PERMITIDOS = (
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
)
MODELO_GEMINI_PADRAO = MODELOS_GEMINI_PERMITIDOS[0]


class Configuracoes(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(DIRETORIO_BACKEND / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    chave_gemini: str = Field(default="", validation_alias="GEMINI_API_KEY")
    modelo_gemini: str = Field(default=MODELO_GEMINI_PADRAO, validation_alias="GEMINI_MODEL")
    id_planilha_google: str = Field(default="", validation_alias="GOOGLE_SHEETS_ID")
    json_conta_servico_google: str = Field(default="", validation_alias="GOOGLE_SERVICE_ACCOUNT_JSON")
    caminho_csv_rastreamento: str = Field(default="output/tracking.csv", validation_alias="TRACKING_CSV_PATH")
    diretorio_relatorios: str = Field(default="output/reports", validation_alias="REPORTS_DIR")


configuracoes = Configuracoes()
