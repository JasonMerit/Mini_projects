
class Player(object):

    def __init__(self, name, health, damage, armor, inventory):
        self.name = name
        self.health = health
        self.damage = damage
        self.armor = armor
        self.inventory = inventory
    
    def attack(self, enemy):
        enemy.health -= self.damage
    
    def defend(self, enemy):
        self.health -= enemy.damage - self.armor

class Enemy(object):
    
        def __init__(self, name, health, damage, armor, inventory):
            self.name = name
            self.health = health
            self.damage = damage
            self.armor = armor
            self.inventory = inventory
        
        def attack(self, player):
            player.health -= self.damage
        
        def defend(self, player):
            self.health -= player.damage - self.armor

class Room(object):
    def __init__(self, name, description, north=None, south=None, east=None, west=None):
        self.name = name
        self.description = description
        self.north = north
        self.south = south
        self.east = east
        self.west = west
    
    def enter(self):
        print(self.description)
    
    def exit(self):
        print("Exiting room")
    
    def get_name(self):
        return self._name
    
    def place_enemy(self, enemy):
        self.enemy = enemy
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def process_command(self, command):
        if command == "north":
            if self.north:
                return self.north
            else:
                print("Room not found")
                return self
        elif command == "south":
            if self.south:
                return self.south
            else:
                print("Room not found")
                return self
        elif command == "east":
            if self.east:
                return self.east
            else:
                print("Room not found")
                return self
        elif command == "west":
            if self.west:
                return self.west
            else:
                print("Room not found")
                return self
        elif command == "quit":
            return "quit"
        else:
            print("Unknown command")
            return None
    
class TextAdventure(object):
    def __init__(self):
        self.player = Player("Albert", 1000, 10, 0, [])
        self.rooms = {}
        for i in range(4):
            self.add_room(Room("Room " + str(i), "Room " + str(i)))
        
        self.rooms["Room 0"].north = self.rooms["Room 1"]
        self.rooms["Room 1"].south = self.rooms["Room 0"]
        self.rooms["Room 1"].east = self.rooms["Room 2"]
        self.rooms["Room 2"].west = self.rooms["Room 1"]
        self.rooms["Room 2"].north = self.rooms["Room 3"]
        self.rooms["Room 3"].south = self.rooms["Room 2"]

        self.current_room = self.rooms["Room 0"]

    def add_room(self, room):
        self.rooms[room.name] = room

    def set_current_room(self, room_name):
        self.current_room = self.rooms[room_name]
    
    def print_map(self):
        print("Map:")
        for room in self.rooms:
            print(room)
            if self.rooms[room].north:
                print("  North: " + str(self.rooms[room].north))
            if self.rooms[room].south:
                print("  South: " + str(self.rooms[room].south))
            if self.rooms[room].east:
                print("  East: " + str(self.rooms[room].east))
            if self.rooms[room].west:
                print("  West: " + str(self.rooms[room].west))

    def play(self):
        while True:
            print(self.current_room)
            command = input("> ")
            if command == "quit":
                break
            elif command == "map":
                self.print_map()
            self.current_room = self.current_room.process_command(command)
    


if __name__ == "__main__":
    game = TextAdventure()
    game.play()
    
