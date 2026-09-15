import os
import sys
import time

# Carrega a biblioteca de conexao real com a IQ Option
from iqoptionapi.stable_api import IQ_Option

print("🔄 Iniciando conexao com os servidores centrais da IQ Option via nuvem...")

# 🚨 COLOQUE SEU EMAIL E SENHA REAIS DA IQ OPTION AQUI:
EMAIL = "chovolate61@gmail.com"
SENHA = "@Binho1010"

API = IQ_Option(EMAIL, SENHA)
API.connect()

if API.check_connect():
    print("✅ CONECTADO COM SUCESSO À PLATAFORMA VIA NUVEM!")
else:
    print("❌ Falha no login. Verifique suas credenciais no codigo.")
    exit()

# 🚨 DEFINA O MODO: "PRACTICE" (Conta Demo para Teste) ou "REAL" (Conta Real)
API.change_balance("PRACTICE") 

ATIVO = "EURUSD"
TIMEFRAME = 1
VALOR_ENTRADA_BASE = 2.0
STOP_LOSS = 15.0
STOP_GAIN = 25.0
PAYOUT_MINIMO = 80

lucro_acumulado = 0
valor_atual_entrada = VALOR_ENTRADA_BASE
martingale_atual = 0
limite_martingales = 2

def calcular_rsi_real(ativo, timeframe, periodo=14):
    try:
        velas = API.get_candles(ativo, timeframe * 60, periodo + 1, time.time())
        ganhos = 0
        perdas = 0
        for i in range(1, len(velas)):
            mudanca = velas[i]['close'] - velas[i-1]['close']
            if mudanca > 0:
                ganhos += mudanca
            else:
                perdas += abs(mudanca)
        if perdas == 0:
            return 100
        rs = ganhos / perdas
        return 100 - (100 / (1 + rs))
    except:
        return 50

# Loop continuo na nuvem (Roda sem parar mesmo com seu celular desligado)
while True:
    try:
        if lucro_acumulado <= -STOP_LOSS or lucro_acumulado >= STOP_GAIN:
            print("🛑 Meta de gerenciamento atingida. Desligando robo.")
            break

        payout = API.get_digital_payout(ATIVO)
        if payout < PAYOUT_MINIMO:
            print(f"⏳ Payout baixo ({payout}%). Aguardando mercado melhorar...")
            time.sleep(30)
            continue

        rsi_atual = calcular_rsi_real(ATIVO, TIMEFRAME)
        print(f"📊 [NUVEM] RSI Real Atual: {rsi_atual:.2f} | Payout: {payout}%")

        # Estrategia de VENDA (Sobrecomprado)
        if rsi_atual >= 70:
            print("🚨 Alvo alcancado: Enviando ordem real de VENDA (Put)...")
            status, id_ordem = API.buy_digital_spot(ATIVO, valor_atual_entrada, "put", TIMEFRAME)
            if status:
                resultado, lucro = API.check_win_digital_v2(id_ordem)
                lucro_acumulado += lucro
                if lucro > 0:
                    print(f"✅ WIN! Lucro: +${lucro:.2f} | Total: ${lucro_acumulado:.2f}")
                    valor_atual_entrada = VALOR_ENTRADA_BASE
                    martingale_atual = 0
                else:
                    print(f"❌ LOSS! Perda: -${abs(lucro):.2f} | Total: ${lucro_acumulado:.2f}")
                    if martingale_atual < limite_martingales:
                        martingale_atual += 1
                        valor_atual_entrada *= 2.2
                        print(f"🔄 Acionando Gale {martingale_atual}. Nova entrada: ${valor_atual_entrada:.2f}")

        # Estrategia de COMPRA (Sobrevendido)
        elif rsi_atual <= 30:
            print("🚨 Alvo alcancado: Enviando ordem real de COMPRA (Call)...")
            status, id_ordem = API.buy_digital_spot(ATIVO, valor_atual_entrada, "call", TIMEFRAME)
            if status:
                resultado, lucro = API.check_win_digital_v2(id_ordem)
                lucro_acumulado += lucro
                if lucro > 0:
                    print(f"✅ WIN! Lucro: +${lucro:.2f} | Total: ${lucro_acumulado:.2f}")
                    valor_atual_entrada = VALOR_ENTRADA_BASE
                    martingale_atual = 0
                else:
                    print(f"❌ LOSS! Perda: -${abs(lucro):.2f} | Total: ${lucro_acumulado:.2f}")
                    if martingale_atual < limite_martingales:
                        martingale_atual += 1
                        valor_atual_entrada *= 2.2
                        print(f"🔄 Acionando Gale {martingale_atual}. Nova entrada: ${valor_atual_entrada:.2f}")

        time.sleep(10)
    except Exception as e:
        time.sleep(5)
