#!/bin/bash

set -e

cd "$(dirname "$0")/.."

echo "Iniciando o processo de build do Sistema de Navegação AED2..."

echo "Garantindo a estrutura de diretórios..."
mkdir -p releases
mkdir -p build_tools/NavegacaoAED2.AppDir/usr/bin
mkdir -p data/out

echo "Limpando cache de compilações anteriores..."
rm -rf build/ dist/ main.spec

echo "Compilando o código Python..."
pyinstaller --noconfirm --noconsole --onefile --paths=src src/main.py

echo "Copiando o binário para o AppDir..."
cp dist/main build_tools/NavegacaoAED2.AppDir/usr/bin/navegacao-aed2
chmod +x build_tools/NavegacaoAED2.AppDir/usr/bin/navegacao-aed2

if [ ! -f "build_tools/appimagetool-x86_64.AppImage" ]; then
    echo "Baixando a ferramenta appimagetool..."
    wget -q -O build_tools/appimagetool-x86_64.AppImage https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x build_tools/appimagetool-x86_64.AppImage
fi

echo "Gerando o ficheiro .AppImage final..."
./build_tools/appimagetool-x86_64.AppImage build_tools/NavegacaoAED2.AppDir

echo "Movendo executável para a pasta releases..."
mv Navegação_AED2-x86_64.AppImage releases/

echo "Limpando ficheiros temporários do PyInstaller..."
rm -rf build/ dist/ main.spec

echo "Build concluído com sucesso!"
echo "O seu executável está pronto em: releases/Navegação_AED2-x86_64.AppImage"