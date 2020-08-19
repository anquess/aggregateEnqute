def main():
    import changeMark
    import csv
    import glob
    import qrCodeRead

    resultJpgFiles = glob.glob('img/enquete/*.jpg')
    for resultJpgFile in resultJpgFiles:
        csvFileName = qrCodeRead.qrCodeToStr(resultJpgFile)
        if not csvFileName == "":
            outputCsvFile = open('result/' + csvFileName + '.csv', 'w',newline="")
            writer = csv.writer(outputCsvFile)
            n_col = int(csvFileName.split('_')[4])
            n_row = int(csvFileName.split('_')[5])
            print(csvFileName)
            print('n_col' + str(n_col))
            print('n_row' + str(n_row))
            resultLine = changeMark.changeMarkToStr(resultJpgFile,n_col,n_row)
            writer.writerows(resultLine)
            outputCsvFile.close()
        else:
            with open('result/err.txt','w+',newline="") as errTxt:
                errTxt.write('err:QRコードが読めなかった,    FileName=',resultJpgFile)

if __name__ =='__main__':
    main()