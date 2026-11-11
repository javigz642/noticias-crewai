from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from noticias_crewai.tools.buscar_noticias import BuscarNoticiaTool


@CrewBase
class NoticieroCrew:
    """Equipo que busca titulares de noticias y escribe un informe"""

    agents: list[Agent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def investigador_noticias(self) -> Agent:
        return Agent(
            config = self.agents_config["investigador_noticias"],
            tools = [BuscarNoticiaTool()]
        )

    @agent
    def redactor_noticias(self) -> Agent:
        return Agent(
            config = self.agents_config["redactor_noticias"]
        )

    @task
    def investigar_noticias_tarea(self) -> Task:
        return Task(
            config = self.tasks_config["investigar_noticias_tarea"]
        )

    @task
    def redactar_noticias_tarea(self) -> Task:
        return Task(
            config = self.tasks_config["redactar_noticias_tarea"],
            context=[self.investigar_noticias_tarea()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            process = Process.sequential,
            verbose = True,
            output_log_file = "output/ejecucion.json"
        )