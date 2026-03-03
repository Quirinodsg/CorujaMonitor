"""
Parte 2: Entradas adicionais para Base de Conhecimento
Linux, Azure, AKS/Kubernetes
"""

# ===== WINDOWS SERVER - MEMÓRIA (3 entradas) =====
MEMORY_ENTRIES = [
    {
        "problem_signature": "memory_leak_process",
        "sensor_type": "memory",
        "severity": "critical",
        "problem_title": "Memory Leak em Processo",
        "problem_description": "Memória do servidor acima de 95% devido a processo com memory leak.",
        "symptoms": ["Memória constantemente alta", "Sistema lento", "Processo específico consumindo RAM"],
        "root_cause": "Aplicação com memory leak não liberando memória corretamente.",
        "root_cause_confidence": 0.80,
        "solution_description": "Identificar e reiniciar processo problemático",
        "solution_steps": ["Identificar processo (Task Manager)", "Verificar se é crítico", "Reiniciar se não-crítico", "Investigar causa raiz", "Aplicar patch"],
        "solution_commands": ["tasklist /v | sort /r /+65", "taskkill /IM <processo>.exe /F"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "high",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.70
    },
    {
        "problem_signature": "memory_high_cache",
        "sensor_type": "memory",
        "severity": "warning",
        "problem_title": "Memória Alta - Cache de Sistema",
        "problem_description": "Memória alta devido a cache de sistema (comportamento normal do Windows).",
        "symptoms": ["Memória >80%", "Standby memory alta", "Sistema responsivo"],
        "root_cause": "Windows usa RAM disponível para cache, liberando quando necessário (comportamento normal).",
        "root_cause_confidence": 0.95,
        "solution_description": "Verificar se é cache (normal) ou leak real",
        "solution_steps": ["Verificar Standby memory", "Usar RAMMap para análise", "Se cache, não requer ação", "Se leak, investigar processos"],
        "solution_commands": ["Get-Counter '\\Memory\\Available MBytes'", "Get-Counter '\\Memory\\Cache Bytes'"],
        "auto_resolution_enabled": False,
        "requires_approval": False,
        "risk_level": "low",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.92
    },
    {
        "problem_signature": "memory_pool_leak",
        "sensor_type": "memory",
        "severity": "critical",
        "problem_title": "Memory Pool Leak - Driver",
        "problem_description": "Memória não-paginada crescendo constantemente (pool leak de driver).",
        "symptoms": ["Non-Paged Pool crescendo", "Memória alta", "Sistema instável", "Possível BSOD"],
        "root_cause": "Driver de dispositivo com bug causando vazamento de memória do kernel.",
        "root_cause_confidence": 0.75,
        "solution_description": "Identificar driver problemático e atualizar",
        "solution_steps": ["Usar PoolMon para identificar tag", "Identificar driver pela tag", "Atualizar/remover driver", "Reiniciar servidor"],
        "solution_commands": ["poolmon.exe"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "high",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.65
    }
]

# ===== WINDOWS SERVER - CPU (3 entradas) =====
CPU_ENTRIES = [
    {
        "problem_signature": "cpu_high_antivirus",
        "sensor_type": "cpu",
        "severity": "warning",
        "problem_title": "CPU Alta - Antivírus em Scan",
        "problem_description": "CPU acima de 90% devido a scan de antivírus.",
        "symptoms": ["CPU alta", "MsMpEng.exe consumindo CPU", "Sistema lento"],
        "root_cause": "Windows Defender ou antivírus executando scan completo durante produção.",
        "root_cause_confidence": 0.92,
        "solution_description": "Reagendar scan para horário de baixo uso",
        "solution_steps": ["Verificar scan em execução", "Aguardar conclusão se possível", "Reagendar para noturno", "Configurar exclusões"],
        "solution_commands": ["Get-MpComputerStatus", "Set-MpPreference -ScanScheduleDay 0 -ScanScheduleTime 02:00:00"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "low",
        "affected_os": ["Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.88
    },
    {
        "problem_signature": "cpu_high_windows_update",
        "sensor_type": "cpu",
        "severity": "warning",
        "problem_title": "CPU Alta - Windows Update",
        "problem_description": "CPU elevada devido a Windows Update instalando patches.",
        "symptoms": ["CPU alta", "TiWorker.exe ou wuauclt.exe ativo", "Disco também alto"],
        "root_cause": "Windows Update instalando patches durante horário de produção.",
        "root_cause_confidence": 0.90,
        "solution_description": "Aguardar conclusão ou reagendar janela de manutenção",
        "solution_steps": ["Verificar status Windows Update", "Aguardar conclusão", "Configurar horário adequado", "Considerar WSUS"],
        "solution_commands": ["Get-WindowsUpdateLog", "wuauclt /detectnow"],
        "auto_resolution_enabled": False,
        "requires_approval": False,
        "risk_level": "low",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.95
    },
    {
        "problem_signature": "cpu_high_sql_query",
        "sensor_type": "cpu",
        "severity": "critical",
        "problem_title": "CPU Alta - Query SQL Pesada",
        "problem_description": "CPU alta devido a query SQL mal otimizada ou sem índice.",
        "symptoms": ["CPU >90%", "sqlservr.exe consumindo CPU", "Aplicações lentas", "Timeouts"],
        "root_cause": "Query SQL sem índice, full table scan, ou plano de execução ruim.",
        "root_cause_confidence": 0.85,
        "solution_description": "Identificar e otimizar query problemática",
        "solution_steps": ["Identificar query via DMV", "Analisar plano de execução", "Criar índices necessários", "Otimizar query", "Atualizar estatísticas"],
        "solution_commands": ["sp_who2", "sp_WhoIsActive"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "medium",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.78
    }
]

# ===== WINDOWS SERVER - REDE (2 entradas) =====
NETWORK_ENTRIES = [
    {
        "problem_signature": "ping_timeout_firewall",
        "sensor_type": "ping",
        "severity": "critical",
        "problem_title": "Servidor Não Responde - Firewall Bloqueando ICMP",
        "problem_description": "Servidor não responde a ping, mas está online. Firewall bloqueando ICMP.",
        "symptoms": ["Ping timeout", "Servidor acessível por RDP/SSH", "Outros serviços funcionando"],
        "root_cause": "Windows Firewall ou firewall de rede bloqueando pacotes ICMP.",
        "root_cause_confidence": 0.85,
        "solution_description": "Ajustar regras de firewall para permitir ICMP",
        "solution_steps": ["Verificar servidor online (RDP/SSH)", "Verificar regras firewall", "Habilitar ICMP Echo Request", "Testar ping"],
        "solution_commands": ["netsh advfirewall firewall add rule name=\"ICMP Allow\" protocol=icmpv4:8,any dir=in action=allow"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "low",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.90
    },
    {
        "problem_signature": "ping_timeout_network",
        "sensor_type": "ping",
        "severity": "critical",
        "problem_title": "Servidor Não Responde - Problema de Rede",
        "problem_description": "Servidor completamente inacessível via rede.",
        "symptoms": ["Ping timeout", "RDP não conecta", "Todos serviços inacessíveis"],
        "root_cause": "Problema de rede física, cabo desconectado, switch com problema, ou interface desabilitada.",
        "root_cause_confidence": 0.75,
        "solution_description": "Verificar conectividade física e configuração de rede",
        "solution_steps": ["Verificar cabo conectado", "Verificar luzes interface", "Acessar console físico/iLO", "Verificar config IP", "Reiniciar interface"],
        "solution_commands": ["ipconfig /all", "netsh interface show interface"],
        "auto_resolution_enabled": False,
        "requires_approval": True,
        "risk_level": "high",
        "affected_os": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Windows Server 2022"],
        "times_matched": 0,
        "times_successful": 0,
        "success_rate": 0.65
    }
]

# Total Windows: 18 entradas
