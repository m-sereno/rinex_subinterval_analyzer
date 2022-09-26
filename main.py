from math import sqrt
from rmse_helper import RmseHelper
import os, shutil

import csv
import matplotlib.pyplot as plt

inputdir = 'C:\\rinex_subinterval_analyzer\\input'
outputdir = 'C:\\rinex_subinterval_analyzer\\output'

ignoreCount = {
    "05": 3,
    "10": 2,
    "base": 0,
    "default": 1
}

point_int_count = {}
pointNamesList = []
intervalsList = []

slicesData = []

# Preliminar: Limpa tudo
for filename in os.listdir(outputdir):
    file_path = os.path.join(outputdir, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

# NAVEGAR: Ponto -> Intervalo -> Arquivo

for subdir, dirs, files in os.walk(inputdir):
    for file in files:

        ext = file.split('.')[-1]
        if ext != 'txt':
            continue
        if file.find('LEIAME') != -1:
            continue

        fullPath = os.path.join(subdir, file)

        # === OBTER: pointName, interval, rinex, utmn, utme

        pointName = subdir.split('\\')[-2]
        interval = subdir.split('\\')[-1]

        dict_key = pointName + "###" + interval
        if dict_key not in point_int_count:
            point_int_count[dict_key] = 0
        
        point_int_count[dict_key] += 1
        ignoreForThisInt = ignoreCount.get(interval, ignoreCount['default'])
        if point_int_count[dict_key] <= ignoreForThisInt:
            continue

        if pointName not in pointNamesList:
            pointNamesList.append(pointName)
        
        if interval not in intervalsList and interval != "base":
            intervalsList.append(interval)

        with open(fullPath, encoding="utf8") as f:
            lines = f.readlines()

            lineToCheck = lines[2]
            if lineToCheck == "Arquivo não processado!\n":
                print('Failed to process %s.' % (fullPath))
                continue

            antennaLine = lines[6]
            isTopcon = antennaLine == "ANTENA NÃO DISPONÍVEL\n"
            
            rinex = lines[1].split(' ')[-1].replace("\n", "")
            utmn = lines[19].split(' ')[-2]
            utme = lines[20].split(' ')[-2]
            hnor = lines[25].split(' ')[-2]

            # ==== OBJETO DO PONTO:
            sliceObj = {
                "name_str": pointName,
                "int_str": interval,
                "rinex_str": rinex,
                "utmn_str": utmn,
                "utme_str": utme,
                "hnor_str": hnor,
                "isTopcon_bool": isTopcon,
                "dx_num": 0,
                "dy_num": 0,
                "dr_num": 0,
                "dh_num": 0
            }

            slicesData.append(sliceObj)


# ======= CALCULOS =======
x_rmseHelper = RmseHelper()
y_rmseHelper = RmseHelper()
r_rmseHelper = RmseHelper()
h_rmseHelper = RmseHelper()

for i in range(len(slicesData)):
    slice = slicesData[i]
    pointName = slice["name_str"]
    interval = slice["int_str"]
    rinex = slice["rinex_str"]
    utmn = slice["utmn_str"]
    utme = slice["utme_str"]
    hnor = slice["hnor_str"]

    if interval == "base":
        continue

    baseline = next(x for x in slicesData if x["name_str"] == pointName and x["int_str"] == "base")

    # Erros:
    dy = float(utmn.replace(',','.')) - float(baseline["utmn_str"].replace(',','.'))
    dx = float(utme.replace(',','.')) - float(baseline["utme_str"].replace(',','.'))
    dr = sqrt(dx*dx + dy*dy)
    dh = float(hnor.replace(',','.')) - float(baseline["hnor_str"].replace(',','.'))

    slicesData[i]["dy_num"] = dy
    slicesData[i]["dx_num"] = dx
    slicesData[i]["dr_num"] = dr
    slicesData[i]["dh_num"] = dh

    x_rmseHelper.registerLine(pointName, int(interval), dx, rinex)
    y_rmseHelper.registerLine(pointName, int(interval), dy, rinex)
    r_rmseHelper.registerLine(pointName, int(interval), dr, rinex)
    h_rmseHelper.registerLine(pointName, int(interval), dh, rinex)

# ESCREVER NO CSV 'BRUTO':

outtablepath = os.path.join(outputdir, 'table.csv')
keys = slicesData[0].keys()

with open(outtablepath, 'w', newline='') as fw:
    dict_writer = csv.DictWriter(fw, keys, delimiter=';')
    dict_writer.writeheader()
    dict_writer.writerows(slicesData)

# Create Summary File:

summaryTablePath = os.path.join(outputdir, "summary.csv")
with open(summaryTablePath, 'w') as fw:
    fw.write("POINT;IS_TOPCON;INT;COUNT;RMSE Y;RMSE X;RMSE R;RMSE H;MAX_ERR Y;MAX_ERR X;MAX_ERR R;MAX_ERR H;RINEX Y;RINEX X;RINEX R;RINEX H\n")
    for pointNameStr in pointNamesList:
        for intervalStr in intervalsList:
            intervalInt = int(intervalStr)

            count = str(x_rmseHelper.getCount(pointNameStr, intervalInt))

            rmse_x = str(x_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_y = str(y_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_r = str(r_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_h = str(h_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')

            (maxE_x, rin_x) = x_rmseHelper.getMaxError(pointNameStr, intervalInt)
            maxE_x = str(maxE_x).replace('.',',')
            (maxE_y, rin_y) = y_rmseHelper.getMaxError(pointNameStr, intervalInt)
            maxE_y = str(maxE_y).replace('.',',')
            (maxE_r, rin_r) = r_rmseHelper.getMaxError(pointNameStr, intervalInt)
            maxE_r = str(maxE_r).replace('.',',')
            (maxE_h, rin_h) = h_rmseHelper.getMaxError(pointNameStr, intervalInt)
            maxE_h = str(maxE_h).replace('.',',')

            isTopcon = next(x for x in slicesData if x["int_str"] == intervalStr)["isTopcon_bool"]

            fw.write(';'.join([pointNameStr, str(isTopcon), intervalStr, count,
                rmse_y, rmse_x, rmse_r, rmse_h,
                maxE_y, maxE_x, maxE_r, maxE_h,
                rin_y, rin_x, rin_r, rin_h]) + '\n')


# Generate 4 BoxPlots for each point:

for pointNameStr in pointNamesList:
    pointPath = os.path.join(outputdir, 'boxplot_' + pointNameStr)
    os.mkdir(pointPath)

    pointSlices = list(x for x in slicesData if x["name_str"] == pointNameStr)
    dx_plotData = []
    dy_plotData = []
    dr_plotData = []
    dh_plotData = []
    for intervalStr in intervalsList:
        intervalSlices = list(x for x in pointSlices if x["int_str"] == intervalStr)
        dx_Data = list(map(lambda x: x["dx_num"], intervalSlices))
        dy_Data = list(map(lambda x: x["dy_num"], intervalSlices))
        dr_Data = list(map(lambda x: x["dr_num"], intervalSlices))
        dh_Data = list(map(lambda x: x["dh_num"], intervalSlices))

        dx_plotData.append(dx_Data)
        dy_plotData.append(dy_Data)
        dr_plotData.append(dr_Data)
        dh_plotData.append(dh_Data)
    
    x_fig = plt.figure(figsize=(19,10))
    y_fig = plt.figure(figsize=(19,10))
    r_fig = plt.figure(figsize=(19,10))
    h_fig = plt.figure(figsize=(19,10))

    x_ax = x_fig.add_subplot(111)
    y_ax = y_fig.add_subplot(111)
    r_ax = r_fig.add_subplot(111)
    h_ax = h_fig.add_subplot(111)

    x_bp = x_ax.boxplot(dx_plotData, labels = intervalsList)
    y_bp = y_ax.boxplot(dy_plotData, labels = intervalsList)
    r_bp = r_ax.boxplot(dr_plotData, labels = intervalsList)
    h_bp = h_ax.boxplot(dh_plotData, labels = intervalsList)

    # Reference line at y = 0:
    x_ax.axhline(y=0, color='g')
    y_ax.axhline(y=0, color='g')
    r_ax.axhline(y=0, color='g')
    h_ax.axhline(y=0, color='g')

    x_path = os.path.join(pointPath, 'x.png')
    y_path = os.path.join(pointPath, 'y.png')
    r_path = os.path.join(pointPath, 'r.png')
    h_path = os.path.join(pointPath, 'h.png')

    x_fig.savefig(x_path)
    y_fig.savefig(y_path)
    r_fig.savefig(r_path)
    h_fig.savefig(h_path)

    plt.close('all')