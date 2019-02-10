from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
import numpy as np
import io
import os
import time

class game:
    def __init__(self, game_path, chromium_path,
                 n_obstacles = 3, 
                 window_size = "320, 180"):
        ### Setting variables
        self._game_path = game_path
        self._chromium_path = chromium_path
        self.n_obstacles = n_obstacles
        self.window_size = window_size
        self._game_url = 'file://' + os.path.join(str(os.getcwd()) + '/game/index.html')
        self._chrome_options = Options() 
        ### Initializing the game
        self._chrome_options.add_argument("--window-size=%s" % self.window_size)
        self._driver = webdriver.Chrome(executable_path=self._chromium_path, 
                                        options = self._chrome_options) 
        self._driver.get(self._game_url)
        self._body = self._driver.find_element_by_class_name("offline")
        self._canva = self._driver.find_element_by_class_name("interstitial-wrapper")
        self.pressSpace()
        time.sleep(2)
        self.restart()
        return
    
    def closeDriver(self):
        self._driver.close()

    def reinitializeDriver(self):
        self._driver = webdriver.Chrome(executable_path=self._chromium_path, 
                                        options = self._chrome_options)
        self._driver.get(self._game_url)
        self._body = self._driver.find_element_by_class_name("offline")
        self._body.send_keys(Keys.SPACE)
        self._canva = self._driver.find_element_by_class_name("runner-container")

    def getCrashed(self):
        return self._driver.execute_script("return Runner.instance_.crashed")
    
    def getPlaying(self):
        return self._driver.execute_script("return Runner.instance_.playing")
    
    def restart(self):
        self._driver.execute_script("Runner.instance_.restart()")
        
    def pressSpace(self):
        self._body.send_keys(Keys.ARROW_UP)

    def pressUp(self):
        self._body.send_keys(Keys.SPACE)
        
    def pressDown(self):
        self._body.send_keys(Keys.ARROW_DOWN)
        
    def getScore(self):
        score_array = self._driver.execute_script("return Runner.instance_.distanceMeter.digits")
        score = ''.join(score_array)
        return int(score)
    
    def pause(self):
        return self._driver.execute_script("return Runner.instance_.stop()")
    
    def resume(self):
        return self._driver.execute_script("return Runner.instance_.play()")

    def _getSingleObstacleInfo(self, obstacle, obstacle_num):
        info = {}
        n = str(obstacle_num)
        info['ObstacleDimHeight_'+n] = obstacle['dimensions']['HEIGHT']
        info['ObstacleDimWidth_'+n] = obstacle['dimensions']['WIDTH']
        info['ObstacleGap_'+n] = obstacle['gap']
        info['ObstacleGapCoefficient_'+n] = obstacle['gapCoefficient']
        info['ObstacleSpritePosX_'+n] = obstacle['spritePos']['x']
        info['ObstacleSpritePosY_'+n] = obstacle['spritePos']['y']
        info['ObstacleWidth_'+n] = obstacle['width']
        info['ObstacleXPos_'+n] = obstacle['xPos']
        info['ObstacleYPos_'+n] = obstacle['yPos']
        info['ObstacleTypeConfigHeight_'+n] = obstacle['typeConfig']['height']
        info['ObstacleTypeConfigMinGap_'+n] = obstacle['typeConfig']['minGap']
        info['ObstacleTypeConfigMinSpeed_'+n] = obstacle['typeConfig']['minSpeed']
        info['ObstacleTypeConfigMultipleSpeed_'+n] = obstacle['typeConfig']['multipleSpeed']
        info['ObstacleTypeConfigType_'+n] = obstacle['typeConfig']['type']
        info['ObstacleTypeConfigWidth_'+n] = obstacle['typeConfig']['width']
        info['ObstacleTypeConfigYPos_'+n] = obstacle['typeConfig']['yPos']
        return info

    def _getSingleEmptyObstacleInfo(self, obstacle_num):
        info = {}
        n = str(obstacle_num)
        info['ObstacleTypeConfigType_'+n] = 'Empty'
        return info

    def getObstaclesInfo(self):
        info = {}
        obstacles_list = self._driver.execute_script("return Runner.instance_.horizon.obstacles")
        n_obstacles = min([len(obstacles_list), self.n_obstacles])
        for i in range(n_obstacles):
            obstacle = obstacles_list[i]
            info.update(self._getSingleObstacleInfo(obstacle, i))
        for i in range(n_obstacles, self.n_obstacles):
            info.update(self._getSingleEmptyObstacleInfo(i))
        return info

    def getDinoInfo(self):
        info = {}
        base_info = self._driver.execute_script("return Runner.instance_.tRex")
        info['RunnerCurrentSpeed'] = self._driver.execute_script("return Runner.instance_.currentSpeed")
        info['DinoJumpVelocity'] = base_info['jumpVelocity']
        info['DinoJumping'] = base_info['jumping']
        info['DinoJumpspotX'] = base_info['jumpspotX']
        info['DinoMidair'] = base_info['midair']
        info['DinoMinJumpHeight'] = base_info['minJumpHeight']
        info['DinoReachedMinHeight'] = base_info['reachedMinHeight']
        info['DinoSpeedDrop'] = base_info['speedDrop']
        info['DinoSpritePosX'] = base_info['spritePos']['x']
        info['DinoSpritePosY'] = base_info['spritePos']['y']
        info['DinoStatus'] = base_info['status']
        info['DinoXPos'] = base_info['xPos']
        info['DinoYPos'] = base_info['yPos']
        return info

    def getFrame(self):
        img_png = self._canva.screenshot_as_png
        base_img_pil = Image.open(io.BytesIO(img_png))
        array = np.asarray(base_img_pil)
        return array

    def getPressedKeys(self):
        info = {}
        info['ts'] = []
        info['keys'] = []
        info['type'] = []
        list_pressed_keys = self._driver.execute_script("return Runner.instance_.pressedKeys")
        for e in list_pressed_keys:
            info['ts'].append(e[0]['ts'])
            info['keys'].append(e[0]['key'])
            info['type'].append(e[0]['type'])
        return info
