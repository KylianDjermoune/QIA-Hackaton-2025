from application import ServerProgram,ClientProgram

from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

# import network configuration from file
cfg = StackNetworkConfig.from_file("config.yaml")

# Initialize protocol programs
server_program = ServerProgram()
client_program = ClientProgram()

# Map each network node to its corresponding protocol program
programs = {"Server": server_program,
            "Client": client_program}

# Run the simulation
run(
    config=cfg,
    programs=programs,
    num_times=1,
)
