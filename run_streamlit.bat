@echo off
echo ============================================================
echo Inventory Anomaly Detector - Interface Web
echo ============================================================
echo.
echo Iniciando servidor Streamlit...
echo.
echo Acesse no navegador:
echo   http://localhost:8501
echo.
echo Para parar, pressione Ctrl+C
echo.
echo ============================================================
echo.

py -m streamlit run app.py --server.port 8501

pause

