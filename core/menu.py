from InquirerPy import inquirer


def main_menu():

    return inquirer.select(
        message="Zabbix Tools",
        choices=[
            "Hosts",
            "Macros",
            "Templates",
            "Database tools",
            "Exit"
        ],
    ).execute()