@echo off
echo --- Iniciando MyWallet e Gerando Backup ---

:: --- CONFIGURACOES ---
:: O %USERPROFILE% pega sua pasta de usuario automaticamente
set "ORIGEM=%USERPROFILE%\mywallet\db.sqlite3"
set "DESTINO=G:\Meu Drive\Backups_MyWallet"

:: 1. Tenta criar a pasta no Drive se ela nao existir
if not exist "%DESTINO%" mkdir "%DESTINO%"

:: 2. Faz o backup de SEGURANCA (sobrescreve o anterior)
echo [Backup] Salvando copia atual no Google Drive...
copy "%ORIGEM%" "%DESTINO%\backup_antes_de_abrir.sqlite3" /Y

:: 3. Abre o navegador e inicia o sistema
echo [MyWallet] Iniciando servidor...
cd /d "%USERPROFILE%\mywallet"
timeout /t 2 >nul
start http://127.0.0.1:8000
call venv\Scripts\activate
python manage.py runserver

:: 4. (Opcional) Tenta fazer backup ao fechar
:: Isso so roda se voce fechar o servidor usando CTRL+C na janela preta.
:: Se fechar clicando no X, essa parte e ignorada (mas o backup do inicio ja garantiu seus dados).
echo [Backup] Salvando versao pos-uso...
copy "%ORIGEM%" "%DESTINO%\backup_pos_uso.sqlite3" /Y

pause