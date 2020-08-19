import changeMark
import csv
import glob
import qrCodeRead


resultJpgFiles = glob.glob('img/enquete/*.jpg')
for resultJpgFile in resultJpgFiles:
    outputCsvFile = open('result/' + qrCodeRead.qrCodeToStr(resultJpgFile) + '.csv', 'w',newline="")
    writer = csv.writer(outputCsvFile)
    
    resultLine = changeMark.changeMarkToStr(resultJpgFile,6,9)
    writer.writerows(resultLine)
outputCsvFile.close()