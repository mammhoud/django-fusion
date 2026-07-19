from shared.node_base import BaseNodeAgent, BaseNodeCommand

class Command(BaseNodeCommand):
    help = "Run the solo POS Portal node agent"

    def get_agent(self, options):
        return BaseNodeAgent(
            node_id=options["node_id"],
            master_url=options["master"],
            interval=options["interval"],
        )

