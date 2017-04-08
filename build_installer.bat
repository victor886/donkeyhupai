rmdir /q /s %cd%\build
rmdir /q /s %cd%\dist
rmdir /q /s %cd%\沪牌助手-2017年4月版
del %cd%\bid.spec
del %cd%\沪牌助手-2017年4月版.rar
C:\Python27\Scripts\pyinstaller --windowed --onefile --icon=%cd%\image\paimai.ico -F %cd%\bid.py
xcopy %cd%\image %cd%\dist\image /e /i /y 
xcopy %cd%\conf %cd%\dist\conf /e /i /y
xcopy %cd%\tessdata %cd%\dist\tessdata /e /i /y
copy %cd%\使用说明.txt %cd%\dist /y 
mkdir %cd%\dist\log
ren %cd%\dist\bid.exe 沪牌助手-2017年4月版.exe
xcopy %cd%\dist %cd%\沪牌助手-2017年4月版 /e /i /y
rar a -r 沪牌助手-2017年4月版.rar 沪牌助手-2017年4月版
pause