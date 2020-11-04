import numpy as np
import math

_CITIES = (("Bordeaux", (44.833333,-0.566667)), ("Paris",(48.8566969,2.3514616)),("Nice",(43.7009358,7.2683912)),
("Lyon",(45.7578137,4.8320114)),("Nantes",(47.2186371,-1.5541362)),("Brest",(48.4,-4.483333)),("Lille",(50.633333,3.066667)),
("Clermont-Ferrand",(45.783333,3.083333)),("Strasbourg",(48.583333,7.75)),("Poitiers",(46.583333,0.333333)),
("Angers",(47.466667,-0.55)),("Montpellier",(43.6,3.883333)),("Caen",(49.183333,-0.35)),("Rennes",(48.083333,-1.683333)),("Pau",(43.3,-0.366667)))

# Paramètres
alpha = 0.6
beta = 0.8
gamma = 0.1
Q = 100
NB_ANTS = 100
NB_RUNS = 100
p = 0.9

# Distance between 2 points
def distance(a,b):
    (x1,y1),(x2,y2) = (a,b)
    return np.sqrt((x1-x2)**2+(y1-y2)**2) 


# Data structure for pheromons
class Pheromons():
    
    _edges = None
    _p = None
    
    def __init__(self, p = 0.9):
        
        self._edges = {}
        self._p = p
        
        for city in _CITIES:
            
            self._edges[city[0]] = {}
            
            for city_bis in _CITIES:
                
                if(city != city_bis):
  
                    self._edges[city[0]][city_bis[0]] = 1
    
        #print(self._edges)
        
    # Method for pheromon evaporation after each loop
    def evaporate(self):
        for key, value in self._edges.items():
            for city in value:
                value[city] = value[city] * self._p
    

    def __getitem__(self, key):
        return self._edges[key]

    def __setitem__(self, key, value):
        self._edges[key] = value
        
        
    def __repr__(self):
        return self._edges.__repr__()

# Class for one autonomous ant
class Ant():
    
    _city = None             # Current city
    _path = None             # Path so far
    _distance = None         # Total length of the journey
    _done = None             # State of the journey
    _remaining_cities = None # Unseen cities
    _history = None
    
    def __init__(self):
        
        # Start in a random city
        index = np.random.randint(0, len(_CITIES))
        self._city = _CITIES[index]
        self._path = [self._city]
        self._remaining_cities = [city for city in _CITIES if city != self._city]

        self._done = False
        self._distance = 0
        self._history = []
        #print(f"Ant starting at {self._city[0]}")
    
    # Compute probability for ant to move to city in the next step
    def computeProb(self, city):
        global pheromons
        
        prob1 = gamma + pheromons[self._city[0]][city[0]]**alpha * 1./distance(self._city[1], city[1])**beta
        prob2 = 0

        for c in self._remaining_cities:
                prob2 += (gamma + pheromons[self._city[0]][c[0]]**alpha * 1./distance(self._city[1], c[1])**beta)

        return prob1 / prob2

    # One step forward in the journey, pick the next destination city
    def nextCity(self):
        
        # Case we went once to every city, end of the loop
        if len(self._path) == len(_CITIES):
            start = self._path[0]
            self._path.append(start)
            self._done = True
            self._distance += distance(self._city[1], start[1])
            self._city = start
            #self.displayPath()
            return

        # Max probability
        pmax = 0
        
        # Compute next destination according to probabilities
        for city in self._remaining_cities:
                prob = self.computeProb(city)
                if prob > pmax:
                    pmax = prob
                    next_city = city 

        # Move to the next city
        self._distance += distance(self._city[1], next_city[1])
        self._city = next_city
        self._path.append(next_city)
        self._remaining_cities.remove(next_city)
        
        
    # Update pheromons structure according to the path length
    def dropPheromons(self):
        global pheromons
        
        # Quantity of pheromons to drop
        value = Q / self._distance
        
        for i in range(len(self._path) - 1):
                pheromons[self._path[i][0]][self._path[i+1][0]] = value
                pheromons[self._path[i+1][0]][self._path[i][0]] = value
        
    # Display function for the path found by the ant
    def displayPath(self):
        
        toret = ""
        for city in self._path:
            toret += city[0] + " - "
            
        toret += "(" + str(self._distance) + ")"
        print(toret)
    
    # Reset ant after she did her job (i.e. loop and drop pheromons)
    def reset(self):
        index = np.random.randint(0, len(_CITIES))
        self._city = _CITIES[index]
        self._path = [self._city]
        self._remaining_cities = [city for city in _CITIES if city != self._city]
        self._done = False
        self._history.append(self._distance)
        self._distance = 0
    
    # One run for the ant
    def run(self):
        
        while not self._done:
            self.nextCity()
            
        self.dropPheromons()
        self.reset()
        

# Running NB_RUNS runs with NB_ANTS ants
ants = []
# Global pheromons
pheromons = Pheromons(p)

# Create ants
for i in range(NB_ANTS):
    ants.append(Ant())

# Runs
for k in range(NB_RUNS):
    pheromons.evaporate()
    for ant in ants:
        ant.run()   


# Results
result = (math.inf, -1)
print(enumerate(ants))
for k, ant in enumerate(ants):
    tmp = min(ant._history)
    if tmp < result[0]:
        result = (tmp, k)
                             
        
print(f"Ant {result[1]} found the shortest path, with length {result[0]} km")  
        
 