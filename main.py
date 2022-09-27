from math import sqrt
from hypothesisTestingHelper import HypothesisTestingHelper
from infoTextParser import InfoTextParser
from plottingHelper import PlottingHelper
from rmse_helper import RmseHelper
import os, shutil

import csv

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

            infoText = InfoTextParser(lines)

            if(infoText.notProcessed()):
                print('Failed to process %s.' % (fullPath))
                continue

            # Intervalo medido deve ter pelo menos 85% do desejado:
            trackingTimedelta = infoText.trackingDuration()
            trk_s = trackingTimedelta.total_seconds()
            tgt_s = 1 if interval == "base" else int(interval) * 60
            relativeCoverage = trk_s/tgt_s
            if relativeCoverage < 0.85:
                continue
            
            # ==== OBJETO DO PONTO:
            sliceObj = {
                "name_str": pointName,
                "int_str": interval,
                "rinex_str": infoText.rinex(),
                "utmn_str": infoText.utmn(),
                "utme_str": infoText.utme(),
                "hnor_str": infoText.hnor(),
                "isTopcon_bool": infoText.isTopcon(),
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

plottingHelper = PlottingHelper()
boxplot_xlabel = 'Duração dos subintervalos (minutos)'
boxplot_ylabel = 'Diferença (metros)'

for pointNameStr in pointNamesList:
    pointPath = os.path.join(outputdir, pointNameStr)
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

        dx_plotData.append(list(map(abs, dx_Data)))
        dy_plotData.append(list(map(abs, dy_Data)))
        dr_plotData.append(list(map(abs, dr_Data)))
        dh_plotData.append(list(map(abs, dh_Data)))

        # Run the normality tests for this set of datapoints:
        nt_path_x = os.path.join(pointPath, 'NT - ' + intervalStr + ' - dx.png')
        nt_path_y = os.path.join(pointPath, 'NT - ' + intervalStr + ' - dy.png')
        nt_path_h = os.path.join(pointPath, 'NT - ' + intervalStr + ' - dh.png')
        HypothesisTestingHelper.runNormalityTest(dx_Data,'%s %s dx' % (pointNameStr, intervalStr), nt_path_x)
        HypothesisTestingHelper.runNormalityTest(dy_Data, '%s %s dy' % (pointNameStr, intervalStr), nt_path_y)
        HypothesisTestingHelper.runNormalityTest(dh_Data, '%s %s dh' % (pointNameStr, intervalStr), nt_path_h)
    
    plottingHelper.prepareAndSaveMultiBoxplot(
        dx_plotData, intervalsList, os.path.join(pointPath, 'BOXPLOT_x.png'),
        pointNameStr + ' - Distribuição do Módulo do Erro para UTME dados diferentes intervalos de fatiamento',
        boxplot_xlabel, boxplot_ylabel)
    plottingHelper.prepareAndSaveMultiBoxplot(
        dy_plotData, intervalsList, os.path.join(pointPath, 'BOXPLOT_y.png'),
        pointNameStr + ' - Distribuição do Módulo do Erro para UTMN dados diferentes intervalos de fatiamento',
        boxplot_xlabel, boxplot_ylabel)
    plottingHelper.prepareAndSaveMultiBoxplot(
        dr_plotData, intervalsList, os.path.join(pointPath, 'BOXPLOT_r.png'),
        pointNameStr + ' - Distribuição da Distância Euclidiana à coordenada esperada dados diferentes intervalos de fatiamento',
        boxplot_xlabel, boxplot_ylabel)
    plottingHelper.prepareAndSaveMultiBoxplot(
        dh_plotData, intervalsList, os.path.join(pointPath, 'BOXPLOT_h.png'),
        pointNameStr + ' - Distribuição do Módulo do Erro para HNOR dados diferentes intervalos de fatiamento',
        boxplot_xlabel, boxplot_ylabel)


# Generate a "summary" boxplot for x, y, h and r (considering all points):

dx_plotData = []
dy_plotData = []
dr_plotData = []
dh_plotData = []

for intervalStr in intervalsList:
    intervalSlices = list(x for x in slicesData if x["int_str"] == intervalStr)

    dx_Data = list(map(lambda x: x["dx_num"], intervalSlices))
    dy_Data = list(map(lambda x: x["dy_num"], intervalSlices))
    dr_Data = list(map(lambda x: x["dr_num"], intervalSlices))
    dh_Data = list(map(lambda x: x["dh_num"], intervalSlices))

    dx_plotData.append(list(map(abs, dx_Data)))
    dy_plotData.append(list(map(abs, dy_Data)))
    dr_plotData.append(list(map(abs, dr_Data)))
    dh_plotData.append(list(map(abs, dh_Data)))

    # Run the grouped normality tests for this subslicing interval:
    nt_path_x = os.path.join(outputdir, 'NT - ' + intervalStr + ' - dx.png')
    nt_path_y = os.path.join(outputdir, 'NT - ' + intervalStr + ' - dy.png')
    nt_path_h = os.path.join(outputdir, 'NT - ' + intervalStr + ' - dh.png')
    HypothesisTestingHelper.runNormalityTest(dx_Data,'%s dx' % (intervalStr), nt_path_x)
    HypothesisTestingHelper.runNormalityTest(dy_Data, '%s dy' % (intervalStr), nt_path_y)
    HypothesisTestingHelper.runNormalityTest(dh_Data, '%s dh' % (intervalStr), nt_path_h)

plottingHelper.prepareAndSaveMultiBoxplot(
    dx_plotData, intervalsList, os.path.join(outputdir, 'summary_boxplot_x.png'),
    'Distribuição do Módulo do Erro para UTME dados diferentes intervalos de fatiamento',
    boxplot_xlabel, boxplot_ylabel)
plottingHelper.prepareAndSaveMultiBoxplot(
    dy_plotData, intervalsList, os.path.join(outputdir, 'summary_boxplot_y.png'),
    'Distribuição do Módulo do Erro para UTMN dados diferentes intervalos de fatiamento',
    boxplot_xlabel, boxplot_ylabel)
plottingHelper.prepareAndSaveMultiBoxplot(
    dr_plotData, intervalsList, os.path.join(outputdir, 'summary_boxplot_r.png'),
    'Distribuição da Distância Euclidiana à coordenada esperada dados diferentes intervalos de fatiamento',
    boxplot_xlabel, boxplot_ylabel)
plottingHelper.prepareAndSaveMultiBoxplot(
    dh_plotData, intervalsList, os.path.join(outputdir, 'summary_boxplot_h.png'),
    'Distribuição do Módulo do Erro para HNOR dados diferentes intervalos de fatiamento',
    boxplot_xlabel, boxplot_ylabel)