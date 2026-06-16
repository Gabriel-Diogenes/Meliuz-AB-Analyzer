from __future__ import annotations

from typing import Any

from app.formatacao_planilha import CABECALHOS_PLANILHA

LARGURAS_COLUNAS_PX = [110, 190, 280, 95, 125, 115, 320, 320, 120]

COR_CABECALHO = {"red": 1.0, "green": 0.45, "blue": 0.0}
COR_TEXTO_CABECALHO = {"red": 1.0, "green": 1.0, "blue": 1.0}
COR_LINHA_PAR = {"red": 0.97, "green": 0.97, "blue": 0.97}
COR_LINHA_IMPAR = {"red": 1.0, "green": 1.0, "blue": 1.0}
BORDA_CELULA = {
    "style": "SOLID",
    "width": 1,
    "color": {"red": 0.82, "green": 0.82, "blue": 0.82},
}


def _definir_larguras_colunas(planilha) -> None:
    requisicoes = []
    for indice, largura in enumerate(LARGURAS_COLUNAS_PX):
        requisicoes.append(
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": planilha.id,
                        "dimension": "COLUMNS",
                        "startIndex": indice,
                        "endIndex": indice + 1,
                    },
                    "properties": {"pixelSize": largura},
                    "fields": "pixelSize",
                }
            }
        )
    if requisicoes:
        planilha.spreadsheet.batch_update({"requests": requisicoes})


def _formato_cabecalho() -> dict[str, Any]:
    return {
        "backgroundColor": COR_CABECALHO,
        "textFormat": {"bold": True, "foregroundColor": COR_TEXTO_CABECALHO, "fontSize": 10},
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE",
        "wrapStrategy": "WRAP",
        "borders": {
            "top": BORDA_CELULA,
            "bottom": BORDA_CELULA,
            "left": BORDA_CELULA,
            "right": BORDA_CELULA,
        },
    }


def _formato_linha_dados(cor_fundo: dict[str, float], negrito_decisao: bool = False) -> dict[str, Any]:
    formato: dict[str, Any] = {
        "backgroundColor": cor_fundo,
        "wrapStrategy": "WRAP",
        "verticalAlignment": "TOP",
        "textFormat": {"fontSize": 10},
        "borders": {
            "top": BORDA_CELULA,
            "bottom": BORDA_CELULA,
            "left": BORDA_CELULA,
            "right": BORDA_CELULA,
        },
    }
    if negrito_decisao:
        formato["textFormat"] = {"fontSize": 10, "bold": True}
    return formato


def ultima_linha_com_dados(planilha) -> int:
    """Ultima linha preenchida na coluna A (nao confundir com row_count da grade)."""
    return len(planilha.col_values(1))


def aplicar_layout_planilha(planilha, *, ultima_linha: int | None = None) -> None:
    """Aplica cabecalho, larguras, cores e bordas na propria planilha Google."""
    linha_final = ultima_linha if ultima_linha is not None else ultima_linha_com_dados(planilha)
    if linha_final < 1:
        linha_final = 1

    cabecalhos_atuais = [valor.strip() for valor in planilha.row_values(1) if valor.strip()]
    if cabecalhos_atuais != CABECALHOS_PLANILHA:
        planilha.update([CABECALHOS_PLANILHA], "A1:I1", value_input_option="USER_ENTERED")

    planilha.freeze(rows=1)
    _definir_larguras_colunas(planilha)

    formatos = [{"range": "A1:I1", "format": _formato_cabecalho()}]

    for numero_linha in range(2, linha_final + 1):
        cor = COR_LINHA_PAR if numero_linha % 2 == 0 else COR_LINHA_IMPAR
        formatos.append(
            {
                "range": f"A{numero_linha}:I{numero_linha}",
                "format": _formato_linha_dados(cor),
            }
        )

    planilha.batch_format(formatos)

    alinhamentos = [
        {"range": f"A2:A{linha_final}", "format": {"horizontalAlignment": "CENTER"}},
        {"range": f"D2:D{linha_final}", "format": {"horizontalAlignment": "CENTER"}},
        {"range": f"F2:F{linha_final}", "format": {"horizontalAlignment": "CENTER"}},
        {"range": f"I2:I{linha_final}", "format": {"horizontalAlignment": "CENTER"}},
    ]
    planilha.batch_format(alinhamentos)
