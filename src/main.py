def main():
    import changeMark
    import csv
    import glob
    import qrCodeRead
    
    resultJpgFiles = glob.glob('img\\enquete\\*.jpg')
    
    for resultJpgFile in resultJpgFiles:
        csvFileName = qrCodeRead.qrCodeToStr(resultJpgFile)
        if not csvFileName == "":
#            outputCsvFile = open('result/' + csvFileName + '.csv',mode='w',newline="")
#            with open('result/' + csvFileName + '.csv',mode='w',newline="")as f:
            with open('result/result.csv',mode='a',newline="")as f:
            
                writer = csv.writer(f)

                message = (csvFileName.split('_')[0:4])
                n_col = int(csvFileName.split('_')[4])
                n_row = int(csvFileName.split('_')[5])

                resultLine = changeMark.changeMarkToStr(resultJpgFile,n_col,n_row,message)
                if not resultLine == 'error':
                    print(resultLine)
                    writer.writerow(resultLine)
#                    outputCsvFile.close()
                else:
                    with open('result/err.txt',mode='a',newline="") as errTxt:
                        errTxt.writerows('err:マークシートが読めなかった,    FileName=' + resultJpgFile)
        else:
            with open('result/err.txt',mode='a',newline="") as errTxt:
                errTxt.writerows('err:QRコードが読めなかった,    FileName=' + resultJpgFile)

if __name__ =='__main__':
    main()