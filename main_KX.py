import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import serial
import time
import sys
import pyvisa
import scipy as sp
import pandas as pd


#保存地址   
BASE_FILE_NAME = "pressure_data20250226_3.39_20v_1" #文件名
BASE_DIRECTORY = "D:\\acoustic_pressure_measurement\\XY\\20250305"

#导出数据到csv文件函数
def Save_data_to_CSV(V,base_file_name,base_Dir):
    df = pd.DataFrame(V)
    file_name = base_Dir + base_file_name + ".csv"
    df.to_csv(file_name,index = False, header = False)
    return


##***移动平台设置***

step = 15 #单步距离
x_len = 1500 #x方向总长度
y_len = 1500 #y方向总长度
x_n = x_len // step #x方向步数
y_n = y_len // step #y方向步数
n = str(int(step / 1000 * 12800)) #步进电机转动圈数
#***示波器连接和设置****************************************************************************

#要求的点数
USER_REQUESTED_POINTS = 1000

#初始化参数
SCOPE_VISA_ADDRESS = "USB0::0x2A8D::0x178B::CN59500178::INSTR" #通过NI VISA获取

GLOBAL_TOUT =  10000 # IO time out in milliseconds

rm = pyvisa.ResourceManager('C:\\Windows\\System32\\visa32.dll') # this uses PyVisa

## Open Connection建立连接
## Define & open the scope by the VISA address ; # This uses PyVisa
try:
    KsInfiniiVisionX = rm.open_resource(SCOPE_VISA_ADDRESS)
except Exception:
    print ("Unable to connect to oscilloscope at " + str(SCOPE_VISA_ADDRESS) + ". Aborting script.\n")
    sys.exit()
#连接移动平台
ser = serial.Serial('COM3',57600,timeout=1) #连接com4端口，口的波特率为57600,timeout为连接超时
#if(ser.isOpen()):
    #print('open')

#设置全局超时
#这可以在任何地方使用，但是本地超时用于武装，触发和完成收购... 因此它主要处理 IO 超时
KsInfiniiVisionX.timeout = GLOBAL_TOUT

## Clear the instrument bus
KsInfiniiVisionX.clear()

def Get_Vpp(KsInfiniiVisionX):
#确定哪些通道处于 AND 已获得数据-Scope 应该已经获得数据并处于停止状态(Run/Stop 按钮为红色)。
## Get Number of analog channels on scope 获取范围内模拟通道的数量
    IDN = str(KsInfiniiVisionX.query("*IDN?"))
## Parse IDN 解析IDN
    IDN = IDN.split(',') # IDN parts are separated by commas, so parse on the commas
    MODEL = IDN[1]
    if list(MODEL[1]) == "9": # This is the test for the PXIe scope, M942xA)
        NUMBER_ANALOG_CHS = 2
    else:
        NUMBER_ANALOG_CHS = int(MODEL[len(MODEL)-2])
    if NUMBER_ANALOG_CHS == 2:
        CHS_LIST = [0,0] # Create empty array to store channel states
    else:
        CHS_LIST = [0,0,0,0]
    NUMBER_CHANNELS_ON = 0
## After the CHS_LIST array is filled it could, for example look like: if chs 1,3 and 4 were on, CHS_LIST = [1,0,1,1]

# # 预先分配垂直前导轨和通道单元的支架
    ANALOGVERTPRES = np.zeros([12])
    CH_UNITS = ["BLANK", "BLANK", "BLANK", "BLANK"]


# # 实际上找到哪个频道是开着的，已经获得了数据，如果需要的话还可以得到前导信息。
#这里的假设是，如果通道关闭，即使后面有数据，也无法从中检索数据。
#注意，如果通道规模(和开/关)没有改变，那么对于重复获取只需要执行一次。
    KsInfiniiVisionX.write(":WAVeform:POINts:MODE MAX")# MAX 模式适用于所有的获取类型，所以这样做是为了避免 Acq。类型与点模式问题。后来根据特定的获取类型进行了调整。

    ch = 1 # Channel number
    for each_value in CHS_LIST:
        On_Off = int(KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":DISPlay?")) # Is the channel displayed? If not, don't pull.
        if On_Off == 1: # Only ask if needed... but... the scope can acquire waveform data even if the channel is off (in some cases) - so modify as needed
            Channel_Acquired = int(KsInfiniiVisionX.query(":WAVeform:SOURce CHANnel" + str(ch) + ";POINts?")) # If this returns a zero, then this channel did not capture data and thus there are no points
        ## Note that setting the :WAV:SOUR to some channel has the effect of turning it on
        else:
            Channel_Acquired = 0
        if Channel_Acquired == 0 or On_Off == 0: # Channel is off or no data acquired
            KsInfiniiVisionX.write(":CHANnel" + str(ch) + ":DISPlay OFF") # Setting a channel to be a waveform source turns it on... so if here, turn it off.
            CHS_LIST[ch-1] = 0 # Recall that python indices start at 0, so ch1 is index 0
        else: # Channel is on AND data acquired
            CHS_LIST[ch-1] = 1 # After the CHS_LIST array is filled it could, for example look like: if chs 1,3 and 4 were on, CHS_LIST = [1,0,1,1]
            NUMBER_CHANNELS_ON += 1
        ## Might as well get the pre-amble info now
            Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',') # ## The programmer's guide has a very good description of this, under the info on :WAVeform:PREamble.
            ## In above line, the waveform source is already set; no need to reset it.
            ANALOGVERTPRES[ch-1]  = float(Pre[7]) # Y INCrement, Voltage difference between data points; Could also be found with :WAVeform:YINCrement? after setting :WAVeform:SOURce增量，数据点之间的电压差; 
            ANALOGVERTPRES[ch+3]  = float(Pre[8]) # Y ORIGin, Voltage at center screen; Could also be found with :WAVeform:YORigin? after setting :WAVeform:SOURceY YORIGIN，电压在中心屏幕; 
            ANALOGVERTPRES[ch+7]  = float(Pre[9]) # Y REFerence, Specifies the data point where y-origin occurs, always zero; Could also be found with :WAVeform:YREFerence? after setting :WAVeform:SOURce指定出现 y 源的数据点，始终为零; 
        ## In most cases this will need to be done for each channel as the vertical scale and offset will differ. However,
            ## if the vertical scales and offset are identical, the values for one channel can be used for the others.
            ## For math waveforms, this should always be done.
            CH_UNITS[ch-1] = str(KsInfiniiVisionX.query(":CHANnel" + str(ch) + ":UNITs?").strip('\n')) # This isn't really needed but is included for completeness
        ch += 1
    del ch, each_value, On_Off, Channel_Acquired
##########################
    if NUMBER_CHANNELS_ON == 0:
        KsInfiniiVisionX.clear()
        KsInfiniiVisionX.close()
        sys.exit("No data has been acquired. Properly closing scope and aborting script.")

############################################
## Find first channel on (as needed/desired) 找到第一个开着的信号通道
    ch = 1
    for each_value in CHS_LIST:
        if each_value == 1:
            FIRST_CHANNEL_ON = ch
            break
        ch +=1
    del ch, each_value

############################################
## Find last channel on (as needed/desired)找到最后一个开着的通道
    ch = 1
    for each_value in CHS_LIST:
        if each_value == 1:
            LAST_CHANNEL_ON = ch
        ch +=1
    del ch, each_value

############################################
## Create list of Channel Numbers that are on创建开着的信号通道的列表
    CHS_ON = [] # Empty list
    ch = 1
    for each_value in CHS_LIST:
        if each_value == 1:
            CHS_ON.append(int(ch)) # for example, if chs 1,3 and 4 were on, CHS_ON = [1,3,4]
        ch +=1
    del ch, each_value

#设置数据导出——对于重复性获取，只需要执行一次，除非更改设置
    KsInfiniiVisionX.write(":WAVeform:FORMat WORD") # 16 bit word format... or BYTE for 8 bit format - WORD recommended, see more comments below when the data is actually retrieved
    ## WORD format especially  recommended  for Average and High Res. Acq. Types, which can produce more than 8 bits of resolution.
    KsInfiniiVisionX.write(":WAVeform:BYTeorder LSBFirst") # Explicitly set this to avoid confusion - only applies to WORD FORMat
    KsInfiniiVisionX.write(":WAVeform:UNSigned 0") # Explicitly set this to avoid confusion

# # 设置和获取要检索的点-对于重复的获取，这只需要做一次，除非范围设置被更改
#这是非常重要的，但是下面的算法总是抛出一个错误，只要 USER _ REQUESTED _ POINTS 是一个正整数(正整数)

# # 确定采集类型，正确设置点模式
    ACQ_TYPE = str(KsInfiniiVisionX.query(":ACQuire:TYPE?")).strip("\n")
        ## This can also be done when pulling pre-ambles (pre[1]) or may be known ahead of time, but since the script is supposed to find everything, it is done now.
    if ACQ_TYPE == "AVER" or ACQ_TYPE == "HRES": # Don't need to check for both types of mnemonics like this: if ACQ_TYPE == "AVER" or ACQ_TYPE == "AVERage": becasue the scope ALWAYS returns the short form
        POINTS_MODE = "NORMal" # Use for Average and High Resoultion acquisition Types.
        ## If the :WAVeform:POINts:MODE is RAW, and the Acquisition Type is Average, the number of points available is 0. If :WAVeform:POINts:MODE is MAX, it may or may not return 0 points.
        ## If the :WAVeform:POINts:MODE is RAW, and the Acquisition Type is High Resolution, then the effect is (mostly) the same as if the Acq. Type was Normal (no box-car averaging).
        ## Note: if you use :SINGle to acquire the waveform in AVERage Acq. Type, no average is performed, and RAW works. See sample script "InfiniiVision_2_Simple_Synchronization_Methods.py"
    else:
        POINTS_MODE = "RAW" # Use for Acq. Type NORMal or PEAK
    ## Note, if using "precision mode" on 5/6/70000s or X6000A, then you must use POINTS_MODE = "NORMal" to get the "precision record."


# # 查找范围的最大点，查找想要的点，查找实际返回的点数
#关键点: 数据必须显示在屏幕上才能检索。如果有数据离开屏幕，: WAVeform: 点？不会“看到”
#附录1展示了如何正确获取屏幕上的所有数据，但是平均和高分辨率采集类型永远不需要这个,
#因为他们基本上不使用屏幕外的数据，你看到的就是你得到的。

#首先，将波形源设置为任何已知开启的信道，并且有点，这里是 FIRST _ Channel _ ON ——如果我们不这样做，它可能被设置为关闭或没有获取数据的信道。
    KsInfiniiVisionX.write(":WAVeform:SOURce CHANnel" + str(FIRST_CHANNEL_ON))
#下一行与前面发送的命令“ : WAVeform: POINts: MODE MAX”相似，但又有所不同。下一个命令是这个脚本中最重要的部分之一。
    KsInfiniiVisionX.write(":WAVeform:POINts MAX")# 这个命令将点模式设置为 MAX，并确保设置要传输的点的最大数目，尽管它们必须仍然在屏幕上
# # 因为上面的“ : WAVeform: POINts MAX”命令也会将: POINts: MODE 更改为 MAXIMum，这可能是件好事，也可能不是件好事，所以请将其更改为下一步需要的内容。
    KsInfiniiVisionX.write(":WAVeform:POINts:MODE " + str(POINTS_MODE))

# # 如果测量也正在进行，那么它们是在“测量记录”上进行的可使用以下方法查阅该记录:
# # : WAVeform: Point: MODE NORMal 而不是: WAVeform: POINts: MODE RAW
# # 详情请参阅程序员指南: WAV: POIN: MODE RAW/NORMal/MAX
#现在找出在给定的点数模式下，当前有多少点数可以转移(必须仍然在屏幕上)
    global USER_REQUESTED_POINTS
    MAX_CURRENTLY_AVAILABLE_POINTS = int(KsInfiniiVisionX.query(":WAVeform:POINts?"))# This is the max number of points currently available - this is for on screen data only - Will not change channel to channel.
    if USER_REQUESTED_POINTS < 100:
        USER_REQUESTED_POINTS = 100
## One may also wish to do other tests, such as: is it a whole number (integer)?, is it real? and so forth...

    if MAX_CURRENTLY_AVAILABLE_POINTS < 100:
        MAX_CURRENTLY_AVAILABLE_POINTS = 100

    if USER_REQUESTED_POINTS > MAX_CURRENTLY_AVAILABLE_POINTS or ACQ_TYPE == "PEAK":
         USER_REQUESTED_POINTS = MAX_CURRENTLY_AVAILABLE_POINTS
     ## Note: for Peak Detect, it is always suggested to transfer the max number of points available so that narrow spikes are not missed.
     ## If the scope is asked for more points than :ACQuire:POINts? (see below) yields, though, not necessarily MAX_CURRENTLY_AVAILABLE_POINTS, it will throw an error, specifically -222,"Data out of range"

## If one wants some other number of points...
## Tell it how many points you want
    KsInfiniiVisionX.write(":WAVeform:POINts " + str(USER_REQUESTED_POINTS))

## Then ask how many points it will actually give you, as it may not give you exactly what you want.
    NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE = int(KsInfiniiVisionX.query(":WAVeform:POINts?"))

#获取定时前导数据，创建时间轴
#我们可以省去前言和分数，以后再处理..。

    Pre = KsInfiniiVisionX.query(":WAVeform:PREamble?").split(',')
# 这确实需要设置为一个打开的通道，但这已经完成了... ... 例如 Pre = KsInfiniVisionX.query (“ : WAVeform: SOURCE CHANnel”+ str (FIRST _ CHANNEL _ ON) + “ ; PREamble?”).分开(’,’)
#虽然这些数值可以用于所有的模拟通道，但是它们需要被检索并分别用于数学波形/其他波形，因为它们可能是不同的。
# ACQ _ TYPE = float (Pre [1]) # 给出作用域获取类型; 这已经在上面的特定脚本中完成了
    X_INCrement = float(Pre[4]) # Time difference between data points; Could also be found with :WAVeform:XINCrement? after setting :WAVeform:SOURce
    X_ORIGin    = float(Pre[5]) # Always the first data point in memory; Could also be found with :WAVeform:XORigin? after setting :WAVeform:SOURce
    X_REFerence = float(Pre[6]) # Specifies the data point associated with x-origin; The x-reference point is the first point displayed and XREFerence is always 0.; Could also be found with :WAVeform:XREFerence? after setting :WAVeform:SOURce
## This could have been pulled earlier...
    DataTime = ((np.linspace(0,NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE-1,NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE)-X_REFerence)*X_INCrement)+X_ORIGin
    if ACQ_TYPE == "PEAK": # This means Peak Detect Acq. Type
        DataTime = np.repeat(DataTime,2)

#预分配数据数组
#显然有很多方法可以将数据放入数组... 这只是其中之一
    if ACQ_TYPE == "PEAK": # This means peak detect mode ### SEE IMPORTANT NOTE ABOUT PEAK DETECT MODE AT VERY END, specific to fast time scales
        Wav_Data = np.zeros([2*NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE,NUMBER_CHANNELS_ON])
    ## Peak detect mode returns twice as many points as the points query, one point each for LOW and HIGH values
    else: # For all other acquistion modes
        Wav_Data = np.zeros([NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE,NUMBER_CHANNELS_ON])

## Get the waveform format获取波形格式
    WFORM = str(KsInfiniiVisionX.query(":WAVeform:FORMat?"))
    if WFORM == "BYTE":
        FORMAT_MULTIPLIER = 1
    else: #WFORM == "WORD"
        FORMAT_MULTIPLIER = 2

    if ACQ_TYPE == "PEAK":
        POINTS_MULTIPLIER = 2 # Recall that Peak Acq. Type basically doubles the number of points.
    else:
        POINTS_MULTIPLIER = 1

    TOTAL_BYTES_TO_XFER = POINTS_MULTIPLIER * NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE * FORMAT_MULTIPLIER + 11

#设置块大小:
    if TOTAL_BYTES_TO_XFER >= 400000:
        KsInfiniiVisionX.chunk_size = TOTAL_BYTES_TO_XFER
## else:
    ## use default size, which is 20480


# # 调出波形数据，放大
    now = time.process_time() # Only to show how long it takes to transfer and scale the data.
    i  = 0 # index of Wav_data, recall that python indices start at 0, so ch1 is index 0

    for channel_number in CHS_ON:
        Wav_Data[:,i] = np.array(KsInfiniiVisionX.query_binary_values(':WAVeform:SOURce CHANnel' + str(channel_number) + ';DATA?', "h", False))
        Wav_Data[:,i] = ((Wav_Data[:,i]-ANALOGVERTPRES[channel_number+7])*ANALOGVERTPRES[channel_number-1])+ANALOGVERTPRES[channel_number+3]
        i +=1

# Reset the chunk size back to default if needed.# 如果需要，将块大小重置为默认值。
    if TOTAL_BYTES_TO_XFER >= 400000:
        KsInfiniiVisionX.chunk_size = 20480
    ## If you don't do this, and now wanted to do something else... such as ask for a measurement result, and leave the chunk size set to something large,
        ## it can really slow down the script, so set it back to default, which works well.

    del i, channel_number
    #print("\n\nIt took " + str(time.process_time() - now) + " seconds to transfer and scale " + str(NUMBER_CHANNELS_ON) + " channel(s). Each channel had " + str(NUMBER_OF_POINTS_TO_ACTUALLY_RETRIEVE) + " points.\n")

    del now
     #find peaks
    #peak_indexes = sp.signal.argrelextrema(Wav_Data,np.greater,order = 1)
    #peak_indexes = peak_indexes[0]
    #peak_y = Wav_Data[peak_indexes]
    #peak_y_mean = np.mean(peak_y)
    peaky = np.max(Wav_Data)

    #find velleys
    #valley_indexes = sp.signal.argrelextrema(Wav_Data,np.less,order = 1)
    #valley_indexes = valley_indexes[0]
    #valley_y = Wav_Data[peak_indexes]
    #valley_y_mean = np.mean(valley_y)
    valleyy = np.min(Wav_Data)
    Vpp = peaky - valleyy
# # 完成范围操作-正确关闭范围连接
    KsInfiniiVisionX.clear()
    KsInfiniiVisionX.close()

   

#del KsInfiniiVisionX


    #print(Vpp)
    return Vpp
#**********************************************************************************************





#X正方向移动一步函数
def X_move(n):
    S = 'DX' + n + ';'
    #print(S)
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

#X负方向移动一步函数
def X_rmove(n):
    S = 'DX-' + n + ';'
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

#Y正方向移动一步函数
def Y_move(n):
    S = 'DY' + n + ';'
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

#Y负方向移动一步函数
def Y_rmove(n):
    S = 'DY-' + n + ';'
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

#Z正方向移动一步函数
def Z_move(n):
    S = 'DZ' + n + ';'
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

#Z负方向移动一步函数
def Z_rmove(n):
    S = 'DZ-' + n + ';'
    char_list = []
    for char in S:
        char_list.append(char.encode('ascii'))
    for i in range(len(char_list)):
        ser.write(char_list[i])
        ser.read(1)
    return

##****

#采集数据函数

#plt.ion()
plt.figure(1)
cmap1 = "jet"

#保存采集的数据的函数
def SaveVpp(x_n,y_n):
    Vpp = np.zeros((int (y_n),int (x_n)))#建立数组存放采集的信号值
    #count = 1
    global BASE_FILE_NAME
    global BASE_DIRECTORY
    for i in np.arange(0,x_n):
        for j in np.arange(0,y_n):
            #采集数据
            Save_data_to_CSV(Vpp,BASE_FILE_NAME,BASE_DIRECTORY)
            ser.flush()
            ser.close()
            KsInfiniiVisionX.open()
            time.sleep(0.1)
            V = Get_Vpp(KsInfiniiVisionX)
            #KsInfiniiVisionX.clear()
            KsInfiniiVisionX.close()
            ser.open()
            if i % 2 == 0:
                Vpp[j][i] = V #保存采集的数据
                #y正方向移动一次
                Y_move(n)
                time.sleep(0.1)

            else:
                Vpp[y_n-1 - j][i] =V #保存采集的数据
                #y负方向移动一次
                Y_rmove(n)
                time.sleep(0.1)
            #global cmap1
            #im = plt.imshow(Vpp,cmap=cmap1)
            #plt.draw()
            #plt.pause(0.5)

            #count = count + 1 #y方向移动一次
        
        X_rmove(n)#x方向移动一次
        
        #time.sleep(1)
        
    return Vpp







Vpp = SaveVpp(x_n, y_n) / 198 *1000

#print(Vpp)
ser.close()
KsInfiniiVisionX.close()


cmap1 = "jet"
im = plt.imshow(Vpp,cmap=cmap1)
clb = plt.colorbar(im,cmap = cmap1)
#plt.ioff()
#plt.savefig(BASE_DIRECTORY + BASE_FILE_NAME +".svg")
plt.show()
