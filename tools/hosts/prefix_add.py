from InquirerPy import inquirer
from core.zabbix_api import ZabbixAPI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

console = Console()

TOOL = {
    "name": "Add prefix to hosts",
    "category": "Hosts",
    "description": "Add prefix to host names",
    "dangerous": False
}

def collect_inputs():
    group = inquirer.text(
        message="Hostgroup name:"
    ).execute()

    prefix = inquirer.text(
        message="Prefix:"
    ).execute()

    return {
        "group": group,
        "prefix": prefix
    }

def run(env, inputs):
    console.print(f"[bold yellow]Environment:[/bold yellow] {env['name']}")

    group = inputs["group"]
    prefix = inputs["prefix"]

    zbx_cfg = env["config"]["zabbix"]

    zapi = ZabbixAPI(
        url=zbx_cfg["url"],
        username=zbx_cfg["username"],
        password=zbx_cfg["password"]
    )

    zapi.login()

    groups = zapi.call(
        "hostgroup.get",
        {
            "filter": {
                "name": group
            }
        }
    )

    if not groups:
        console.print("[red]Hostgroup not found[/red]")
        return

    groupid = groups[0]["groupid"]

    hosts = zapi.call(
        "host.get",
        {
            "groupids": groupid,
            "output": ["hostid", "host"]
        }
    )

    console.print(f"[cyan]{len(hosts)} hosts found[/cyan]")

    lines = []

    total = len(hosts)
    lines.append(f"\nHosts in selected group: {group} ({total})")
    lines.append("-" * 60)
    lines.append("")

    for i, host in enumerate(hosts, start=1):
        old_name = host["host"]
        new_name = f"{prefix}{old_name}"

        lines.append(
            f"[dim][{i}/{total}][/dim] [red]{old_name}[/red] -> [green]{new_name}[/green]"
        )

    with console.pager(styles=True):
        for line in lines:
            console.print(line)
    console.print("")

    confirm = inquirer.confirm(
        message="Apply prefix to these hosts?",
        default=False
    ).execute()

    if not confirm:
        console.print("[yellow]Operation cancelled[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        task = progress.add_task(
            "Updating hosts...",
            total=len(hosts)
        )

        for host in hosts:
            new_name = f"{prefix}{host['host']}"

            zapi.call(
                "host.update",
                {
                    "hostid": host["hostid"],
                    "host": new_name
                }
            )

            progress.advance(task)

    console.print("[green]Hosts updated[/green]")