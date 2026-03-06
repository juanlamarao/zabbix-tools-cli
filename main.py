# main.py
from utils.terminal import clear_screen
import os
from InquirerPy import inquirer
from rich.console import Console
from rich.text import Text

from config.loader import ConfigLoader
from core.context import Context
from core.plugin_loader import PluginLoader

console = Console()

def select_profiles():
    """Lista arquivos em config/profiles e permite selecionar múltiplos"""

    profiles_dir = "config/profiles"

    profiles = [
        f.replace(".yaml", "")
        for f in os.listdir(profiles_dir)
        if f.endswith(".yaml")
    ]

    if not profiles:
        raise SystemExit("Nenhum profile encontrado em config/profiles")

    selected = inquirer.checkbox(
        message="Select environment(s)",
        choices=sorted(profiles)
    ).execute()

    if not selected:
        raise SystemExit("Nenhum ambiente selecionado")

    return selected

def show_header():
    env_names = [env["name"].upper() for env in Context.environments]

    env_text = ", ".join(env_names)

    header = Text.assemble(
        ("Zabbix Toolbox", "bold white"),
        ("  "),
        (f"ENV: {env_text}", "cyan")
    )

    console.rule(header)

def main():
    # 1) Seleciona profile e carrega config
    profiles = select_profiles()
    Context.environments = []

    for profile in profiles:

        loader = ConfigLoader(profile)
        config = loader.get()

        Context.environments.append({
            "name": profile,
            "config": config
        })

    console.print(f"Loaded environments: {', '.join(profiles)}\n")

    # 2) Descobre plugins
    plugin_loader = PluginLoader()
    plugin_loader.discover()
    categories = plugin_loader.group_by_category()

    # 3) Loop principal
    while True:
        clear_screen()
        show_header()

        category = inquirer.select(
            message="Select category",
            choices=sorted(list(categories.keys())) + ["Exit"]
        ).execute()

        if category == "Exit":
            console.print("Bye 👋")
            break

        tools = categories[category]
        tool_choices = [t["name"] for t in sorted(tools, key=lambda x: x["name"])]
        tool_choice = inquirer.select(
            message=f"Select tool ({category})",
            choices=tool_choices + ["Back"]
        ).execute()

        if tool_choice == "Back":
            continue

        # encontra plugin selecionado
        plugin = next((t for t in tools if t["name"] == tool_choice), None)
        if not plugin:
            console.print("[red]Plugin não encontrado[/red]")
            continue

        # confirmação caso seja PROD + perigoso
        # if not confirm_prod_action(plugin):
        #     console.print("[yellow]Operação abortada pelo usuário[/yellow]")
        #     continue

        # executa a tool (passa Context para que a tool possa acessar config, db, etc)
        try:
            inputs = {}

            # coletar inputs uma única vez
            if "collect_inputs" in plugin["module"].__dict__:
                inputs = plugin["module"].collect_inputs()

            for env in Context.environments:

                console.rule(f"[bold cyan]Running in {env['name']}[/bold cyan]")

                try:
                    plugin["run"](env, inputs)

                except Exception as e:
                    console.print(f"[red]Erro no ambiente {env['name']}:[/red] {e}")
        except TypeError:
            # compatibilidade: tools que não esperam context
            plugin["run"](None)
        except Exception as e:
            console.print(f"[red]Erro ao executar a tool:[/red] {e}")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()