def main():
    import changeMark
    import csv
    import glob
    import qrCodeRead
    
    resultJpgFiles = glob.glob('img\\enquete\\*.jpg')
    
    for resultJpgFile in resultJpgFiles:
        csvFileName = qrCodeRead.qrCodeToStr(resultJpgFile)
        if not csvFileName == "":
            outputCsvFile = open('result/' + csvFileName + '.csv',mode='w',newline="")
            writer = csv.writer(outputCsvFile)
            message = (csvFileName.split('_')[0:4])
            n_col = int(csvFileName.split('_')[4])
            n_row = int(csvFileName.split('_')[5])

            resultLine = changeMark.changeMarkToStr(resultJpgFile,n_col,n_row,message)
            if not resultLine == 'error':
                writer.writerows(resultLine)
                outputCsvFile.close()
            else:
                with open('result/err.txt',mode='a',newline="") as errTxt:
                    errTxt.writerows('err:マークシートが読めなかった,    FileName=' + resultJpgFile)
        else:
            with open('result/err.txt',mode='a',newline="") as errTxt:
                errTxt.writerows('err:QRコードが読めなかった,    FileName=' + resultJpgFile)

if __name__ =='__main__':
    main()