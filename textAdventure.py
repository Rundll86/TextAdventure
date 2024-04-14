import msvcrt, os, random


class directs:
    right = "right"
    left = "left"
    up = "up"
    down = "down"


mapw = 30
maph = 30
playerx = 1
playery = 1
players = 1
playera = directs.right
playerhm = 2010
playerh = playerhm
playeratk = 500
swords = False
enimielist = []
lastfight = None
level = 99
gameover = False
score = 0
createdDoor = False
flowerGrass = ["草", "草"]
mobCount = [5, 10]
itemCount = [0, 1]


def swordpos():
    result = []
    offset = 1
    if swords:
        offset = 2
    if playera == directs.right:
        result = [playerx + offset, playery]
    elif playera == directs.left:
        result = [playerx - offset, playery]
    elif playera == directs.up:
        result = [playerx, playery - offset]
    elif playera == directs.down:
        result = [playerx, playery + offset]
    return result


def clearflush():
    os.system("cls")


clearflush()


def pointdes(target, current):
    if current[0] + 1 == target[0] and current[1] + 1 == target[1]:
        return True
    else:
        return False


def progresslen(current, max, length=10):
    result = round(current / max * length)
    return result * "=" + (length - result) * "-"


def badenimielen():
    result = 0
    for i in enimielist:
        if type(i) == enimie:
            result += 1
    return result


def update():
    global lastfight, playerx, playery, playerh, playerhm, score, createdDoor
    if playerx < 1:
        playerx = 1
    if playerx > mapw:
        playerx = mapw
    if playery < 1:
        playery = 1
    if playery > maph:
        playery = maph
    if playerh > playerhm:
        playerh = playerhm
    for i in enimielist:
        i: enimie
        i.ai()
        if i.pos[0] < 1:
            i.pos[0] = 1
        if i.pos[0] > mapw:
            i.pos[0] = mapw
        if i.pos[1] < 1:
            i.pos[1] = 1
        if i.pos[1] > maph:
            i.pos[1] = maph
    for i in range(len(enimielist)):
        e: enimie = enimielist[i]
        for j in range(len(enimielist)):
            e2: enimie = enimielist[j]
            if e2.pos == e.pos and i != j:
                e2.pos[0] += 1
    result = ""
    result += "*" * (mapw * 2 + 2)
    result += "\n"
    for i in range(maph):
        result += "*"
        for j in range(mapw):
            isblank = True
            swordp = swordpos()
            if pointdes([playerx, playery], [j, i]):
                result += "我"
                isblank = False
            elif pointdes(swordp, [j, i]):
                result += "剑"
                isblank = False
            for ki in range(len(enimielist)):
                k: enimie = enimielist[ki]
                if swordp == k.pos:
                    if playera == directs.right:
                        k.pos[0] += 1
                    elif playera == directs.left:
                        k.pos[0] -= 1
                    elif playera == directs.up:
                        k.pos[1] -= 1
                    elif playera == directs.down:
                        k.pos[1] += 1
                    k.health -= playeratk
                    lastfight = k
                    if k.health <= 0:
                        del enimielist[ki]
                        k.onDie()
                        lastfight = None
                        score += k.atk
                        if badenimielen() == 0 and not createdDoor:
                            door = nextlevel()
                            createdDoor = True
                            enimielist.append(door)
                        break
                if pointdes(k.pos, [j, i]):
                    result += k.texture
                    isblank = False
            if isblank:
                result += "  "
        result += "*"
        result += "\n"
    result += "*" * (mapw * 2 + 2)
    result += "\n"
    result += f"生命 [ {progresslen(playerh,playerhm)} ] <{playerh}/{playerhm}>\n"
    result += f"攻击 <{playeratk}>\n"
    result += f"等级 <{level}>\n"
    result += f"积分 <{score}>\n"
    if lastfight is not None:
        result += f"敌人 [ {progresslen(lastfight.health,lastfight.healthm)} ] <{lastfight.health}/{lastfight.healthm}>"
    if gameover:
        result += "\n游戏结束！"
    return result


def processInput(key):
    global playerx, playery, playera, swords
    if key == "w":
        target = playery - players
        if len(enimielist) == 0:
            createEnimie()
        for k in enimielist:
            k: enimie
            if not pointdes(k.pos, [playerx - 1, target - 1]):
                playery = target
        playera = directs.up
    elif key == "s":
        target = playery + players
        if len(enimielist) == 0:
            createEnimie()
        for k in enimielist:
            k: enimie
            if not pointdes(k.pos, [playerx - 1, target - 1]):
                playery = target
        playera = directs.down
    elif key == "a":
        target = playerx - players
        if len(enimielist) == 0:
            createEnimie()
        for k in enimielist:
            k: enimie
            if not pointdes(k.pos, [target - 1, playery - 1]):
                playerx = target
        playera = directs.left
    elif key == "d":
        target = playerx + players
        if len(enimielist) == 0:
            createEnimie()
        for k in enimielist:
            k: enimie
            if not pointdes(k.pos, [target - 1, playery - 1]):
                playerx = target
        playera = directs.right
    elif key == "e":
        swords = not swords


def upOrDown(num):
    if num > 0:
        return 1
    if num < 0:
        return -1
    return 0


class enimie:
    texture = "怪"
    healthm = 0
    health = 0
    atk = 0
    pos = []
    lastmoved = True
    atktime = 0

    def random(self):
        self.pos = [random.randint(1, mapw), random.randint(1, maph)]
        self.healthm = random.randint(50 * level, 100 * level)
        self.health = self.healthm
        self.atk = random.randint(level, level * 2)

    def ai(self):
        if self.lastmoved:
            self.lastmoved = False
        else:
            global playerh, gameover
            offsetpos = [self.pos[0] - playerx, self.pos[1] - playery]
            if abs(offsetpos[0]) < 2 and abs(offsetpos[1]) < 2:
                if self.atktime:
                    self.atktime -= 1
                else:
                    playerh -= self.atk
                    self.atktime = 5
                if playerh <= 0:
                    gameover = True
            if abs(offsetpos[0]) > abs(offsetpos[1]):
                self.pos[0] -= upOrDown(offsetpos[0])
            if abs(offsetpos[0]) < abs(offsetpos[1]):
                self.pos[1] -= upOrDown(offsetpos[1])
            self.lastmoved = True

    def onDie(self):
        return


class nextlevel(enimie):
    pos = [2, 2]
    texture = "门"
    health = 1

    def ai(self):
        return

    def onDie(self):
        createEnimie()


class flowerOrGrass(enimie):
    def onDie(self):
        global playerhm, playerh, playeratk
        if self.texture == "花":
            playerhm += 5
            playerh += 5
        elif self.texture == "草":
            playeratk += 2

    def ai(self):
        return

    def __init__(self):
        self.random()
        self.texture = random.choice(flowerGrass)
        self.healthm = 1
        self.health = 1


class fruit(enimie):
    def __init__(self):
        self.random()
        self.texture = "果"
        self.healthm = 1
        self.health = 1

    def ai(self):
        return

    def onDie(self):
        global playerh, playerhm
        playerh += playerhm * 0.05
        playerh = int(playerh)


class tree(enimie):
    growtime = 0

    def __init__(self):
        self.random()
        self.texture = "树"
        self.healthm = 100
        self.health = 100

    def ai(self):
        if self.growtime:
            self.growtime -= 1
        else:
            f = fruit()
            f.pos = self.pos.copy()
            f.pos[0] += random.choice([-1, 1])
            f.pos[1] += random.choice([-1, 0, 1])
            enimielist.append(f)
            self.growtime = 30


def createEnimie():
    global level, playeratk, playerh, enimielist, createdDoor
    createdDoor = False
    enimielist = []
    level += 1
    playerh += playerhm * 0.2
    playerh = int(playerh)
    for i in range(random.randint(mobCount[0], mobCount[1])):
        e = enimie()
        e.random()
        enimielist.append(e)
    for i in range(random.randint(itemCount[0], itemCount[1])):
        e = flowerOrGrass()
        enimielist.append(e)
    e = tree()
    enimielist.append(e)


createEnimie()
while True:
    renderdata = update()
    clearflush()
    print(renderdata, end="\r")
    if gameover:
        while True:
            pass
    keyinput = msvcrt.getch().decode("ascii")
    processInput(keyinput)
