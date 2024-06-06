import time
import wx
import wx.grid

FIRST = dict()  # FIRST集
FOLLOW = dict()  # FOLLOW集
Grammar = dict()  # 文法
LL1Table = dict()  # 分析表
VT = set()  # 终结符
ProcessList = dict()


def get_lan():
    num = int(input('请输入文法的个数：'))
    for i in range(num):
        temp = input()
        splitlist = temp[3:].replace("\n", "").split("|")
        Grammar[temp[0]] = splitlist


def get_first():
    for k in Grammar:
        l = Grammar[k]
        FIRST[k] = list()
        for s in l:
            if not (s[0].isupper()):
                FIRST[k].append(s[0])
    for i in range(2):
        for k in Grammar:
            l = Grammar[k]
            for s in l:
                if (s[0].isupper()):
                    FIRST[k].extend(FIRST[s[0]])
                    FIRST[k] = list(set(FIRST[k]))  # 去重
    print("文法为：%s" % Grammar)
    print("FIRST集为：%s" % FIRST)


def get_follow():
    condition = lambda t: t != '~'  # 过滤器用于过滤空串
    for k in Grammar:  # 新建list
        FOLLOW[k] = list()
        if k == list(Grammar.keys())[0]:
            FOLLOW[k].append('#')
    for i in range(2):
        for k in Grammar:
            l = Grammar[k]
            for s in l:
                if s[len(s) - 1].isupper():
                    FOLLOW[s[len(s) - 1]].extend(FOLLOW[k])  # 若A→αB是一个产生式，则把FOLLOW(A)加至FOLLOW(B)中
                    FOLLOW[s[len(s) - 1]] = list(filter(condition, FOLLOW[s[len(s) - 1]]))  # 去除空串
                for index in range(len(s) - 1):
                    if s[index].isupper():
                        if s[index + 1].isupper():  # 若A→αBβ是一个产生式，则把FIRST(β)\{ε}加至FOLLOW(B)中；
                            FOLLOW[s[index]].extend(FIRST[s[index + 1]])
                            FOLLOW[s[index]] = list(filter(condition, FOLLOW[s[index]]))  # 去除空串
                        if not (s[index + 1].isupper()) and (s[index + 1] != '~'):
                            FOLLOW[s[index]].append(s[index + 1])
                        emptyflag = 1
                        for i in range(index + 1, len(s)):
                            if not (s[i].isupper()) or (s[i].isupper() & ('~' not in FIRST[s[i]])):
                                emptyflag = 0
                                break
                        if emptyflag == 1:
                            FOLLOW[s[index]].extend(FOLLOW[k])  # A→αBβ是一个产生式而(即ε属于FIRST(β))，则把FOLLOW(A)加至FOLLOW(B)中
                            FOLLOW[s[index]] = list(filter(condition, FOLLOW[s[index]]))  # 去除空串
    for k in FOLLOW:  # 去重
        FOLLOW[k] = list(set(FOLLOW[k]))
    print('FOLLOW集为：%s' % FOLLOW)


def get_VT():
    VT.add('#')
    for l in Grammar.values():
        for s in l:
            for c in s:
                if not (c.isupper()) and (c != '~'): VT.add(c)
    print('终结符为：%s' % VT)


def generate_table():
    get_VT()
    for k in Grammar:  # 初始化分析表
        LL1Table[k] = dict()
        for e in VT:
            LL1Table[k][e] = None
    for k in Grammar:
        l = Grammar[k]
        for s in l:
            if s[0].isupper():
                for e in VT:
                    if e in FIRST[s[0]]: LL1Table[k][e] = s
            if s[0] in VT:
                LL1Table[k][s[0]] = s
            if (s[0].isupper() and ('~' in FIRST[s[0]])) or (s == '~'):
                for c in FOLLOW[k]:
                    LL1Table[k][c] = s
    print('分析表为：%s' % LL1Table)


class GridFrame(wx.Frame):
    def __init__(self, parent):
        global LR0TABLE

        wx.Frame.__init__(self, parent)

        # Create a wxGrid object
        grid = wx.grid.Grid(self, -1)

        # Then we call CreateGrid to set the dimensions of the grid
        # (100 rows and 10 columns in this example)
        grid.CreateGrid(len(list(LL1Table)) + 1, len(VT) + 1)

        # We can set the sizes of individual rows and columns
        # in pixels

        grid.SetCellValue(1, 0, 'E')
        grid.SetCellValue(2, 0, 'M')
        grid.SetCellValue(3, 0, 'T')
        grid.SetCellValue(4, 0, 'N')
        grid.SetCellValue(5, 0, 'F')

        VTList = list(VT)
        VTList.sort(reverse=True)
        for i in range(len(list(VT))):
            grid.SetCellValue(0, i+1, list(VTList)[i])

        for i in range(len(list(LL1Table))):
            for j in range(len(list(VT))):
                if str(LL1Table[grid.GetCellValue(i + 1, 0)][grid.GetCellValue(0, j + 1)]) != 'None':
                    grid.SetCellValue(i + 1, j + 1, '->' + str(LL1Table[grid.GetCellValue(i + 1, 0)][grid.GetCellValue(0, j + 1)]))

        print(LL1Table[grid.GetCellValue(1, 0)][grid.GetCellValue(0, 1)])

        self.Show()




##############句子的分析###############

def analyze():
    temp = input('输入句子')
    global a
    inputstr = '#'+temp+'#'
    inputstr = inputstr[1:]
    inputstr = list(inputstr[::-1])
    print(inputstr)
    process = list()
    process.append('#')  # "#"入栈
    process.append(list(Grammar.keys())[0])  # 开始符入栈
    errorflag = 0  # 出错标识
    count = 0  # 插入列表时的索引
    ProcessList.clear()
    ProcessList[count] = (''.join(process), ''.join(inputstr), ' ', 'init')
    while True:
        count += 1
        current = process.pop()
        if current == inputstr[-1] == '#':  # 分析成功结束
            ProcessList[count] = ('句子', '接受', '', '')
            break

        if current in VT and (current == inputstr[-1]):  # 遇到终结符
            inputstr.pop()
            ProcessList[count] = (''.join(process), ''.join(inputstr), ' ', '读取下一个')
            continue

        if inputstr[-1] in VT:  # 判断是不是终结符
            new = LL1Table[current][inputstr[-1]]
        else:
            errorflag = 1
            ProcessList[count] = (''.join(process), ''.join(inputstr), ' ', 'Error:输入不合法！')
            break

        if new == None:  # 没有找到对应产生式
            errorflag = 1
            ProcessList[count] = (''.join(process), ''.join(inputstr), ' ', 'Error:没有找到对应产生式!')
            break

        if new == '~':  # 产生式为空串
            ProcessList[count] = (''.join(process), ''.join(inputstr), current + '->~', '出栈')
            continue

        for c in reversed(new):  # 将产生式入栈
            process.append(c)
        ProcessList[count] = (''.join(process), ''.join(inputstr), current + '->' + ''.join(new), '出栈、入栈')

    if errorflag == 0:
        print("分析成功！")
    else:
        print("分析失败！")

    items = list(ProcessList.items())
    for i in range(len(items)):
        print(items[i][0],end='  ')
        for j in range(len(items[i][1])):
            print(items[i][1][j], end='  ')
        print(' ')
    # print(items)


def analyze2():
    temp = '(i+i)*i+i*i+i*(i+i)*i*i'
    global a
    inputstr = '#'+temp+'#'
    inputstr = inputstr[1:]
    inputstr = list(inputstr[::-1])
    process = list()
    process.append('#')  # "#"入栈
    process.append(list(Grammar.keys())[0])  # 开始符入栈
    count = 0  # 插入列表时的索引
    while True:
        count += 1
        current = process.pop()
        if current == inputstr[-1] == '#':  # 分析成功结束
            break

        if (current in VT) and (current == inputstr[-1]):  # 遇到终结符
            inputstr.pop()
            continue

        if inputstr[-1] in VT:  # 判断是不是终结符
            new = LL1Table[current][inputstr[-1]]
        else:
            break

        if new == None:  # 没有找到对应产生式
            break

        if new == '~':  # 产生式为空串
            continue

        for c in reversed(new):  # 将产生式入栈
            process.append(c)


get_lan()  # 得到文法
get_first()  # 得到FIRST集
get_follow()  # 得到FOLLOW集s
generate_table()  # 得到分析表

# GUI
app = wx.App(0)
frame = GridFrame(None)
app.MainLoop()


x = 100000
a = time.clock()
print('start')
while x:
    analyze2()  # 对输入字符串进行分析
    x -= 1
b = time.clock()
print(b-a)


'''
E->TM
M->+TM|~
T->FN
N->*FN|~
F->i|(E)
'''

'''
(i+i)*i+i*i+i*(i+i)*i*i+i+i*i+(i*i)+(i+i)*i+i*i+i*(i+i)*i*i+i+i*i+(i*i)*(i+i)*i+i*i+i*(i+i)*i*i+i+i*i+(i*i)
'''