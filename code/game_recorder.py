import game
import pandas as pd
import copy
import time
import argparse
import os

class game_recorder:
    def __init__(self, game_path, chromium_path):
        self.chromium_path = chromium_path
        self.game_path = game_path
        self.game = None
        self.frame_info = None
        self.pressed_key_log = None
        self.result = None

    def record(self):
        self.game = game.game(self.game_path, self.chromium_path)
        self.game.restart()
        info = []
        while not self.game.getCrashed():
            frame_info = {'frame_ts' : time.time()}
            frame_info.update(self.game.getDinoInfo())
            frame_info.update(self.game.getObstaclesInfo())
            info.append(frame_info)
        self.pressed_key_log = pressed_key_log = self.game.getPressedKeys()
        self.frame_info = pd.DataFrame(info)
        self.game.closeDriver()
        self.game = None

    def proc_result(self):
        n_rows = self.frame_info.shape[0]
        self.result = self.frame_info.assign(key_pressed=pd.Series([None]*n_rows).values,
                                             key_event_type=pd.Series([None]*n_rows).values)
        n_key_events = len(self.pressed_key_log['ts'])
        next_init_pos = 0
        for j in range(n_key_events):
            ts_key = self.pressed_key_log['ts'][j] / (1000.0)
            for i in range(next_init_pos, n_rows):
                next_init_pos += 1
                ts_frame = self.result.iloc[i]['frame_ts']
                if float(ts_key) < float(ts_frame) :
                    self.result.at[i-1, 'key_pressed'] = self.pressed_key_log['keys'][j]
                    self.result.at[i-1, 'key_event_type'] = self.pressed_key_log['type'][j]
                    break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_path", type=str, action='store',
                        help="Path to the game directory!\n ex: game/index.html",
                        default = 'game/index.html')
    parser.add_argument("--chromium_path", type=str, action='store',
                        help="Path to the game directory!\n ex: ./source/chromedriver_mac",
                        default='./source/chromedriver_mac')
    parser.add_argument("--output_folder", type=str, action='store',
                        help="Path to the game directory!\n ex: ./game_records/",
                        default='./game_records/')
    args = vars(parser.parse_args())
    if not os.path.exists(args['output_folder']):
        os.makedirs(args['output_folder'])
    print(args)
    output_file_name = os.path.join(args['output_folder'], 'record_' + str(time.time()) + '.csv')
    gr = game_recorder(args['game_path'], args['chromium_path'])
    gr.record()
    gr.proc_result()
    gr.result.to_csv(output_file_name)

