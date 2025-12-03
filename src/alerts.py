"""
Módulo para envio de alertas via webhook (Discord/Teams) e email.
Envia alertas automáticos quando anomalias são detectadas.
"""

import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd

from src.config import ALERT_CONFIG, EMAIL_CONFIG


def send_discord_alert(
    message: str,
    title: str = "Alerta de Anomalia",
    webhook_url: Optional[str] = None,
    color: int = 15158332  # Vermelho
) -> bool:
    """
    Envia alerta para Discord via webhook.
    
    Args:
        message: Mensagem do alerta.
        title: Título do alerta.
        webhook_url: URL do webhook do Discord. Se None, usa config.
        color: Cor do embed (decimal). 15158332 = vermelho, 3066993 = verde.
    
    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    if webhook_url is None:
        webhook_url = ALERT_CONFIG.get("discord_webhook_url")
    
    if webhook_url is None:
        print("Aviso: URL do webhook Discord não configurada.")
        print("Configure ALERT_CONFIG['discord_webhook_url'] em src/config.py")
        return False
    
    embed = {
        "title": title,
        "description": message,
        "color": color,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Alerta Discord enviado com sucesso!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar alerta Discord: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao enviar alerta Discord: {e}")
        return False


def send_teams_alert(
    message: str,
    title: str = "Alerta de Anomalia",
    webhook_url: Optional[str] = None
) -> bool:
    """
    Envia alerta para Microsoft Teams via webhook.
    
    Args:
        message: Mensagem do alerta.
        title: Título do alerta.
        webhook_url: URL do webhook do Teams. Se None, usa config.
    
    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    if webhook_url is None:
        webhook_url = ALERT_CONFIG.get("teams_webhook_url")
    
    if webhook_url is None:
        print("Aviso: URL do webhook Teams não configurada.")
        print("Configure ALERT_CONFIG['teams_webhook_url'] em src/config.py")
        return False
    
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": title,
        "themeColor": "FF0000",  # Vermelho
        "title": title,
        "text": message
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Alerta Teams enviado com sucesso!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar alerta Teams: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao enviar alerta Teams: {e}")
        return False


def format_anomaly_alert(
    df_anomalies: pd.DataFrame,
    produto_id: Optional[str] = None,
    max_anomalies: int = 10
) -> str:
    """
    Formata mensagem de alerta para anomalias detectadas.
    
    Args:
        df_anomalies: DataFrame com anomalias detectadas (deve ter is_anomaly=True).
        produto_id: ID do produto (opcional).
        max_anomalies: Número máximo de anomalias a listar.
    
    Returns:
        Mensagem formatada.
    """
    n_anomalies = len(df_anomalies)
    
    if n_anomalies == 0:
        return "Nenhuma anomalia detectada."
    
    # Cabeçalho
    message = "=" * 60 + "\n"
    message += f"ALERTA: {n_anomalies} ANOMALIA(S) DETECTADA(S)\n"
    message += "=" * 60 + "\n\n"
    
    if produto_id:
        message += f"Produto: {produto_id}\n"
    
    # Estatísticas gerais
    if "anomaly_score" in df_anomalies.columns:
        avg_score = df_anomalies["anomaly_score"].mean()
        max_score = df_anomalies["anomaly_score"].max()
        message += f"\nEstatísticas:\n"
        message += f"  - Score médio: {avg_score:.4f}\n"
        message += f"  - Score máximo: {max_score:.4f}\n"
    
    message += "\n" + "-" * 60 + "\n"
    message += "DETALHES DAS ANOMALIAS:\n"
    message += "-" * 60 + "\n\n"
    
    # Listar anomalias (ordenadas por score se disponível)
    anomalies_list = df_anomalies.copy()
    if "anomaly_score" in anomalies_list.columns:
        anomalies_list = anomalies_list.sort_values("anomaly_score", ascending=False)
    anomalies_list = anomalies_list.head(max_anomalies)
    
    for idx, (_, row) in enumerate(anomalies_list.iterrows(), 1):
        message += f"[{idx}] Anomalia Detectada\n"
        message += "-" * 40 + "\n"
        
        if "data" in row or "ds" in row:
            date_col = "data" if "data" in row else "ds"
            date_val = row[date_col]
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d')
            message += f"  Data: {date_val}\n"
        
        if "produto_id" in row:
            message += f"  Produto: {row['produto_id']}\n"
        
        # Consumo
        consumo_val = None
        if "consumo_mean" in row:
            consumo_val = row['consumo_mean']
        elif "consumo" in row:
            consumo_val = row['consumo']
        elif "y" in row:
            consumo_val = row['y']
        
        if consumo_val is not None:
            message += f"  Consumo: {consumo_val:.2f}\n"
        
        # Estoque
        estoque_val = None
        if "estoque_mean" in row:
            estoque_val = row['estoque_mean']
        elif "estoque" in row:
            estoque_val = row['estoque']
        
        if estoque_val is not None:
            message += f"  Estoque: {estoque_val:.2f}\n"
        
        # Score
        if "anomaly_score" in row:
            score = row['anomaly_score']
            severity = "CRÍTICA" if score > 0.7 else "ALTA" if score > 0.6 else "MÉDIA"
            message += f"  Score: {score:.4f} ({severity})\n"
        
        message += "\n"
    
    if n_anomalies > max_anomalies:
        message += f"... e mais {n_anomalies - max_anomalies} anomalia(s) não listada(s).\n"
    
    message += "=" * 60 + "\n"
    message += f"Total: {n_anomalies} anomalia(s) detectada(s)\n"
    message += "=" * 60
    
    return message


def send_anomaly_alerts(
    df_anomalies: pd.DataFrame,
    produto_id: Optional[str] = None,
    min_score: Optional[float] = None,
    send_discord: bool = True,
    send_teams: bool = False
) -> Dict[str, bool]:
    """
    Envia alertas para anomalias detectadas.
    
    Args:
        df_anomalies: DataFrame com anomalias detectadas (deve ter coluna 'is_anomaly').
        produto_id: ID do produto.
        min_score: Score mínimo para enviar alerta. Se None, usa config.
        send_discord: Se True, envia para Discord.
        send_teams: Se True, envia para Teams.
    
    Returns:
        Dicionário com status de envio {platform: success}.
    """
    # Filtrar apenas anomalias
    anomalies_filtered = df_anomalies[df_anomalies["is_anomaly"]].copy()
    
    if len(anomalies_filtered) == 0:
        print("Nenhuma anomalia detectada para enviar alerta.")
        return {"discord": False, "teams": False}
    
    # Filtrar por score mínimo se especificado
    if min_score is None:
        min_score = ALERT_CONFIG.get("min_anomaly_score", 0.7)
    
    if "anomaly_score" in anomalies_filtered.columns:
        anomalies_filtered = anomalies_filtered[
            anomalies_filtered["anomaly_score"] >= min_score
        ]
    
    if len(anomalies_filtered) == 0:
        print(f"Nenhuma anomalia acima do score mínimo ({min_score}) para alerta.")
        return {"discord": False, "teams": False}
    
    # Formatar mensagem
    message = format_anomaly_alert(anomalies_filtered, produto_id=produto_id)
    title = f"Alerta de Anomalia - {produto_id}" if produto_id else "Alerta de Anomalia"
    
    results = {}
    
    if send_discord:
        results["discord"] = send_discord_alert(message, title=title)
    
    if send_teams:
        results["teams"] = send_teams_alert(message, title=title)
    
    return results


def send_anomaly_alert_by_product(
    df_anomalies: pd.DataFrame,
    produto_column: str = "produto_id",
    min_score: Optional[float] = None,
    send_discord: bool = True,
    send_teams: bool = False
) -> Dict[str, Dict[str, bool]]:
    """
    Envia alertas separados para cada produto com anomalias.
    
    Args:
        df_anomalies: DataFrame com anomalias detectadas.
        produto_column: Nome da coluna de produto.
        min_score: Score mínimo para enviar alerta.
        send_discord: Se True, envia para Discord.
        send_teams: Se True, envia para Teams.
    
    Returns:
        Dicionário com status por produto {produto_id: {platform: success}}.
    """
    if produto_column not in df_anomalies.columns:
        print(f"Coluna '{produto_column}' não encontrada.")
        return {}
    
    produtos_com_anomalias = df_anomalies[
        df_anomalies["is_anomaly"]
    ][produto_column].unique()
    
    results = {}
    
    print(f"Enviando alertas para {len(produtos_com_anomalias)} produtos...")
    
    for produto_id in produtos_com_anomalias:
        df_produto = df_anomalies[df_anomalies[produto_column] == produto_id]
        results[produto_id] = send_anomaly_alerts(
            df_produto,
            produto_id=produto_id,
            min_score=min_score,
            send_discord=send_discord,
            send_teams=send_teams
        )
    
    return results


def send_email_alert(
    subject: str,
    message: str,
    to_emails: Optional[List[str]] = None,
    html_message: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_username: Optional[str] = None,
    smtp_password: Optional[str] = None,
    from_email: Optional[str] = None,
    use_tls: bool = True
) -> bool:
    """
    Envia alerta por email via SMTP.
    
    Args:
        subject: Assunto do email.
        message: Mensagem em texto plano.
        to_emails: Lista de emails destinatários. Se None, usa config.
        html_message: Mensagem em HTML (opcional).
        smtp_server: Servidor SMTP. Se None, usa config.
        smtp_port: Porta SMTP. Se None, usa config.
        smtp_username: Usuário SMTP. Se None, usa config.
        smtp_password: Senha SMTP. Se None, usa config.
        from_email: Email do remetente. Se None, usa config.
        use_tls: Se True, usa TLS.
    
    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    # Usar configurações padrão se não fornecidas
    if smtp_server is None:
        smtp_server = EMAIL_CONFIG.get("smtp_server")
    if smtp_port is None:
        smtp_port = EMAIL_CONFIG.get("smtp_port", 587)
    if smtp_username is None:
        smtp_username = EMAIL_CONFIG.get("smtp_username")
    if smtp_password is None:
        smtp_password = EMAIL_CONFIG.get("smtp_password")
    if from_email is None:
        from_email = EMAIL_CONFIG.get("from_email")
    if to_emails is None:
        to_emails = EMAIL_CONFIG.get("to_emails", [])
    
    # Validar configurações
    if not smtp_server or not smtp_username or not smtp_password or not from_email:
        print("Aviso: Configurações de email não completas.")
        print("Configure EMAIL_CONFIG em src/config.py")
        return False
    
    if not to_emails or len(to_emails) == 0:
        print("Aviso: Nenhum email destinatário configurado.")
        return False
    
    try:
        # Criar mensagem
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        
        # Adicionar texto plano
        text_part = MIMEText(message, "plain", "utf-8")
        msg.attach(text_part)
        
        # Adicionar HTML se fornecido
        if html_message:
            html_part = MIMEText(html_message, "html", "utf-8")
            msg.attach(html_part)
        
        # Conectar e enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email enviado com sucesso para {len(to_emails)} destinatário(s)!")
        return True
        
    except smtplib.SMTPException as e:
        print(f"Erro SMTP ao enviar email: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado ao enviar email: {e}")
        return False


def format_anomaly_email_html(
    df_anomalies: pd.DataFrame,
    produto_id: Optional[str] = None
) -> str:
    """
    Formata mensagem de alerta em HTML para email.
    
    Args:
        df_anomalies: DataFrame com anomalias detectadas.
        produto_id: ID do produto (opcional).
    
    Returns:
        Mensagem HTML formatada.
    """
    n_anomalies = len(df_anomalies)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ background-color: #ff4444; color: white; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .stats {{ background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ff4444; }}
            .stats h3 {{ margin-top: 0; color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; color: #333; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .score-critical {{ color: #ff0000; font-weight: bold; }}
            .score-high {{ color: #ff6600; font-weight: bold; }}
            .score-medium {{ color: #ffaa00; font-weight: bold; }}
            .footer {{ background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ALERTA: {n_anomalies} Anomalia(s) Detectada(s)</h1>
    """
    
    if produto_id:
        html += f"<p style='margin: 10px 0 0 0; font-size: 16px;'>Produto: {produto_id}</p>"
    
    # Estatísticas
    if "anomaly_score" in df_anomalies.columns:
        avg_score = df_anomalies["anomaly_score"].mean()
        max_score = df_anomalies["anomaly_score"].max()
        html += """
            </div>
            <div class="content">
                <div class="stats">
                    <h3>Estatísticas</h3>
                    <p><strong>Score médio:</strong> """ + f"{avg_score:.4f}" + """</p>
                    <p><strong>Score máximo:</strong> """ + f"{max_score:.4f}" + """</p>
                </div>
                <h3>Detalhes das Anomalias:</h3>
                <table>
                    <tr>
        """
    else:
        html += """
            </div>
            <div class="content">
                <h3>Detalhes das Anomalias:</h3>
                <table>
                    <tr>
        """
    
    # Cabeçalhos da tabela
    columns = []
    if "data" in df_anomalies.columns or "ds" in df_anomalies.columns:
        columns.append("Data")
    if "produto_id" in df_anomalies.columns:
        columns.append("Produto")
    if "consumo_mean" in df_anomalies.columns:
        columns.append("Consumo")
    elif "consumo" in df_anomalies.columns:
        columns.append("Consumo")
    elif "y" in df_anomalies.columns:
        columns.append("Consumo")
    if "estoque_mean" in df_anomalies.columns:
        columns.append("Estoque")
    elif "estoque" in df_anomalies.columns:
        columns.append("Estoque")
    if "anomaly_score" in df_anomalies.columns:
        columns.append("Score")
    
    for col in columns:
        html += f"<th>{col}</th>"
    
    html += """
                </tr>
    """
    
    # Ordenar por score se disponível
    anomalies_sorted = df_anomalies.copy()
    if "anomaly_score" in anomalies_sorted.columns:
        anomalies_sorted = anomalies_sorted.sort_values("anomaly_score", ascending=False)
    
    # Dados das anomalias
    for _, row in anomalies_sorted.head(20).iterrows():
        html += "<tr>"
        
        if "data" in row or "ds" in row:
            date_col = "data" if "data" in row else "ds"
            date_val = row[date_col]
            if hasattr(date_val, 'strftime'):
                date_val = date_val.strftime('%Y-%m-%d')
            html += f"<td>{date_val}</td>"
        
        if "produto_id" in row:
            html += f"<td>{row['produto_id']}</td>"
        
        if "consumo_mean" in row:
            html += f"<td>{row['consumo_mean']:.2f}</td>"
        elif "consumo" in row:
            html += f"<td>{row['consumo']:.2f}</td>"
        elif "y" in row:
            html += f"<td>{row['y']:.2f}</td>"
        
        if "estoque_mean" in row:
            html += f"<td>{row['estoque_mean']:.2f}</td>"
        elif "estoque" in row:
            html += f"<td>{row['estoque']:.2f}</td>"
        
        if "anomaly_score" in row:
            score = row['anomaly_score']
            if score > 0.7:
                score_class = "score-critical"
                severity = "CRÍTICA"
            elif score > 0.6:
                score_class = "score-high"
                severity = "ALTA"
            else:
                score_class = "score-medium"
                severity = "MÉDIA"
            html += f"<td class='{score_class}'>{score:.4f} ({severity})</td>"
        
        html += "</tr>"
    
    html += """
                    </table>
    """
    
    if n_anomalies > 20:
        html += f"<p style='margin-top: 15px; color: #666;'><em>... e mais {n_anomalies - 20} anomalia(s) não listada(s).</em></p>"
    
    html += f"""
                <p style='margin-top: 20px; padding: 10px; background-color: #fff; border-left: 4px solid #ff4444;'>
                    <strong>Total:</strong> {n_anomalies} anomalia(s) detectada(s)
                </p>
            </div>
            <div class="footer">
                <p>Inventory Anomaly Detector - Sistema Automatizado de Detecção de Anomalias</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_anomaly_email(
    df_anomalies: pd.DataFrame,
    produto_id: Optional[str] = None,
    min_score: Optional[float] = None,
    subject: Optional[str] = None
) -> bool:
    """
    Envia alerta de anomalias por email.
    
    Args:
        df_anomalies: DataFrame com anomalias detectadas (deve ter is_anomaly=True).
        produto_id: ID do produto.
        min_score: Score mínimo para enviar alerta.
        subject: Assunto do email. Se None, usa assunto padrão.
    
    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    # Filtrar apenas anomalias
    anomalies_filtered = df_anomalies[df_anomalies["is_anomaly"]].copy()
    
    if len(anomalies_filtered) == 0:
        print("Nenhuma anomalia detectada para enviar email.")
        return False
    
    # Filtrar por score mínimo
    if min_score is None:
        min_score = ALERT_CONFIG.get("min_anomaly_score", 0.7)
    
    if "anomaly_score" in anomalies_filtered.columns:
        anomalies_filtered = anomalies_filtered[
            anomalies_filtered["anomaly_score"] >= min_score
        ]
    
    if len(anomalies_filtered) == 0:
        print(f"Nenhuma anomalia acima do score mínimo ({min_score}) para email.")
        return False
    
    # Formatar mensagens
    text_message = format_anomaly_alert(anomalies_filtered, produto_id=produto_id)
    html_message = format_anomaly_email_html(anomalies_filtered, produto_id=produto_id)
    
    # Assunto
    if subject is None:
        subject = f"Alerta de Anomalia - {produto_id}" if produto_id else "Alerta de Anomalia"
        subject += f" ({len(anomalies_filtered)} anomalia(s))"
    
    # Enviar email
    return send_email_alert(
        subject=subject,
        message=text_message,
        html_message=html_message
    )

