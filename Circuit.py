
class Circuit:
    
        def __init__(self, name, nodes, components):
            self.name = name
            self.nodes = nodes
            self.components = components
    
        def __str__(self):
            return "Circuit: " + self.name + " with " + str(len(self.nodes)) + " nodes and " + str(len(self.components)) + " components"

class Resistor(Circuit):
    def __init__(self, name, value, node1, node2):
        Circuit.__init__(self, name, value, [node1, node2])

    def get_current(self):
        return (self.node1.get_voltage() - self.node2.get_voltage()) / self.value

    def get_power(self):
        return self.get_current() * (self.node1.get_voltage() - self.node2.get_voltage())

    def get_voltage(self):
        return self.get_current() * self.value

    def get_impedance(self):
        return self.value

    def get_admittance(self):
        return 1 / self.value

    def get_type(self):
        return "Resistor"


class Capacitor(Circuit):
    def __init__(self, name, value, node1, node2):
        Circuit.__init__(self, name, value, node1, node2)

    def get_current(self):
        return (self.node1.get_voltage() - self.node2.get_voltage()) / self.value

    def get_power(self):
        return self.get_current() * (self.node1.get_voltage() - self.node2.get_voltage())

    def get_voltage(self):
        return self.get_current() * self.value

    def get_impedance(self):
        return self.value

    def get_admittance(self):
        return 1 / self.value

    def get_type(self):
        return "Capacitor"

class Inductor(Circuit):
    def __init__(self, name, value, node1, node2):
        Circuit.__init__(self, name, value, node1, node2)

    def get_current(self):
        return (self.node1.get_voltage() - self.node2.get_voltage()) / self.value

    def get_power(self):
        return self.get_current() * (self.node1.get_voltage() - self.node2.get_voltage())

    def get_voltage(self):
        return self.get_current() * self.value

    def get_impedance(self):
        return self.value

    def get_admittance(self):
        return 1 / self.value

    def get_type(self):
        return "Inductor"

class Node:
    def __init__(self, name, voltage):
        self.name = name
        self.voltage = voltage

    def get_voltage(self):
        return self.voltage

    def get_type(self):
        return "Node"

class CircuitSolver:
    def __init__(self, circuit):
        self.circuit = circuit

    def solve(self):
        print("Solving circuit: " + self.circuit.name)
        print("Nodes: " + str(self.circuit.nodes))
        print("Components: " + str(self.circuit.components))

        # Create a matrix of the circuit
        matrix = []
        for i in range(len(self.circuit.nodes)):
            matrix.append([])
            for j in range(len(self.circuit.nodes)):
                matrix[i].append(0)
        
        # Fill the matrix with the values of the components
        for component in self.circuit.components:
            if component.get_type() == "Resistor":
                matrix[component.node1][component.node1] += 1 / component.value
                matrix[component.node1][component.node2] -= 1 / component.value
                matrix[component.node2][component.node1] -= 1 / component.value
                matrix[component.node2][component.node2] += 1 / component.value
            elif component.get_type() == "Capacitor":
                matrix[component.node1][component.node1] += 1 / component.value
                matrix[component.node1][component.node2] -= 1 / component.value
                matrix[component.node2][component.node1] -= 1 / component.value
                matrix[component.node2][component.node2] += 1 / component.value
            elif component.get_type() == "Inductor":
                matrix[component.node1][component.node1] += 1 / component.value
                matrix[component.node1][component.node2] -= 1 / component.value
                matrix[component.node2][component.node1] -= 1 / component.value
                matrix[component.node2][component.node2] += 1 / component.value
        
        # Print the matrix
        for i in range(len(self.circuit.nodes)):
            print(matrix[i])
        
        # Solve the matrix
        # TODO

class CircuitBuilder:
    def __init__(self):
        self.circuit = None
        self.nodes = []
        self.components = []

    def add_node(self, name, voltage):
        self.nodes.append(Node(name, voltage))

    def add_resistor(self, name, value, node1, node2):
        self.components.append(Resistor(name, value, node1, node2))

    def add_capacitor(self, name, value, node1, node2):
        self.components.append(Capacitor(name, value, node1, node2))

    def add_inductor(self, name, value, node1, node2):
        self.components.append(Inductor(name, value, node1, node2))

    def build(self, name):
        self.circuit = Circuit(name, self.nodes, self.components)
        return self.circuit


if __name__ == "__main__":
    circuit_builder = CircuitBuilder()
    circuit_builder.add_node("A", 0)
    circuit_builder.add_node("B", 10)
    circuit_builder.add_resistor("R1", 1, 0, 1)
    circuit_builder.add_resistor("R2", 2, 1, 0)
    circuit = circuit_builder.build("Circuit 1")
    print(circuit)
    circuit_solver = CircuitSolver(circuit)
    circuit_solver.solve()
