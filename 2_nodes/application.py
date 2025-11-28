import netsquid as ns

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class ServerProgram(Program):
    NODE_NAME = "Server"
    PEER_CLIENT = "Client"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_CLIENT],
            epr_sockets=[self.PEER_CLIENT],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_bob = context.csockets[self.PEER_CLIENT]
        # get EPR sockets
        epr_socket_bob = context.epr_sockets[self.PEER_CLIENT]
        # get connection to QNPU
        connection = context.connection

        print(f"{ns.sim_time()} ns: Hello from {self.NODE_NAME}")
        return {}

class ClientProgram(Program):
    NODE_NAME = "Client"
    PEER_SERVER = "Server"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_SERVER],
            epr_sockets=[self.PEER_SERVER],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_SERVER = context.csockets[self.PEER_SERVER]
        # get EPR sockets
        epr_socket_SERVER = context.epr_sockets[self.PEER_SERVER]
        # get connection to QNPU
        connection = context.connection

        print(f"{ns.sim_time()} ns: Hello from {self.NODE_NAME}")
        return {}