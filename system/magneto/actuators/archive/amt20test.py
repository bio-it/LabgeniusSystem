# from actuators.amt203 import AMT203
from amt203 import AMT203
from time import sleep


amt203 = AMT203()



if __name__ == '__main__':
    try:
        # for i in range (1, 10):
        while(1):
            # print( amt203.read_abs_pos())
            pos, count = amt203.read_abs_pos()
            print(f'{count}, {pos}')
            sleep(0.001)

    except (KeyboardInterrupt, SystemExit):
        print('\nReceived keyboard interrupt, quitting threads.\n')
        g_is_accepted = False