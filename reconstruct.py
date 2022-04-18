import random
import time
import numpy
import pyautogui
import win32api
import win32con
import win32gui
import win32ui
from numpy import average, dot, linalg
from PIL import Image, ImageGrab

class Llk:
    left = 574
    top = 401
    interval_x = 30
    interval_y = 34
    x = 19
    y = 11
    
    hdwd = win32gui.FindWindow(0,"QQ游戏 - 连连看角色版")
    def __init__(self) -> None:
        self.arrays = [[0 for a in range(self.x)] for b in range(self.y)]
        self.rest_pics = [[0 for a in range(self.x)] for b in range(self.y)]
        win32gui.SetForegroundWindow(self.hdwd)
        time.sleep(0.3)
        self.screen_shot = ImageGrab.grab(all_screens=True)
        def back_ground(img):
            for i in range(7,16,2):
                for j in range(7,16,2):
                    if(img.getpixel((j,i)) != (48,76,112)):
                        return False
            return True
        lis = [self.left,self.top]
        for i in range(self.x):
            lis[0] = self.left + self.interval_x*i+i
            for j in range(self.y):
                lis[1] = self.top + self.interval_y*j+j
                self.arrays[j][i] = self.screen_shot.crop(box = (lis[0],lis[1],lis[0]+self.interval_x,lis[1]+self.interval_y))
                #self.arrays[j][i].save("%d,%d.png"%(j,i)) #下载图片，便于调试
                if(back_ground(self.arrays[j][i])):
                    self.rest_pics[j][i] = 0
                else:
                    self.rest_pics[j][i] = 1
    #直线相连
    def straight(self,j,i,indexj,indexi):
        if(i != indexi and j != indexj):
            return False
        if (j == indexj and abs(i - indexi)==1) or (i == indexi and abs(j-indexj)==1):
            return True#相邻直接相消
        elif (j == indexj):
            s = 0
            if (abs(indexi - i) == 2):
                return 1-bool(self.rest_pics[j][int((i+indexi)/2)])
            else:
                for t in range(min(i,indexi)+1,max(i,indexi)):
                    s += self.rest_pics[j][t]
                return 1-bool(s)
        elif (i == indexi):
            s = 0
            if(indexj - j == 2):
                return 1-bool(self.rest_pics[int((j+indexj)/2)][i])
            else:
                for t in range(min(j,indexj)+1,max(j,indexj)):
                    s += self.rest_pics[t][i]
                return 1-bool(s)
        else:
            return False###
    #转弯一次
    def one_turn(self,j,i,indexj,indexi):
        case1 = self.rest_pics[j][indexi]
        case2 = self.rest_pics[indexj][i]
        if (case1 + case2 == 0):
            return ((self.straight(j,indexi,j,i) == True) and (self.straight(j,indexi,indexj,indexi) == True)) or \
                ((self.straight(indexj,i,j,i) == True) and (self.straight(indexj,i,indexj,indexi)) == True)
        elif(case1 == 0 and case2 == 1):
            return ((self.straight(j,indexi,j,i) == True) and (self.straight(j,indexi,indexj,indexi) == True))
        elif(case1 == 1 and case2 == 0):
            return ((self.straight(indexj,i,j,i) == True) and (self.straight(indexj,i,indexj,indexi)) == True)
        else:
            return False
    def one_turn_or2(self,j,i,indexj,indexi):
        if(j == indexj or i == indexi):
            return self.straight(j,i,indexj,indexi)
        else:
            return self.one_turn(j,i,indexj,indexi)

    #转弯二次
    def z_turns(self,j,i,indexj,indexi):
        leftw = indexi - 1
        upw = indexj -1
        rightw = indexi + 1
        downw = indexj + 1
        index = 0
        while(leftw>=0):
            if(self.rest_pics[indexj][leftw] == True):
                break
            elif (self.one_turn_or2(indexj,leftw,j,i)):
                return True
            else:
                leftw -= 1
        while(upw>=0):
            if(self.rest_pics[upw][indexi] == True):
                break
            elif (self.one_turn_or2(upw,indexi,j,i)):
                return True
            else:
                upw -= 1
        while(rightw<len(self.arrays[0])):
            if(self.rest_pics[indexj][rightw] == True):
                break
            elif (self.one_turn_or2(indexj,rightw,j,i)):
                return True
            else:
                rightw += 1
        while(downw<len(self.arrays)):
            if(self.rest_pics[downw][indexi] == True):
                break
            elif (self.one_turn_or2(downw,indexi,j,i)):
                return True
            else:
                downw += 1
        return False
    def click_block(self,indexi,indexj,i,j):#控制鼠标进行点击操作
        
        sleep = 2.5
        print("(%d,%d)  (%d,%d)"%(i,j,indexi,indexj))
        pyautogui.click(x = self.left + (self.interval_x+0.5)*indexi+indexi,y = self.top + (self.interval_y+0.5)*indexj+indexj)
        pyautogui.click(x = self.left + (self.interval_x+0.5)*i+i,y = self.top + (self.interval_y+0.5)*j+j,interval= sleep/10)
        self.rest_pics[j][i] = 0
        self.rest_pics[indexj][indexi] = 0
    def check_connect(self,j,i,indexj,indexi):
        if(self.straight(j,i,indexj,indexi)):
            return True
        if(self.one_turn(j,i,indexj,indexi)):
            return True
        if(self.z_turns(j,i,indexj,indexi)):
            return True
        return False
    def find_siblings(self,indexj,indexi):
        for i in range(0,self.x):
            for j in range(0,self.y):
                if ((self.arrays[j][i]==self.arrays[indexj][indexi]) and ((j != indexj) or (i != indexi))):
                    if ((indexi >= i) and self.rest_pics[j][i] == True and self.rest_pics[indexj][indexi]== True):
                        if(self.check_connect(j,i,indexj,indexi)):
                            self.click_block(indexi,indexj,i,j)
                            return True
    def rest(self):
        for i in range(19):
            for j in range(11):
                if(self.rest_pics[j][i] == 1):
                    return True
        return 0
    def run(self):
        hdwd = win32gui.FindWindow(0,"QQ游戏 - 连连看角色版")
        win32gui.SetForegroundWindow(hdwd)
        while self.rest():
            for i in range(self.x):
                for j in range(self.y):
                    self.find_siblings(j, i)
a = Llk()
a.run()
