''' Implement an Auto-play mode playing tetris '''

'''
<Reference>
1.  Handley, M. (2018) 'Lecture notes at Design and Professional Skills', (23rd NOV 2018), UCL
        - Gave inspiration as to make_move() and search() function

2.  Lee, Y. (2013) 'Tetris AI - The (Near) Perfect Bot'. Available at: 
    https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
        - Gave inspiration as to rewards

3.  Williams, M.J (2012) 'Implementing Tetirs'. Available at:
    https://gamedevelopment.tutsplus.com/tutorials/implementing-tetris-clearing-lines--gamedev-1197
        - Gave inspiration as to row_complete() function
'''

from random import Random
from te_settings import Direction


class AutoPlayer():
    def __init__(self, controller):
        self.controller = controller
        self.searchPos = 0
        self.searchAng = 0
        #weights for rewards
        self.holeweight = -0.35
        self.heightweight = -0.5
        self.bumpweight = -0.25
        self.lineweight = 0.7

    def next_move(self, gamestate):
        x, y = gamestate.get_falling_block_position()
        if y == 0:
            self.searchPos, self.searchAng = self.search(gamestate)
        self.make_move(gamestate, self.searchPos, self.searchAng)

    def make_move(self, gamestate, target_pos, target_rot):
        x, y = gamestate.get_falling_block_position()
        #move tile to best position
        direction = None
        if target_pos < x:
            direction = Direction.LEFT
        elif target_pos > x:
            direction = Direction.RIGHT
        if direction != None:
            gamestate.move(direction)
        
        #set to the best target roatation
        angle = gamestate.get_falling_block_angle()
        direction = None
        if target_rot == 3 and angle == 0:
            direction = Direction.LEFT
        elif target_rot > angle:
            direction = Direction.RIGHT
        if direction != None:
            gamestate.rotate(direction)

    def search(self, gamestate):
        searchPos = 0
        searchAng = 0
        threshold = -999999999      #random small negative value

        # height_record = 0
        for angle in range(0, 4):
            for position in range(-3, 15):
                clone = gamestate.clone(True)
                while clone.update() == False:

                    a, b = clone.get_falling_block_position()
                    direction = None
                    if position < a:
                        direction = Direction.LEFT
                    elif position > a:
                        direction = Direction.RIGHT
                    if direction != None:
                        clone.move(direction)

                    ang = clone.get_falling_block_angle()
                    direction = None
                    if angle == 3 and ang == 0:
                        direction = Direction.LEFT
                    elif angle > ang:
                        direction = Direction.RIGHT
                    if direction != None:
                        clone.rotate(direction)

                f1 = self.height_aggregation(clone)
                reward1 = sum(f1)
                reward2 = self.check_holes(clone)
                reward3 = self.bumpiness(clone)
                reward4 = self.row_complete(clone)
                
                t1 = reward1 * self.heightweight
                t2 = reward2 * self.holeweight
                t3 = reward3 * self.bumpweight
                t4 =reward4 * self.lineweight

                final = t1 + t2 +t3 + t4

                if final > threshold:
                    threshold = final
                    searchPos = position
                    searchAng = angle
                    
        return (searchPos, searchAng)



    def height_aggregation(self, clone):
        cloned_tiles = clone.get_tiles()

        height = []
        for col in range(10):
            for row in range(20):
                if cloned_tiles[row][col] != 0:
                    height.append(20-row)
                    break
                
        return height


    def check_holes(self, clone):
            #checking all columns and find any holes
            cloned_tiles = clone.get_tiles()
            
            hole_cnt = 0
            for row in range(20):
                for col in range(10):
                    if row < 19 and cloned_tiles[row][col] != 0 and cloned_tiles[row+1][col] == 0:
                        hole_cnt = hole_cnt + 1
            return hole_cnt


    def bumpiness(self, clone):
        cloned_tiles = clone.get_tiles()
        #summing up the absolute differences between all two adjacent columns
        
        # intentionally did not use nested loops in order to know which column has which height
        height0 = [0]
        height1 = [0]
        height2 = [0]
        height3 = [0]
        height4 = [0]
        height5 = [0]
        height6 = [0]
        height7 = [0]
        height8 = [0]
        height9 = [0]

        for i in range(20):
            if cloned_tiles[i][0] != 0:
                h0 = 20-i
                height0[0] = h0
                break
                

        for i in range(20):
            if cloned_tiles[i][1] != 0:
                h1 = 20-i
                height1[0] = h1
                break
                
        for i in range(20):
            if cloned_tiles[i][2] != 0:
                h2 = 20-i
                height2[0] = h2
                break

        for i in range(20):
            if cloned_tiles[i][3] != 0:
                h3 = 20-i
                height3[0] = h3
                break

        for i in range(20):
            if cloned_tiles[i][4] != 0:
                h4 = 20-i
                height4[0] = h4
                break

        for i in range(20):
            if cloned_tiles[i][5] != 0:
                h5 = 20-i
                height5[0] = h5
                break

        for i in range(20):
            if cloned_tiles[i][6] != 0:
                h6 = 20-i
                height6[0] = h6
                break

        for i in range(20):
            if cloned_tiles[i][7] != 0:
                h7 = 20-i
                height7[0] = h7
                break

        for i in range(20):
            if cloned_tiles[i][8] != 0:
                h8 = 20-i
                height8[0] = h8
                break

        for i in range(20):
            if cloned_tiles[i][9] != 0:
                h9 = 20-i
                height9[0] = h9
                break
        
        return abs(height0[0]-height1[0]) + abs(height1[0]-height2[0]) + abs(height2[0]-height3[0]) + abs(height3[0]-height4[0]) + abs(height4[0]-height5[0]) + abs(height6[0]-height7[0]) + abs(height7[0]-height8[0]) + abs(height8[0]-height9[0])
    
    
    def row_complete(self, clone):
        #check if blocks complete lines
        cloned_tiles = clone.get_tiles()
        
        block_cnt = 0 
        explosion = 0

        for row in range(20):
            block_cnt = 0
            for col in range(10):
                if cloned_tiles[row][col] != 0:
                    block_cnt = block_cnt + 1
                else:
                    break
            if block_cnt == 10:
                explosion = explosion +1
        return explosion




