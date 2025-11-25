#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para processar e concatenar todos os datasets CSV de 2023 e 2024.

Funcionalidades:
1. Processa todos os arquivos CSV nas pastas 2023 e 2024
2. Extrai o nome da estação de cada arquivo
3. Aplica correções (remove metadados, converte separadores, converte decimais)
4. Adiciona coluna "ESTACAO" com o nome da estação
5. Concatena todos os dados em um único CSV
"""

import os
import re
import glob
from pathlib import Path


def detect_encoding(file_path):
    """Detecta o encoding de um arquivo."""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    
    return None


def is_numeric_field(field):
    """
    Verifica se um campo parece ser numérico e pode ter vírgula decimal.
    """
    if not field or field.strip() == '':
        return True
    
    field = field.strip()
    pattern = r'^[\d\s,.\-]+$|^[\d\s]+UTC$'
    return bool(re.match(pattern, field))


def convert_decimal_comma(field):
    """Converte vírgula decimal para ponto em campos numéricos."""
    if not field or field.strip() == '':
        return field
    
    if is_numeric_field(field):
        return field.replace(',', '.')
    
    return field


def extract_station_name(file_path):
    """
    Extrai o nome da estação do arquivo CSV (linha 3).
    Retorna o nome da estação ou None se não encontrar.
    """
    encoding = detect_encoding(file_path)
    if not encoding:
        return None
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        if len(lines) < 3:
            return None
        
        # Linha 3 (índice 2) contém: ESTACAO:;NOME_ESTACAO
        station_line = lines[2].strip()
        parts = station_line.split(';')
        
        if len(parts) >= 2:
            station_name = parts[1].strip()
            return station_name
        
        return None
    except Exception as e:
        print(f"  ⚠ Erro ao extrair nome da estação: {e}")
        return None


def process_csv_file(file_path, station_name):
    """
    Processa um arquivo CSV e retorna as linhas corrigidas.
    
    Args:
        file_path: Caminho do arquivo CSV
        station_name: Nome da estação a ser adicionado
    
    Returns:
        Lista de linhas corrigidas (cabeçalho + dados) ou None em caso de erro
    """
    encoding = detect_encoding(file_path)
    if not encoding:
        print(f"  ⚠ Não foi possível detectar encoding do arquivo")
        return None
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
        
        if len(lines) < 10:
            print(f"  ⚠ Arquivo muito curto ({len(lines)} linhas)")
            return None
        
        processed_lines = []
        
        # Processa cabeçalho (linha 9, índice 8)
        header = lines[8].strip()
        header_parts = header.split(';')
        header_parts = [convert_decimal_comma(part) for part in header_parts]
        
        # Adiciona coluna ESTACAO no início do cabeçalho
        header_fixed = 'ESTACAO,' + ','.join(header_parts)
        processed_lines.append(header_fixed)
        
        # Processa dados (linhas 10+, índice 9+)
        for line in lines[9:]:
            line = line.strip()
            if not line:
                continue
            
            # Divide por ;
            parts = line.split(';')
            
            # Converte cada campo
            fixed_parts = []
            for part in parts:
                fixed_part = convert_decimal_comma(part)
                fixed_parts.append(fixed_part)
            
            # Adiciona nome da estação no início (sem aspas)
            fixed_line = f'{station_name},' + ','.join(fixed_parts)
            processed_lines.append(fixed_line)
        
        return processed_lines
        
    except Exception as e:
        print(f"  ⚠ Erro ao processar arquivo: {e}")
        return None


def process_all_datasets(year_folders, output_file):
    """
    Processa todos os arquivos CSV nas pastas especificadas e concatena em um único arquivo.
    
    Args:
        year_folders: Lista de pastas a processar (ex: ['2023', '2024'])
        output_file: Nome do arquivo de saída
    """
    all_csv_files = []
    seen_files = set()  # Para evitar duplicatas
    
    # Coleta todos os arquivos CSV
    for folder in year_folders:
        if not os.path.exists(folder):
            print(f"⚠ Pasta '{folder}' não encontrada. Pulando...")
            continue
        
        # Busca arquivos .CSV e .csv
        csv_pattern_upper = os.path.join(folder, '*.CSV')
        csv_pattern_lower = os.path.join(folder, '*.csv')
        
        csv_files_upper = glob.glob(csv_pattern_upper, recursive=False)
        csv_files_lower = glob.glob(csv_pattern_lower, recursive=False)
        
        # Adiciona arquivos únicos (normaliza caminho para evitar duplicatas no Windows)
        for csv_file in csv_files_upper + csv_files_lower:
            normalized_path = os.path.normpath(csv_file).lower()
            if normalized_path not in seen_files:
                seen_files.add(normalized_path)
                all_csv_files.append(csv_file)
    
    if not all_csv_files:
        print("❌ Nenhum arquivo CSV encontrado nas pastas especificadas.")
        return False
    
    print(f"📁 Encontrados {len(all_csv_files)} arquivos CSV para processar\n")
    
    all_data = []
    header_written = False
    processed_count = 0
    error_count = 0
    
    # Processa cada arquivo
    for csv_file in sorted(all_csv_files):
        file_name = os.path.basename(csv_file)
        print(f"📄 Processando: {file_name}")
        
        # Extrai nome da estação
        station_name = extract_station_name(csv_file)
        if not station_name:
            print(f"  ⚠ Não foi possível extrair nome da estação. Usando nome do arquivo.")
            # Tenta extrair do nome do arquivo como fallback
            # Formato: INMET_NE_PE_A322_GARANHUNS_...
            match = re.search(r'_([A-Z\s]+)_\d', file_name)
            if match:
                station_name = match.group(1).strip()
            else:
                station_name = os.path.splitext(file_name)[0]
        
        print(f"  🏢 Estação: {station_name}")
        
        # Processa arquivo
        processed_lines = process_csv_file(csv_file, station_name)
        
        if processed_lines:
            # Adiciona cabeçalho apenas uma vez
            if not header_written:
                all_data.append(processed_lines[0])
                header_written = True
            
            # Adiciona dados (pula o cabeçalho se já foi escrito)
            start_idx = 1 if header_written else 0
            all_data.extend(processed_lines[1:])
            
            data_lines = len(processed_lines) - 1
            print(f"  ✓ {data_lines} linhas de dados processadas")
            processed_count += 1
        else:
            print(f"  ❌ Erro ao processar arquivo")
            error_count += 1
        
        print()
    
    # Escreve arquivo consolidado
    if not all_data:
        print("❌ Nenhum dado foi processado com sucesso.")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for line in all_data:
                outfile.write(line + '\n')
        
        print("=" * 60)
        print(f"✓ Processamento concluído com sucesso!")
        print(f"  Arquivos processados: {processed_count}")
        print(f"  Arquivos com erro: {error_count}")
        print(f"  Total de linhas (incluindo cabeçalho): {len(all_data)}")
        print(f"  Arquivo de saída: {output_file}")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao escrever arquivo de saída: {e}")
        return False


def main():
    """Função principal."""
    import sys
    
    # Pastas a processar
    year_folders = ['2023', '2024']
    
    # Arquivo de saída
    output_file = 'dados_consolidados_2023_2024.csv'
    
    # Permite especificar arquivo de saída via argumento
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    print("🚀 Iniciando processamento de datasets...")
    print(f"📂 Pastas: {', '.join(year_folders)}")
    print(f"💾 Arquivo de saída: {output_file}\n")
    
    success = process_all_datasets(year_folders, output_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

