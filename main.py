from math import sqrt
from rmse_helper import RmseHelper
import os, shutil
inputdir = 'C:\\rinex_subinterval_analyzer\\input'
outputdir = 'C:\\rinex_subinterval_analyzer\\output'

tableLines = []
point_baseline_dict = {}
linesAsVecs = []

pointNamesList = []
intervalsList = []

isPointTopcon = {}

point_interval_lines = {}
point_int_count = {}

ignoreCount = {
    "05": 3,
    "10": 2,
    "base": 0,
    "default": 1
}

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
            isPointTopcon[pointName] = isTopcon
            
            rinex = lines[1].split(' ')[-1].replace("\n", "")
            utmn = lines[19].split(' ')[-2]
            utme = lines[20].split(' ')[-2]
            hnor = lines[25].split(' ')[-2]

            # === Registrar para calculos posteriores:
            eqVec = [pointName, interval, rinex, utmn, utme, hnor]

            if(interval == "base"):
                point_baseline_dict[pointName] = eqVec
            else:
                linesAsVecs.append(eqVec)
            
            # PREPARAR para escrever nos .csv:
            lineToWrite = ';'.join(eqVec)
            tableLines.append(lineToWrite)


# ESCREVER NO CSV 'BRUTO':

outtablepath = os.path.join(outputdir, 'table.csv')

with open(outtablepath, 'w') as fw:
    fw.write('\n'.join(tableLines) + '\n')


# ======= CALCULOS POSTERIORES =======
x_rmseHelper = RmseHelper()
y_rmseHelper = RmseHelper()
r_rmseHelper = RmseHelper()
h_rmseHelper = RmseHelper()

for i in range(len(linesAsVecs)):
    line = linesAsVecs[i]
    pointName = line[0]
    interval = line[1]
    rinex = line[2]
    utmn = line[3]
    utme = line[4]
    hnor = line[5]

    baseline = point_baseline_dict[pointName]

    # Erros:
    dy = float(utmn.replace(',','.')) - float(baseline[3].replace(',','.'))
    dx = float(utme.replace(',','.')) - float(baseline[4].replace(',','.'))
    dr = sqrt(dx*dx + dy*dy)
    dh = float(hnor.replace(',','.')) - float(baseline[5].replace(',','.'))

    linesAsVecs[i].extend([str(dy).replace('.',','),str(dx).replace('.',','),str(dr).replace('.',','),str(dh).replace('.',',')])

    dict_key = pointName + "###" + interval
    if dict_key not in point_interval_lines:
        point_interval_lines[dict_key] = []
    
    point_interval_lines[dict_key].append(linesAsVecs[i])

    x_rmseHelper.registerLine(pointName, int(interval), dx, rinex)
    y_rmseHelper.registerLine(pointName, int(interval), dy, rinex)
    r_rmseHelper.registerLine(pointName, int(interval), dr, rinex)
    h_rmseHelper.registerLine(pointName, int(interval), dh, rinex)


# Create all remaining directories and files:

for pointNameStr in pointNamesList:
    pointpath = os.path.join(outputdir, pointNameStr)
    os.mkdir(pointpath)
    for intervalStr in intervalsList:
        intervalTablePath = os.path.join(pointpath, (intervalStr + ".csv"))
        with open(intervalTablePath, 'w') as fw:
            dict_key = pointNameStr + "###" + intervalStr

            lines = point_interval_lines[dict_key]
            fw.write("POINT;INT;RINEX;UTMN;UTME;HNOR;DY;DX;DR;DH\n")
            for lineVec in lines:
                fw.write(';'.join(lineVec) + '\n')
    
    resultsTablePath = os.path.join(pointpath, "results.csv")
    with open(resultsTablePath, 'w') as fw:
        fw.write("INT;RMSE Y;RMSE X;RMSE R;RMSE H\n")
        for intervalStr in intervalsList:
            intervalInt = int(intervalStr)

            rmse_x = str(x_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_y = str(y_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_r = str(r_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')
            rmse_h = str(h_rmseHelper.getRmse(pointNameStr, intervalInt)).replace('.',',')

            fw.write(';'.join([intervalStr, rmse_y, rmse_x, rmse_r, rmse_h]) + '\n')

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

            fw.write(';'.join([pointNameStr, str(isPointTopcon[pointNameStr]), intervalStr, count,
                rmse_y, rmse_x, rmse_r, rmse_h,
                maxE_y, maxE_x, maxE_r, maxE_h,
                rin_y, rin_x, rin_r, rin_h]) + '\n')