import os
from statistics import mean
import numpy as np
from time import sleep


# function to calculate 10-point linear regression slope and y-intercept
def best_fit_slope_and_intercept(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs * ys)) /
         ((mean(xs) * mean(xs)) - mean(xs * xs)))

    b = mean(ys) - m * mean(xs)

    return m, b


# constants
DELIM = ','
tcr_set = 36.6         # core set-point degC Temperature
tsk_set = 34.1         # skin set-point degC Temperature
cp_body = 3490         # Specific Heat capacity of body (J/(Kg.K)
bfn = 6.3              # Neutral skin blood flow (g/m2.s)
c_dil = 50             # Specific heat (constant) for skin blood flow
s_tr = 0.5             # Heat storage constriction (constant) for skin blood flow
t_thresh = 2           # temperature change threshold for max heat-storage

# lists for storage of previous values
storage_body = []
storage_body_kcal = []
core_temp = []
skin_temp = []

# testing --------------------------------------------------------------------------
f = open('C:\\Users\\ATOM\\Downloads\\Log.csv', 'r')
f.readline()
# --------------------------------------------------------------------------


# the function that is called when webpage is opened
def start(weight):
    if not os.path.exists("temp.csv"):
        fp = open('temp.csv', 'w')
        header = "Time" + DELIM + "core_temp" + DELIM + "neck_temp" + DELIM + "arm_temp" + DELIM + \
                 "back_temp" + DELIM + "shin_temp" + DELIM + "flags" + "\n"
        fp.write(header)
        fp.close()

    file = open("temp.csv", "a")    # temporary file that stores received input data
    params = []     # list for return values to webpage

    # release this on real-time data ----------------------
    # arr = [item for item in input("Enter the list items : ").split()]   # input every minute
    # --------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # # specific for testing
    data = f.readline().strip()
    if data == '':
        sleep(60000)
    print(data)
    arr = data.split(",")
    # -------------------------------------------------------------------------------

    curr_time = arr[0]  # time in minutes

    # averages each minute
    curr_core_temp = float(arr[1])
    curr_neck_temp = float(arr[2])
    curr_arm_temp = float(arr[3])
    curr_back_temp = float(arr[4])
    curr_shin_temp = float(arr[5])

    # status at each minute
    curr_flags = str(arr[6])

    # dictionary to store input data
    heatdata = {'Core': curr_core_temp, 'Neck_S': curr_neck_temp, 'Arm_S': curr_arm_temp,
                'Shin_S': curr_shin_temp, 'Scapula_S': curr_back_temp, 'Stor_body': 0.0,
                'Stor_bodykCal': 0.0}

    # data calculated at curr time T
    maxHS = ((weight * cp_body * t_thresh) / 1000)/4.184  # mc(dt), J to kJ
    threshold = (weight * 3490.0 * 2) / 1000

    # data calculated at time T+1
    heatdata['Skin'] = ((0.28 * heatdata['Neck_S']) + (0.28 * heatdata['Scapula_S'])
                        + (0.16 * heatdata['Arm_S']) + (
                                    0.28 * heatdata['Shin_S']))  # Ramanathan weighing coefficient
    heatdata['TS_cr'] = heatdata['Core'] - tcr_set  # Core thermal signal
    if heatdata['TS_cr'] < 0:
        heatdata['TS_cr'] = 0  # converting all negative value to 0
    heatdata['TS_sk'] = tsk_set - heatdata['Skin']  # Skin thermal signal
    if heatdata['TS_sk'] < 0:
        heatdata['TS_sk'] = 0  # converting all negative value to 0

    # appending data to be used later
    skin_temp.append(heatdata['TS_sk'])
    core_temp.append(heatdata['TS_cr'])

    if len(skin_temp) > 2:
        skin_temp.pop(0)
        core_temp.pop(0)

    # data calculated using time T+1, T+2
    if len(skin_temp) == 2:
        heatdata['Q_bl'] = (bfn + c_dil * heatdata['TS_cr']) / (
                    1 + s_tr * heatdata['TS_sk'])  # Peripheral Blood flow, L/(h.m2) ASHRAE 2005
        heatdata['alpha_sk'] = 0.04177 + (
                    0.74518 / (heatdata['Q_bl'] + 0.58541))  # alpha skin , ASHRAE 2017, Gagge 1986
        heatdata['Stor_cr'] = (1 - heatdata['alpha_sk']) * weight * cp_body * (core_temp[1] - core_temp[0])  # heat storage in core(J)
        heatdata['Stor_sk'] = heatdata['alpha_sk'] * weight * cp_body * (skin_temp[1] - skin_temp[0])  # heat storage in skin(J)
        heatdata['Stor_body'] = (heatdata['Stor_cr'] + heatdata[
            'Stor_sk']) / 1000  # heat storage in body(J) converted to kJ by dividing 1000
        # above value to be used for predition, also for percentage display and guage
        heatdata['Stor_bodykCal'] += (heatdata['Stor_body'] / 4.184)  # Conver kJ to kcal
        if heatdata['Stor_bodykCal'] < 0:
            heatdata['Stor_bodykCal'] = 0
        # above value to be used just for display on app in kcal
        storage_body.append(heatdata['Stor_body'])

    recovery = 0
    x_intercept = 0
    if len(storage_body) == 10:
        xs = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        ys = np.array(storage_body)
        m, b = best_fit_slope_and_intercept(xs, ys)
        if m>0:             # indicates danger
            recovery = 0
            x_intercept = (threshold - b) / m
        else:           # indicates recovery
            recovery = 1
            x_intercept = -1*b/m
        if x_intercept > 30:    # indicates no fear/stress
            recovery = 2
        storage_body.pop(0)     # popping to make sure no of values is 10 always

    # return values
    params.append(round(curr_core_temp,1))
    params.append(round(heatdata['Skin'],1))
    params.append(int(maxHS))
    params.append(int(heatdata['Stor_body']))
    params.append(round(heatdata['Stor_bodykCal'],2))
    params.append(recovery)
    params.append(int(x_intercept))
    params.append(curr_flags)

    # file append values
    line = curr_time + DELIM + str(curr_core_temp) + DELIM + str(curr_neck_temp) + DELIM + str(curr_arm_temp) + DELIM + str(curr_back_temp) + DELIM + str(curr_shin_temp) + DELIM + str(curr_flags) + "\n"
    file.write(line)
    file.close()
    print(params)   # testing
    return params







