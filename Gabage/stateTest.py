

class StateMachine(object):

    def __init__(self):
        self._state = self.idle
        self._stateChange = [self.changePanic,self.changeActive]

        self._x = 0
        self._y = 0

    def update(self,x,y):
        self._x = x
        self._y = y
        for count,n in enumerate(self._stateChange):
     #       print(count,n)
            n()
        self._state()

    def changePanic(self):
        print(self._x,self._y)
        if self._x == 5 and self._y != 3:
            print('changePanic')
            self._state = self.panic


    def changeActive(self):
      #  print('changeActive')
        if self._x != 5 and self._y == 3:
            print('changeActive')
            self._state = self.panic

    def changePassive(self):
        print('changePassive')

    def idle(self):
        print('idle')
     #   self._state = self.active

    def active(self):
        print('active')
      #  self._state = self.panic

    def panic(self):
        print('panik')
       # self._state = self.idle
        self._stateChange = [self.changeActive]

    def run(self):
        self.update(5,4)
        self.update(5,3)
        self.update(4,3)



stm = StateMachine()
stm.run()

