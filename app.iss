[Setup]
; Nome do seu programa e versão
AppName=Sistema de Navegação AED2
AppVersion=1.0
AppPublisher=Guilherme Oliveira
; Onde será instalado (ex: C:\Program Files\NavegacaoAED2)
DefaultDirName={autopf}\NavegacaoAED2
DefaultGroupName=Sistema de Navegação
; Nome do ficheiro final que vai mandar para os seus colegas
OutputBaseFilename=Instalador_Navegacao_v1
Compression=lzma
SolidCompression=yes
; Pede permissão de administrador para instalar
PrivilegesRequired=admin

[Files]
; Aponte para o ficheiro gerado pelo PyInstaller. 
; Coloque o caminho completo se o ficheiro .iss não estiver na mesma pasta.
Source: "C:\Users\Lucas\OneDrive\Desktop\Grafo--AED2\Grafo---AED2\src\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Cria atalho no Menu Iniciar
Name: "{group}\Sistema de Navegação"; Filename: "{app}\main.exe"
; Cria atalho na Área de Trabalho
Name: "{autodesktop}\Sistema de Navegação"; Filename: "{app}\main.exe"