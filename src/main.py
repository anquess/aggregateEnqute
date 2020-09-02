def main():
    import changeMark
    import csv
    import glob
    import qrCodeRead
    
    resultJpgFiles = glob.glob('img\\enquete\\*.jpg')
    
    for resultJpgFile in resultJpgFiles:
        qrMessage = qrCodeRead.qrCodeToStr(resultJpgFile)
        if not qrMessage == "":
            enqueteId = (qrMessage.split('_')[0] + '_' + qrMessage.split('_')[1])
            personalId = qrMessage.split('_')[2:4]
            n_col = int(qrMessage.split('_')[4])
            n_row = int(qrMessage.split('_')[5])

            with open('result/' + enqueteId + '.csv',mode='a',newline="")as f:

                writer = csv.writer(f)
                resultLine = changeMark.changeMarkToStr(resultJpgFile,n_col,n_row,personalId)
                if not resultLine == 'error':
                    print(resultLine)
                    writer.writerow(resultLine)
                else:
                    with open('result/err.txt',mode='a',newline="") as errTxt:
                        errTxt.writerows('err:マークシートが読めなかった,    FileName=' + resultJpgFile)
        else:
            with open('result/err.txt',mode='a',newline="") as errTxt:
                errTxt.writerows('err:QRコードが読めなかった,    FileName=' + resultJpgFile)

if __name__ =='__main__':
    main()