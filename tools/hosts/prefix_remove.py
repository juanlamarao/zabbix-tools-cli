from InquirerPy import inquirer
from core.zabbix_api import ZabbixAPI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

console = Console()

TOOL = {
    "name": "Remove prefix from hosts",
    "category": "Hosts",
    "description": "Remove prefix from host names",
    "dangerous": False
}


def collect_inputs():

    group = inquirer.text(
        message="Hostgroup name:"
    ).execute()

    prefix = inquirer.text(
        message="Prefix to remove:"
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

    affected_hosts = []

    for host in hosts:

        old_name = host["host"]

        if old_name.startswith(prefix):
            new_name = old_name[len(prefix):]

            affected_hosts.append({
                "hostid": host["hostid"],
                "old": old_name,
                "new": new_name
            })

    console.print(f"[cyan]{len(affected_hosts)} hosts will be updated[/cyan]")

    if not affected_hosts:
        console.print("[yellow]No hosts with this prefix found[/yellow]")
        return

    lines = []

    total = len(hosts)
    # lines.append(f"\nHosts in selected group: {group}")
    lines.append(f"\nHosts in selected group: {group} ({total})")
    lines.append("-" * 60)
    lines.append("")

    # for host in affected_hosts:

    for i, host in enumerate(hosts, start=1):
        
        lines.append(
            f"[dim][{i}/{total}][/dim] [red]{old_name}[/red] -> [green]{new_name}[/green]"
        )

    with console.pager(styles=True):
        for line in lines:
            console.print(line)

    console.print("")

    confirm = inquirer.confirm(
        message="Remove prefix from these hosts?",
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
            total=len(affected_hosts)
        )

        for host in affected_hosts:

            zapi.call(
                "host.update",
                {
                    "hostid": host["hostid"],
                    "host": host["new"]
                }
            )

            progress.advance(task)

    console.print("[green]Hosts updated[/green]")