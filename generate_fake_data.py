"""
Script para gerar dataset fake de estoque e consumo.
Gera um CSV com dados de série temporal para testes do pipeline.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_fake_inventory_data(
    start_date: str = "2023-01-01",
    end_date: str = "2024-12-31",
    n_products: int = 5,
    output_path: str = "data/inventory_data.csv"
) -> pd.DataFrame:
    """
    Gera dataset fake de estoque e consumo.
    
    Args:
        start_date: Data inicial (YYYY-MM-DD)
        end_date: Data final (YYYY-MM-DD)
        n_products: Número de produtos diferentes
        output_path: Caminho para salvar o CSV
    
    Returns:
        DataFrame com colunas: data, produto_id, estoque, consumo
    """
    # Gerar range de datas
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = pd.date_range(start=start, end=end, freq="D")
    
    # Lista para armazenar dados
    data_list = []
    
    for product_id in range(1, n_products + 1):
        # Parâmetros base para cada produto
        base_consumo = random.uniform(10, 50)
        base_estoque = random.uniform(500, 2000)
        
        # Estoque inicial
        current_estoque = base_estoque
        
        for date in dates:
            # Consumo com tendência e sazonalidade
            # Tendência leve
            days_from_start = (date - start).days
            trend_factor = 1 + (days_from_start / 365) * random.uniform(-0.1, 0.1)
            
            # Sazonalidade semanal
            day_of_week = date.weekday()
            weekly_factor = 1 + 0.2 * np.sin(2 * np.pi * day_of_week / 7)
            
            # Sazonalidade mensal
            day_of_month = date.day
            monthly_factor = 1 + 0.15 * np.sin(2 * np.pi * day_of_month / 30)
            
            # Ruído aleatório
            noise = random.uniform(0.85, 1.15)
            
            # Calcular consumo
            consumo = base_consumo * trend_factor * weekly_factor * monthly_factor * noise
            consumo = max(0, round(consumo, 2))
            
            # Atualizar estoque (reposição periódica)
            if date.day == 1:  # Reposição no primeiro dia do mês
                current_estoque = base_estoque + random.uniform(-100, 100)
            
            # Reduzir estoque pelo consumo
            current_estoque -= consumo
            
            # Garantir que estoque não fique muito negativo (reposição de emergência)
            if current_estoque < 0:
                current_estoque = random.uniform(100, 500)
            
            # Adicionar algumas anomalias ocasionais
            if random.random() < 0.02:  # 2% de chance de anomalia
                if random.random() < 0.5:
                    # Anomalia: consumo muito alto
                    consumo *= random.uniform(2, 4)
                else:
                    # Anomalia: estoque muito baixo ou muito alto
                    current_estoque *= random.choice([0.1, 3])
            
            data_list.append({
                "data": date.strftime("%Y-%m-%d"),
                "produto_id": f"PROD_{product_id:03d}",
                "estoque": round(max(0, current_estoque), 2),
                "consumo": round(consumo, 2)
            })
    
    # Criar DataFrame
    df = pd.DataFrame(data_list)
    
    # Salvar CSV
    df.to_csv(output_path, index=False, encoding="utf-8")
    
    print(f"Dataset gerado com sucesso!")
    print(f"Arquivo salvo em: {output_path}")
    print(f"Total de registros: {len(df)}")
    print(f"Período: {start_date} a {end_date}")
    print(f"Número de produtos: {n_products}")
    print(f"\nPrimeiras linhas:")
    print(df.head(10))
    
    return df


if __name__ == "__main__":
    # Gerar dataset padrão
    generate_fake_inventory_data()

