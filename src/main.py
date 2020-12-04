import logging
import csv
import glob
import os    

import changeMark.changeMark
import qrCodeRead

handler = logging.FileHandler('result/err.txt', encoding='utf-8')
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s %(name)s %(message)s"))

logger = logging.getLogger()
logger.addHandler(handler)
logger = logging.getLogger(__name__)

def main():
    
    resultJpgFiles = glob.glob('img\\enquete\\*.jpg')
    
    for resultJpgFile in resultJpgFiles:
        qrMessage = qrCodeRead.qrCodeToStr(resultJpgFile)
        if not qrMessage == None:
            enqueteId = (qrMessage.split('_')[0] + '_' + qrMessage.split('_')[1])
            personalId = qrMessage.split('_')[2:4]
            n_col = int(qrMessage.split('_')[4])
            n_row = int(qrMessage.split('_')[5])

            if not os.path.isdir('result'):
                os.mkdir('result')
            with open('result/' + enqueteId + '.csv',mode='a',newline="",encoding = "utf_8")as f:

                writer = csv.writer(f)
                resultLine = changeMark.changeMark.changeMarkToStr(resultJpgFile,n_col,n_row,personalId)
                if not resultLine == 'error':
                    logger.info(resultLine)
                    writer.writerow(resultLine)
                else:
                    logger.error('マークシートが読めなかった,' + resultJpgFile)

if __name__ =='__main__':
    main()