import importlib
import pkgutil

class PluginLoader:
    def __init__(self, tools_package="tools"):
        self.tools_package = tools_package
        self.plugins = []

    def discover(self):
        """
        Descobre automaticamente todos os plugins dentro do pacote tools
        """

        package = importlib.import_module(self.tools_package)

        for _, module_name, _ in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + "."
        ):
            module = importlib.import_module(module_name)

            # valida plugin
            if hasattr(module, "TOOL") and hasattr(module, "run"):

                tool_meta = module.TOOL

                plugin = {
                    "name": tool_meta.get("name", module_name),
                    "category": tool_meta.get("category", "Other"),
                    "description": tool_meta.get("description", ""),
                    "module": module,
                    "run": module.run
                }

                self.plugins.append(plugin)

        return self.plugins

    def group_by_category(self):
        """
        Agrupa plugins por categoria
        """

        categories = {}

        for plugin in self.plugins:
            category = plugin["category"]

            if category not in categories:
                categories[category] = []

            categories[category].append(plugin)

        return categories