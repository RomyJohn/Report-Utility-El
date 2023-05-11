@ECHO OFF
TITLE Eleserv utility
:: This is a comment
cd code
set classpath="D:\ReportUtility\code\marvin\framework\marvin_1.5.5.jar;"

java -Xmx512m -cp %classpath%;D:\ReportUtility\code\eleservAutomationUtility.jar com.eleserv.wordParser.App
ECHO Congratulations! Batch file executed successfully.
PAUSE