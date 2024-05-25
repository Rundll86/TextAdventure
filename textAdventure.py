import msvcrt, os, random, rich, colorama, json, modLoader, importlib, math
from rich import text, style, live


class directs:
    right = "right"
    left = "left"
    up = "up"
    down = "down"


class weapons:
    sword = "sword"
    bow = "bow"


class logRecorder:
    content = ["-", "-", "-"]

    def append(self, cont, color):
        self.content.append(f"[{color}]{cont}[/{color}]") if canLog else ""

    def popFirst(self):
        del self.content[0]


mapw = 30  # 地图长
maph = 30  # 地图宽
playerx = 1  # 玩家初始X坐标
playery = 1  # 玩家初始Y坐标
players = 1  # 玩家移动速度
playera = directs.right  # 玩家方向
playerhm = 20  # 玩家最大生命值
playeratk = 10  # 玩家攻击力
playerw = weapons.sword  # 玩家武器
swords = False  # 如果武器为剑，剑的展开状态
enimielist = []  # 实体列表
lastfight = None  # 上次战斗敌怪
level = 10  # 等级
gameover = False  # 游戏是否结束
score = 0  # 分数
createdDoor = False  # 门已创建
flowerTexture = "[magenta]花[/magenta]"  # 花的贴图
grassTexture = "[green]草[/green]"  # 草的贴图
flowerGrass = [flowerTexture] * 1 + [grassTexture] * 1  # 花草占随机数组权重
mobCount = [5, 10]  # 敌怪数量
itemCount = [5, 10]  # 道具数量
logs = logRecorder()  # 游玩日志，最多储存3条
canLog = False  # 是否可记录游玩日志
slowActionKey = "wsadeo12"  # 非快速行动的按键列表
flowerBoost = 20  # 拾取花时提升量
grassBoost = 2  # 拾取草时提升量
autoAtkMultiplier = 1  # 自动等级时攻击力倍率
autoHealthMultiplier = 1  # 自动等级时生命上限倍率
autoScoreMultiplier = 1  # 自动等级时积分倍率
floatRate = 20  # 伤害浮动区间
autoPlay = False  # 自动战斗开关
canSave = True  # 是否自动存档
aiAtkTime = True  # AI自动战斗时攻击倒计时


def playerAttack():
    global swords
    if playerw == weapons.sword:
        swords = not swords
    elif playerw == weapons.bow:
        e = arrow()
        e.pos = [playerx, playery]
        e.direct = playera
        e.atk = playeratk + 1
        e.ai()
        enimielist.append(e)


def autoPlayer():
    global playerw, playera, aiAtkTime

    def lineD(start, end):
        return math.ceil(math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2))

    def closest(targetType):
        lastD = lineD([playerx, playery], [mapw * 3, maph * 3])
        result = None
        for i in enimielist:
            i: enimie
            if type(i) == targetType and lineD([playerx, playery], i.pos) < lastD:
                result = i
        return result

    def goto(pos):
        global playerx, playery, playera
        offsetpos = [pos[0] - playerx, pos[1] - playery]
        if abs(offsetpos[0]) > abs(offsetpos[1]):
            moved = upOrDown(offsetpos[0])
            if moved == 1:
                playera = directs.right
            elif moved == -1:
                playera = directs.left
            playerx += moved
        elif abs(offsetpos[0]) < abs(offsetpos[1]):
            moved = upOrDown(offsetpos[1])
            if moved == 1:
                playera = directs.down
            elif moved == -1:
                playera = directs.up
            playery += upOrDown(moved)
        else:
            moved = upOrDown(offsetpos[1])
            if moved == 1:
                playera = directs.down
            elif moved == -1:
                playera = directs.up
            playery += upOrDown(moved)

    def gotoAndAttack(pos):
        global playera
        d = directs.left if pos[0] + 3 <= mapw else directs.right
        pos = pos.copy()
        pos[0] += 3 if pos[0] + 3 <= mapw else -3
        goto(pos)
        if playerx == pos[0] and playery == pos[1]:
            playera = d

    playerw = weapons.bow
    if playerh / playerhm < 0.7:
        if closest(fruit) is not None:
            gotoAndAttack(closest(fruit).pos)
        else:
            try:
                pos = closest(enimie).pos.copy()
                pos[0] += random.choice([-10, 10])
                pos[1] += random.choice([-10, 10])
                "" if createdDoor else goto(pos)
            except:
                pass
    elif closest(flowerOrGrass) is not None:
        gotoAndAttack(closest(flowerOrGrass).pos)
    elif createdDoor:
        try:
            gotoAndAttack(closest(nextlevel).pos)
        except:
            pass
    elif closest(enimie) is not None:
        pos = closest(enimie).pos.copy()
        pos[0] += 5
        gotoAndAttack(pos)
    playerAttack() if aiAtkTime else ""
    aiAtkTime = not aiAtkTime


def updateSave():
    savedata = {
        "player": {
            "health": playerh,
            "healthMax": playerhm,
            "atk": playeratk,
            "position": [playerx, playery],
            "angle": playera,
            "weapon": playerw,
        },
        "system": {
            "score": score,
            "logs": logs.content,
            "level": level,
        },
    }
    json.dump(
        savedata, open("textAdventure.sv", "w", encoding="utf8"), ensure_ascii=False
    )
    return savedata


def loadsave():
    global playerh, playerhm, playeratk, playerx, playery, playera, playerw, score, level
    savedata = json.load(open("textAdventure.sv", encoding="utf8"))
    playerh = savedata["player"]["health"]
    playerhm = savedata["player"]["healthMax"]
    playeratk = savedata["player"]["atk"]
    playerx = savedata["player"]["position"][0]
    playery = savedata["player"]["position"][1]
    playera = savedata["player"]["angle"]
    playerw = savedata["player"]["weapon"]
    score = savedata["system"]["score"]
    logs.content = savedata["system"]["logs"]
    level = savedata["system"]["level"]
    return savedata


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


def pointdes(target, current):
    if current[0] + 1 == target[0] and current[1] + 1 == target[1]:
        return True
    else:
        return False


def progresslen(current, max, length=10):
    result = round(current / max * length)
    return (
        "[green]" + result * "=" + "[/green][red]" + (length - result) * "=" + "[/red]"
    )


def badenimielen():
    result = 0
    for i in enimielist:
        if type(i) == enimie:
            result += 1
    return result


def update():
    global lastfight, playerx, playery, playerh, playerhm, score, createdDoor, logs
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
            if (
                e2.pos == e.pos
                and i != j
                and type(e2) != arrow
                and type(e) != arrow
                and e2.canBePushed
            ):
                e2.pos[0] += 1
    while len(logs.content) > 3:
        logs.popFirst()
    result = ""
    result += "*" * (mapw * 2 + 2)
    result += "\n"
    for i in range(maph):
        result += "*"
        for j in range(mapw):
            isblank = True
            swordp = swordpos()
            if pointdes([playerx, playery], [j, i]):
                result += "[blue]我[/blue]"
                isblank = False
                continue
            elif pointdes(swordp, [j, i]):
                result += f"[yellow]{'剑'if playerw==weapons.sword else '弓'}[/yellow]"
                isblank = False
                continue
            for ki in range(len(enimielist)):
                if ki >= len(enimielist):
                    break
                k: enimie = enimielist[ki]
                deletedA = False
                if k.canDamage:
                    hurt = False
                    if swordp == k.pos and playerw == weapons.sword:
                        if k.canBePushed:
                            if playera == directs.right:
                                k.pos[0] += 1
                            elif playera == directs.left:
                                k.pos[0] -= 1
                            elif playera == directs.up:
                                k.pos[1] -= 1
                            elif playera == directs.down:
                                k.pos[1] += 1
                        damage = playeratk
                        hurt = True
                    for al in range(len(enimielist)):
                        a = enimielist[al]
                        if type(a) == arrow and a.pos == k.pos:
                            if k.canBePushed:
                                if a.direct == directs.right:
                                    k.pos[0] += 1
                                elif a.direct == directs.left:
                                    k.pos[0] -= 1
                                elif a.direct == directs.up:
                                    k.pos[1] -= 1
                                elif a.direct == directs.down:
                                    k.pos[1] += 1
                            damage = a.atk
                            hurt = True
                            del enimielist[al]
                            break
                    if hurt:
                        damage = round(
                            damage
                            * random.randint(100 - floatRate, 100 + floatRate)
                            * 0.01
                        )
                        k.health -= damage
                        (
                            logs.append(f"造成了{damage}点伤害！", "yellow")
                            if canLog
                            else ""
                        )
                        lastfight = k
                if k.health <= 0:
                    if deletedA:
                        ki -= 1
                    try:
                        del enimielist[ki]
                    except:
                        continue
                    k.onDie()
                    lastfight = None
                    if k.haveScore:
                        score += k.atk
                        (
                            logs.append(f"获得了{k.atk}点积分！", "green")
                            if canLog
                            else ""
                        )
                    if badenimielen() == 0 and not createdDoor:
                        door = nextlevel()
                        createdDoor = True
                        enimielist.append(door)
                if pointdes(k.pos, [j, i]):
                    result += k.texture
                    isblank = False
                    continue
            if isblank:
                result += "  "
        result += "*"
        result += "\n"
    result += "*" * (mapw * 2 + 2)
    result += "\n"
    result += f"生命 [ {progresslen(playerh,playerhm)} ] <{playerh}/{playerhm}>\n"
    result += f"攻击 <{playeratk}>\n"
    result += f"等级 <{level}>\n"
    weapontext = text.Text()
    usingw = style.Style(color="black", bgcolor="white")
    unusingw = style.Style(color="white", bgcolor=None)
    weapontext.append("武器 [ ")
    weapontext.append("近战", style=usingw if playerw == weapons.sword else unusingw)
    weapontext.append(" ")
    weapontext.append("远程", style=usingw if playerw == weapons.bow else unusingw)
    weapontext.append(" ]\n")
    result += weapontext.markup
    result += f"积分 <{score}>\n"
    if lastfight is None:
        result += "敌人 [ 未进入战斗 ]\n"
    else:
        result += f"敌人 [ {progresslen(lastfight.health,lastfight.healthm)} ] <{lastfight.health}/{lastfight.healthm}>\n"
    for i in range(3):
        result += (logs.content[i] if len(logs.content) > i else "") + "\n"
    if autoPlay:
        result += "[magenta][AI] 自动战斗运行中[/magenta]\n"
    else:
        result += "\n"
    if gameover:
        os.system("del /s /q textAdventure.sv")
        result += "[red]游戏结束！\n旧存档已删除。[/red]"
    else:
        result += "[yellow]WSAD移动，O键启/禁用自动战斗AI，E键攻击，数字键1、2切换武器[/yellow]"
    updateSave() if canSave else ""
    return result


def processInput(key):
    global playerx, playery, playera, swords, playerw
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
        playerAttack()
    elif key == "1":
        playerw = weapons.sword
    elif key == "2":
        playerw = weapons.bow
        swords = False


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
    canDamage = False
    canBePushed = True
    haveScore = True

    def random(self):
        self.pos = [random.randint(1, mapw), random.randint(1, maph)]
        self.healthm = random.randint(50 * level, 100 * level)
        self.health = self.healthm
        self.atk = random.randint(level, level * 2)
        self.atktime = random.randint(0, 5)

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
                    (logs.append(f"受到了{self.atk}点伤害！", "red") if canLog else "")
                    self.atktime = 5
                if playerh <= 0:
                    gameover = True
            if abs(offsetpos[0]) > abs(offsetpos[1]):
                self.pos[0] -= upOrDown(offsetpos[0])
            elif abs(offsetpos[0]) < abs(offsetpos[1]):
                self.pos[1] -= upOrDown(offsetpos[1])
            else:
                self.pos[1] -= upOrDown(offsetpos[1])
            self.lastmoved = True

    def onDie(self):
        return


class arrow(enimie):
    texture = "[yellow]箭[/yellow]"
    direct = None
    lifetime = 20
    haveScore = False
    offset = 0
    offsetStep = 0
    offsetTime = 0

    def __init__(self):
        self.random()
        self.offset = random.randint(-1, 1)
        self.offsetStep = random.randint(0, 10)
        self.offsetTime = self.offsetStep

    def ai(self):
        num = 0
        if self.offsetTime > 0:
            self.offsetTime -= 1
        else:
            num = self.offset
            self.offsetTime = self.offsetStep
        if self.direct == directs.up:
            self.pos[1] -= 1
            self.pos[0] += num
        elif self.direct == directs.down:
            self.pos[1] += 1
            self.pos[0] -= num
        elif self.direct == directs.left:
            self.pos[0] -= 1
            self.pos[1] -= num
        elif self.direct == directs.right:
            self.pos[0] += 1
            self.pos[1] += num
        self.atk *= 0.8
        self.atk = int(self.atk)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.health = 0

    def onDie(self):
        self.atk = 0


class nextlevel(enimie):
    pos = [2, 2]
    texture = "门"
    health = 1
    canDamage = True

    def ai(self):
        return

    def onDie(self):
        createEnimie()

    def __init__(self):
        self.pos = [2, 2]


class flowerOrGrass(enimie):
    canDamage = True

    def onDie(self):
        global playerhm, playerh, playeratk, flowerBoost, grassBoost
        flowerBoost = random.randint(10, 20)
        grassBoost = random.randint(2, 5)
        if self.texture == flowerTexture:
            playerhm += flowerBoost
            playerh += flowerBoost
            (logs.append(f"生命上限提升{flowerBoost}点！", "green") if canLog else "")
        elif self.texture == grassTexture:
            playeratk += grassBoost
            logs.append(f"攻击提升{grassBoost}点！", "yellow")

    def ai(self):
        return

    def __init__(self):
        self.random()
        self.texture = random.choice(flowerGrass)
        self.healthm = 1
        self.health = 1


class fruit(enimie):
    canDamage = True

    def __init__(self):
        self.random()
        self.texture = "[red]果[/red]"
        self.healthm = 1
        self.health = 1

    def ai(self):
        return

    def onDie(self):
        global playerh, playerhm
        playerh += playerhm * 0.05
        logs.append(f"回复了{playerhm*0.05}点生命！", "green")
        playerh = int(playerh)


class tree(enimie):
    growtime = 0
    canBePushed = False

    def __init__(self):
        self.random()
        """self.pos = [
            random.randint(round(mapw / 2 - 5), math.ceil(mapw / 2 + 5)),
            random.randint(round(maph / 2 - 5), math.ceil(maph / 2 + 5)),
        ]"""
        self.texture = "[green]树[/green]"
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
    logs.append(f"到达第{level}等级！", "magenta")
    playerh += playerhm * 0.2
    logs.append(f"回复了{playerhm*0.2}点生命！", "green")
    playerh = int(playerh)
    for i in range(random.randint(mobCount[0], mobCount[1])):
        e = enimie()
        e.random()
        e.canDamage = True
        enimielist.append(e)
    for i in range(random.randint(itemCount[0], itemCount[1])):
        e = flowerOrGrass()
        enimielist.append(e)
    e = tree()
    enimielist.append(e)


if True:
    for i in range(level - 1):
        playeratk += (
            random.randint(round(itemCount[0] / 2), round(itemCount[1] / 2))
            * grassBoost
            * autoAtkMultiplier
        )
        playerhm += (
            random.randint(round(itemCount[0] / 2), round(itemCount[1] / 2))
            * flowerBoost
            * autoHealthMultiplier
        )
        score += random.randint(round(level), round(level * 2)) * autoHealthMultiplier
    playeratk = int(playeratk)
    playerhm = int(playerhm)
    score = int(score)
    playerh = playerhm
    keyinput = ""
    level -= 1
    colorama.init(autoreset=True)
    createEnimie()
    canLog = True
    if os.path.exists("textAdventure.sv"):
        loadsave()
    """if not os.path.exists("mods"):
        os.mkdir("mods")
    modsImportPathes = []
    for root, _, files in os.walk("mods"):
        for file in files:
            if "__PYCACHE__" in root.upper():
                continue
            p: str = os.path.relpath(os.path.join(root, file), os.curdir)
            if os.path.splitext(p)[1].upper().startswith(".PY"):
                p = os.path.splitext(p)[0].replace("/", ".").replace("\\", ".")
                modsImportPathes.append(p)
    for i in modsImportPathes:
        try:
            modData: modLoader.Mod = importlib.import_module(i).Export
        except Exception as e:
            print("加载Mod出错。", e)
            while True:
                pass"""
    renderer = live.Live()
    lastlength = 0
    while True:
        renderdata = update() if keyinput in slowActionKey else renderdata
        if len(renderdata) < lastlength:
            renderdata = renderdata.ljust(lastlength)
        if len(renderdata) > lastlength:
            lastlength = len(renderdata)
        clearflush()
        rich.print(renderdata)
        if gameover:
            while True:
                pass
        if autoPlay:
            autoPlayer()
        else:
            keyinput = msvcrt.getch().decode("ascii")
            if keyinput == "o":
                autoPlay = True
                continue
            processInput(keyinput)
