import netsquid as ns

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from netqasm.sdk.qubit import Qubit
from squidasm.util.routines import teleport_recv, teleport_send
from squidasm.sim.stack.program import ProgramContext

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

        local_qubit_1 = Qubit(connection)
        local_qubit_2 = Qubit(connection)

        #Plus states
        local_qubit_1.H()
        local_qubit_2.H()

        for _ in range(3):
            #Tagging
            local_qubit_1.cphase(local_qubit_2)
            local_qubit_1.rot_Z(0, 0)
            local_qubit_2.rot_Z(1, 0)

            #Inversion
            local_qubit_1.rot_Z(3, 1)
            local_qubit_1.H()
            local_qubit_1.cphase(local_qubit_2)
            local_qubit_2.H()

        r1 = local_qubit_1.measure()
        r2 = local_qubit_2.measure()

        yield from connection.flush()

        print(f"Local qubits: {r1}, {r2}")
        
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

        plus_qubit = Qubit(connection)
        plus_qubit.H()

        teleport_send(plus_qubit, context, self.PEER_SERVER)

        return {}