



class GirlFriendSimulator(object):
    """Simulate a girlfriend"""

    def __init__(self):
        self._girlfriend = None
    
    def kiss(self):
        print("Kiss")
    
    def hug(self):
        print("Hug")
    
    def make_sanwich(self):
        print("Making sanwich")
        
    
    def start_chat(self):
        print("Chatting with girlfriend")
        response = input("Enter your message:\n>")
        while response != "":
            if response == "":
                print("Stopped chatting")
            elif response == "kiss":
                self.kiss()
            elif response == "hug":
                self.hug()
            else:
                print("Unknown command")
            response = input("Enter your message:\n>")
        
    def start(self):
        print("Starting girlfriend simulator")
        self._girlfriend = input("Enter your girlfriend's name: ")
        print("Your girlfriend is " + self._girlfriend)
        self.start_chat()
    
    def __del__(self):
        print("Goodbye")
    
    def __str__(self):
        return "GirlFriendSimulator object"
    
    def __repr__(self):
        return "GirlFriendSimulator object"

    def get_girlfriend(self):
        return self._girlfriend
    
    def set_girlfriend(self, value):
        self._girlfriend = value
    
    def del_girlfriend(self):
        del self._girlfriend
    
    girlfriend = property(get_girlfriend, set_girlfriend, del_girlfriend, "I'm your girlfriend")


gf = GirlFriendSimulator()
gf.girlfriend = "Samantha"
gf.start()
