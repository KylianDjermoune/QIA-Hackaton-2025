import netsquid as ns

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from netqasm.sdk.qubit import Qubit
from squidasm.util.routines import teleport_recv, teleport_send
from squidasm.sim.stack.program import ProgramContext

from math import pi
from random import randint

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
        csocket_CLIENT = context.csockets[self.PEER_CLIENT]
        # get EPR sockets
        epr_socket_CLIENT = context.epr_sockets[self.PEER_CLIENT]
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

        print(f"[SERVER] Local qubits: {r1}, {r2}")
        
        received_qubit_1 = yield from teleport_recv(context, self.PEER_CLIENT)
        received_qubit_2 = yield from teleport_recv(context, self.PEER_CLIENT)
        received_qubit_3 = yield from teleport_recv(context, self.PEER_CLIENT)
        received_qubit_4 = yield from teleport_recv(context, self.PEER_CLIENT)

        #Create the cluster state
        received_qubit_1.cphase(received_qubit_2)
        received_qubit_1.cphase(received_qubit_3)
        received_qubit_2.cphase(received_qubit_3)
        received_qubit_3.cphase(received_qubit_4)

        #Get the angles of measurement
        delta_2 = yield from csocket_CLIENT.recv()
        delta_3 = yield from csocket_CLIENT.recv()

        print(f"[SERVER] Received angles of measurement: {delta_2}, {delta_3}")
        
        #Measure with angle delta
        #Tagging by measuring 2 and 3
        received_qubit_2.rot_Z(angle=delta_2)
        received_qubit_2.measure()
        received_qubit_3.rot_Z(angle=delta_3)
        received_qubit_3.measure()
        yield from connection.flush()

        #Retrieve tagged state by measuring 1 and 4
        received_qubit_1.rot_Z(1, 1) #angle = pi/2
        r_2 = received_qubit_1.measure()
        received_qubit_4.rot_Z(1, 1) #angle = pi/2
        r_3 = received_qubit_4.measure()
        yield from connection.flush()

        print(f"[SERVER] Results: {r_2}, {r_3}")

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

    def theta_state(self, theta, connection):
        qubit = Qubit(connection)
        qubit.H()
        qubit.rot_Z(angle=theta)
        return qubit

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_SERVER = context.csockets[self.PEER_SERVER]
        # get EPR sockets
        epr_socket_SERVER = context.epr_sockets[self.PEER_SERVER]
        # get connection to QNPU
        connection = context.connection

        print(f"{ns.sim_time()} ns: Hello from {self.NODE_NAME}")

        #Initialize the angles
        theta_1 = 0
        theta_2 = 7 * pi / 4
        theta_3 = pi / 4
        theta_4 = 0

        #Create the qubits
        theta_1_qubit = self.theta_state(theta_1, connection)
        theta_2_qubit = self.theta_state(theta_2, connection)
        theta_3_qubit = self.theta_state(theta_3, connection)
        theta_4_qubit = self.theta_state(theta_4, connection)

        #Send the qubits
        yield from teleport_send(theta_1_qubit, context, self.PEER_SERVER)
        yield from teleport_send(theta_2_qubit, context, self.PEER_SERVER)
        yield from teleport_send(theta_3_qubit, context, self.PEER_SERVER)
        yield from teleport_send(theta_4_qubit, context, self.PEER_SERVER)

        r2: int = randint(0, 1)
        r3: int = randint(0, 1)

        #Angle for tagging 01
        phi_2 = -pi / 2
        phi_3 = pi

        delta_2 = phi_2 + pi * r2 + theta_2
        delta_3 = phi_3 + pi * r3 + theta_3

        print(f"[CLIENT] delta_2 = {delta_2}")
        print(f"[CLIENT] delta_3 = {delta_3}")

        csocket_SERVER.send(delta_2)
        csocket_SERVER.send(delta_3)

        return {}