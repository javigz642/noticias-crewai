from pathlib import Path

from noticias_crewai.crew import NoticieroCrew


TEMA_POR_DEFECTO = "inteligencia artificial"


def run():
    # Si el usuario pulsa Enter sin escribir nada, "" or "..." devuelve el tema por defecto
    tema = input(f"Introduce el tema del que investigar [{TEMA_POR_DEFECTO}]: ").strip() or TEMA_POR_DEFECTO
    num_noticias = 5
    noticiero_crew = NoticieroCrew().crew()
    # CrewAI no crea la carpeta del output_log_file: hay que crearla antes del kickoff
    Path("output").mkdir(parents=True, exist_ok=True)
    resultado = noticiero_crew.kickoff(inputs={"tema": tema, "num_noticias": num_noticias})

    # Separador para encontrar el resumen final entre todo el texto de verbose
    print("\n" + "=" * 60)
    print(f"RESUMEN FINAL: {tema}")
    print("=" * 60)
    print(resultado.raw)


if __name__ == "__main__":
    run()

