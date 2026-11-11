from pydantic import BaseModel, Field
from typing import Type
from crewai.tools import BaseTool

from email.utils import parsedate_to_datetime
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


def buscar_en_google_news(palabras_clave: str, num_noticias: int) -> list[str]:
    url = f"https://news.google.com/rss/search?q={quote(palabras_clave)}&hl=es&gl=ES&ceid=ES:es"
    peticion = Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(peticion, timeout=15) as respuesta:
        datos_bytes = respuesta.read()
        xml_texto = datos_bytes.decode("utf-8")
    raiz = ET.fromstring(xml_texto)
    noticias = raiz.findall(".//item")[:num_noticias]
    lista_noticias_formato = []
    for i, noticia in enumerate(noticias, 1):
        medio = noticia.findtext("source")
        titulo = noticia.findtext("title").removesuffix(f" - {medio}")
        # El RSS trae la fecha como "Tue, 10 Nov 2026 18:37:19 GMT": la pasamos a "10/11/2026"
        # (más corta = menos tokens para el LLM, y en formato español)
        fecha_rss = noticia.findtext("pubDate")
        fecha = parsedate_to_datetime(fecha_rss).strftime("%d/%m/%Y") if fecha_rss else "sin fecha"
        enlace = noticia.findtext("link")
        lista_noticias_formato.append(f"{i}. {titulo} | Medio: {medio} | Fecha: {fecha} | Enlace: {enlace}")
    return lista_noticias_formato


class NoticiaInput(BaseModel):
    """Esquema de input para las noticias"""
    palabras_clave: str = Field(...,description="Palabras clave de tema en concreto sobre lo que buscar noticias en Español")
    num_noticias: int = Field(gt=1, lt=10, default=5, description="Numero de noticias que se traen")


class BuscarNoticiaTool(BaseTool):
    name: str = "Buscador de noticias"
    description: str = ("Consulta Google News RSS para saber noticias actuales. "
                        "Devuelve para cada noticia: titulo, medio, fecha y enlace. "
                        "Úsala cuando necesites buscar noticias sobre algun tema específico.")
    args_schema: Type[BaseModel] = NoticiaInput

    def _run(self, palabras_clave: str, num_noticias: int) -> str:
        try:
            lista_noticias = buscar_en_google_news(palabras_clave, num_noticias)
        except Exception as e:
            return f"Error al consultar la noticia: {e}. Prueba con otro tema."
        if not lista_noticias:
            return f"No se han encontrado noticias de '{palabras_clave}'. Prueba con otro tema."

        return "\n".join(lista_noticias)

