#!/usr/bin/env python3
"""
Script para criar uma falha de teste e verificar se notificações são enviadas
"""
import sys
from datetime import datetime
from database import SessionLocal
from models import Sensor, Metric

def criar_falha_teste():
    """Cria uma métrica com valor acima do threshold para simular falha"""
    db = SessionLocal()
    
    try:
        # Buscar primeiro sensor ativo
        sensor = db.query(Sensor).filter(
            Sensor.is_active == True,
            Sensor.sensor_type.in_(['cpu', 'memory', 'disk', 'ping'])
        ).first()
        
        if not sensor:
            print("❌ Nenhum sensor ativo encontrado")
            return False
        
        print(f"✅ Sensor encontrado: {sensor.name} (ID: {sensor.id})")
        print(f"   Tipo: {sensor.sensor_type}")
        print(f"   Threshold crítico: {sensor.threshold_critical}")
        print(f"   Threshold aviso: {sensor.threshold_warning}")
        print()
        
        # Criar métrica com valor acima do threshold crítico
        if sensor.sensor_type == 'ping':
            # Para ping, 0 = offline
            valor_falha = 0
            print(f"🔴 Simulando OFFLINE (ping = 0)")
        else:
            # Para CPU/Memory/Disk, usar valor acima do crítico
            valor_falha = sensor.threshold_critical + 10
            print(f"🔴 Simulando falha com valor: {valor_falha}%")
        
        # Criar métrica
        metric = Metric(
            sensor_id=sensor.id,
            value=valor_falha,
            unit='%' if sensor.sensor_type != 'ping' else 'ms',
            timestamp=datetime.utcnow()
        )
        
        db.add(metric)
        db.commit()
        
        print(f"✅ Métrica de falha criada com sucesso!")
        print()
        print("📢 PRÓXIMOS PASSOS:")
        print("1. Aguarde até 60 segundos (worker roda a cada minuto)")
        print("2. O worker vai detectar a falha")
        print("3. Criar incidente automaticamente")
        print("4. Enviar notificações para TOPdesk, Teams, Email")
        print()
        print("🔍 Para monitorar:")
        print("   docker logs coruja-worker -f")
        print()
        print("⏰ Aguardando worker processar...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE NOTIFICAÇÕES AUTOMÁTICAS")
    print("=" * 60)
    print()
    
    if criar_falha_teste():
        print()
        print("✅ Falha de teste criada com sucesso!")
        print("   Aguarde até 60 segundos e verifique:")
        print("   - TOPdesk: https://grupotechbiz.topdesk.net")
        print("   - Teams: Canal configurado")
        print("   - Email: Caixa de entrada")
    else:
        print()
        print("❌ Falha ao criar teste")
        sys.exit(1)
