// Sensor Templates Library - PRTG Style
// Biblioteca de templates de sensores padrão

export const sensorCategories = {
  standard: {
    name: 'Sensores Padrão',
    icon: '⭐',
    description: 'Sensores essenciais para monitoramento básico'
  },
  windows: {
    name: 'Windows',
    icon: '🪟',
    description: 'Sensores específicos para servidores Windows'
  },
  linux: {
    name: 'Linux',
    icon: '🐧',
    description: 'Sensores específicos para servidores Linux'
  },
  network: {
    name: 'Rede',
    icon: '🌐',
    description: 'Sensores de conectividade e tráfego de rede'
  },
  snmp: {
    name: 'SNMP',
    icon: '📡',
    description: 'Dispositivos SNMP (switches, roteadores, impressoras)'
  },
  storage: {
    name: 'Storage',
    icon: '💿',
    description: 'Sistemas de armazenamento (SAN, NAS, Dell EqualLogic)'
  },
  cloud: {
    name: 'Cloud',
    icon: '☁️',
    description: 'Serviços em nuvem (Azure, AWS, Google Cloud)'
  },
  azure: {
    name: 'Microsoft Azure',
    icon: '☁️',
    description: 'Recursos e serviços do Microsoft Azure'
  },
  database: {
    name: 'Banco de Dados',
    icon: '🗄️',
    description: 'Sensores para monitoramento de bancos de dados'
  },
  application: {
    name: 'Aplicações',
    icon: '📦',
    description: 'Sensores para aplicações e serviços específicos'
  },
  custom: {
    name: 'Personalizado',
    icon: '⚙️',
    description: 'Crie seus próprios sensores customizados'
  }
};

export const sensorTemplates = {
  // ===== SENSORES PADRÃO =====
  standard: [
    {
      id: 'ping',
      name: 'Ping',
      icon: '📡',
      description: 'Monitora conectividade e latência de rede',
      sensor_type: 'ping',
      default_name: 'Ping',
      requires_discovery: false,
      thresholds: {
        warning: 100,
        critical: 200,
        unit: 'ms'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'cpu',
      name: 'CPU',
      icon: '🖥️',
      description: 'Monitora uso do processador',
      sensor_type: 'cpu',
      default_name: 'CPU',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'memory',
      name: 'Memória',
      icon: '💾',
      description: 'Monitora uso de memória RAM',
      sensor_type: 'memory',
      default_name: 'Memória',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'disk',
      name: 'Disco',
      icon: '💿',
      description: 'Monitora uso de espaço em disco',
      sensor_type: 'disk',
      default_name: 'Disco C',
      requires_discovery: true,
      discovery_type: 'disks',
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'uptime',
      name: 'Uptime',
      icon: '⏱️',
      description: 'Monitora tempo de atividade do sistema',
      sensor_type: 'system',
      default_name: 'Uptime',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'days'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'network_in',
      name: 'Network IN',
      icon: '📥',
      description: 'Monitora tráfego de rede de entrada',
      sensor_type: 'network',
      default_name: 'Network IN',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: 'MB/s'
      },
      recommended: true,
      auto_created: true
    },
    {
      id: 'network_out',
      name: 'Network OUT',
      icon: '📤',
      description: 'Monitora tráfego de rede de saída',
      sensor_type: 'network',
      default_name: 'Network OUT',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: 'MB/s'
      },
      recommended: true,
      auto_created: true
    }
  ],

  // ===== SENSORES WINDOWS =====
  windows: [
    {
      id: 'windows_service',
      name: 'Serviço Windows',
      icon: '⚙️',
      description: 'Monitora status de serviços Windows',
      sensor_type: 'service',
      default_name: 'service_',
      requires_discovery: true,
      discovery_type: 'services',
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      },
      recommended: true
    },
    {
      id: 'windows_event_log',
      name: 'Event Log',
      icon: '📋',
      description: 'Monitora logs de eventos do Windows',
      sensor_type: 'eventlog',
      default_name: 'Event Log',
      requires_discovery: false,
      thresholds: {
        warning: 10,
        critical: 50,
        unit: 'errors'
      }
    },
    {
      id: 'windows_process',
      name: 'Processo Windows',
      icon: '⚡',
      description: 'Monitora processos específicos',
      sensor_type: 'process',
      default_name: 'process_',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'iis',
      name: 'IIS Web Server',
      icon: '🌐',
      description: 'Monitora servidor IIS',
      sensor_type: 'service',
      default_name: 'service_W3SVC',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'windows_updates',
      name: 'Windows Updates',
      icon: '🔄',
      description: 'Monitora atualizações pendentes do Windows',
      sensor_type: 'windows_updates',
      default_name: 'Windows Updates',
      requires_discovery: false,
      thresholds: {
        warning: 10,
        critical: 50,
        unit: 'updates'
      }
    },
    {
      id: 'active_directory',
      name: 'Active Directory',
      icon: '🔐',
      description: 'Monitora saúde do Active Directory',
      sensor_type: 'service',
      default_name: 'service_NTDS',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'dns_server',
      name: 'DNS Server',
      icon: '🌐',
      description: 'Monitora serviço DNS do Windows',
      sensor_type: 'service',
      default_name: 'service_DNS',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'dhcp_server',
      name: 'DHCP Server',
      icon: '📡',
      description: 'Monitora serviço DHCP do Windows',
      sensor_type: 'service',
      default_name: 'service_DHCPServer',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'print_spooler',
      name: 'Print Spooler',
      icon: '🖨️',
      description: 'Monitora serviço de impressão',
      sensor_type: 'service',
      default_name: 'service_Spooler',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'windows_firewall',
      name: 'Windows Firewall',
      icon: '🛡️',
      description: 'Monitora firewall do Windows',
      sensor_type: 'service',
      default_name: 'service_MpsSvc',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'windows_defender',
      name: 'Windows Defender',
      icon: '🛡️',
      description: 'Monitora antivírus Windows Defender',
      sensor_type: 'service',
      default_name: 'service_WinDefend',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'remote_desktop',
      name: 'Remote Desktop',
      icon: '🖥️',
      description: 'Monitora serviço de área de trabalho remota',
      sensor_type: 'service',
      default_name: 'service_TermService',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'task_scheduler',
      name: 'Task Scheduler',
      icon: '⏰',
      description: 'Monitora agendador de tarefas',
      sensor_type: 'service',
      default_name: 'service_Schedule',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'windows_time',
      name: 'Windows Time',
      icon: '🕐',
      description: 'Monitora sincronização de horário',
      sensor_type: 'service',
      default_name: 'service_W32Time',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    }
  ],

  // ===== SENSORES LINUX =====
  linux: [
    {
      id: 'linux_service',
      name: 'Serviço Linux (systemd)',
      icon: '⚙️',
      description: 'Monitora serviços systemd',
      sensor_type: 'service',
      default_name: 'service_',
      requires_discovery: true,
      discovery_type: 'services',
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'linux_load',
      name: 'Load Average',
      icon: '📊',
      description: 'Monitora carga do sistema',
      sensor_type: 'load',
      default_name: 'Load Average',
      requires_discovery: false,
      thresholds: {
        warning: 2,
        critical: 4,
        unit: 'load'
      }
    },
    {
      id: 'apache',
      name: 'Apache Web Server',
      icon: '🌐',
      description: 'Monitora servidor Apache',
      sensor_type: 'service',
      default_name: 'service_apache2',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'nginx',
      name: 'Nginx Web Server',
      icon: '🌐',
      description: 'Monitora servidor Nginx',
      sensor_type: 'service',
      default_name: 'service_nginx',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'ssh',
      name: 'SSH Server',
      icon: '🔐',
      description: 'Monitora serviço SSH',
      sensor_type: 'service',
      default_name: 'service_sshd',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'cron',
      name: 'Cron Daemon',
      icon: '⏰',
      description: 'Monitora agendador de tarefas',
      sensor_type: 'service',
      default_name: 'service_cron',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'docker_service',
      name: 'Docker Service',
      icon: '🐳',
      description: 'Monitora serviço Docker',
      sensor_type: 'service',
      default_name: 'service_docker',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'nfs',
      name: 'NFS Server',
      icon: '📁',
      description: 'Monitora servidor NFS',
      sensor_type: 'service',
      default_name: 'service_nfs-server',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'samba',
      name: 'Samba Server',
      icon: '📁',
      description: 'Monitora servidor Samba',
      sensor_type: 'service',
      default_name: 'service_smbd',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    }
  ],

  // ===== SENSORES DE REDE =====
  network: [
    {
      id: 'http',
      name: 'HTTP/HTTPS',
      icon: '🌐',
      description: 'Monitora disponibilidade de sites',
      sensor_type: 'http',
      default_name: 'HTTP',
      requires_discovery: false,
      thresholds: {
        warning: 2000,
        critical: 5000,
        unit: 'ms'
      },
      recommended: true
    },
    {
      id: 'port',
      name: 'Porta TCP',
      icon: '🔌',
      description: 'Monitora disponibilidade de portas TCP',
      sensor_type: 'port',
      default_name: 'Port',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'snmp_traffic',
      name: 'SNMP Traffic',
      icon: '📊',
      description: 'Monitora tráfego via SNMP',
      sensor_type: 'snmp',
      default_name: 'SNMP Traffic',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'ssl_certificate',
      name: 'Certificado SSL',
      icon: '🔒',
      description: 'Monitora validade de certificados SSL',
      sensor_type: 'ssl',
      default_name: 'SSL Certificate',
      requires_discovery: false,
      thresholds: {
        warning: 30,
        critical: 7,
        unit: 'days'
      }
    },
    {
      id: 'dns_query',
      name: 'DNS Query',
      icon: '🌐',
      description: 'Monitora resolução DNS',
      sensor_type: 'dns',
      default_name: 'DNS Query',
      requires_discovery: false,
      thresholds: {
        warning: 500,
        critical: 2000,
        unit: 'ms'
      }
    },
    {
      id: 'smtp',
      name: 'SMTP Server',
      icon: '📧',
      description: 'Monitora servidor de email SMTP',
      sensor_type: 'port',
      default_name: 'SMTP Port 25',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'pop3',
      name: 'POP3 Server',
      icon: '📧',
      description: 'Monitora servidor POP3',
      sensor_type: 'port',
      default_name: 'POP3 Port 110',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'imap',
      name: 'IMAP Server',
      icon: '📧',
      description: 'Monitora servidor IMAP',
      sensor_type: 'port',
      default_name: 'IMAP Port 143',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'ftp',
      name: 'FTP Server',
      icon: '📁',
      description: 'Monitora servidor FTP',
      sensor_type: 'port',
      default_name: 'FTP Port 21',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'rdp',
      name: 'RDP (Remote Desktop)',
      icon: '🖥️',
      description: 'Monitora porta RDP',
      sensor_type: 'port',
      default_name: 'RDP Port 3389',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    },
    {
      id: 'vpn',
      name: 'VPN Server',
      icon: '🔐',
      description: 'Monitora servidor VPN',
      sensor_type: 'port',
      default_name: 'VPN',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 3000,
        unit: 'ms'
      }
    }
  ],

  // ===== SENSORES SNMP =====
  snmp: [
    {
      id: 'snmp_device',
      name: 'Dispositivo SNMP',
      icon: '📡',
      description: 'Monitora dispositivo via SNMP (v1/v2c/v3)',
      sensor_type: 'snmp',
      default_name: 'SNMP Device',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      recommended: true
    },
    {
      id: 'snmp_access_point',
      name: 'Access Point (AP)',
      icon: '📶',
      description: 'Monitora Access Point WiFi via SNMP (clientes, sinal, uptime)',
      sensor_type: 'snmp_ap',
      default_name: 'Access Point',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      recommended: true
    },
    {
      id: 'snmp_air_conditioning',
      name: 'Ar-Condicionado',
      icon: '❄️',
      description: 'Monitora ar-condicionado via SNMP (temperatura, status, alarmes)',
      sensor_type: 'snmp_ac',
      default_name: 'Ar-Condicionado',
      requires_discovery: false,
      thresholds: {
        warning: 28,
        critical: 32,
        unit: '°C'
      },
      recommended: true
    },
    {
      id: 'snmp_ups',
      name: 'Nobreak (UPS)',
      icon: '🔋',
      description: 'Monitora nobreak via SNMP (bateria, carga, tempo restante)',
      sensor_type: 'snmp_ups',
      default_name: 'Nobreak',
      requires_discovery: false,
      thresholds: {
        warning: 30,
        critical: 15,
        unit: '%'
      },
      recommended: true
    },
    {
      id: 'snmp_printer',
      name: 'Impressora SNMP',
      icon: '🖨️',
      description: 'Monitora impressora via SNMP (toner, páginas, status)',
      sensor_type: 'snmp_printer',
      default_name: 'Impressora',
      requires_discovery: false,
      thresholds: {
        warning: 20,
        critical: 10,
        unit: '%'
      },
      recommended: true
    },
    {
      id: 'snmp_switch',
      name: 'Switch SNMP',
      icon: '🔀',
      description: 'Monitora switch de rede via SNMP (portas, tráfego, uptime)',
      sensor_type: 'snmp_switch',
      default_name: 'Switch',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'snmp_router',
      name: 'Roteador SNMP',
      icon: '🌐',
      description: 'Monitora roteador via SNMP (CPU, memória, interfaces)',
      sensor_type: 'snmp_router',
      default_name: 'Roteador',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'snmp_custom_oid',
      name: 'OID Customizado',
      icon: '⚙️',
      description: 'Monitora OID SNMP específico',
      sensor_type: 'snmp_custom',
      default_name: 'Custom OID',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: 'value'
      }
    }
  ],

  // ===== SENSORES DE BANCO DE DADOS =====
  database: [
    {
      id: 'sql_server',
      name: 'SQL Server',
      icon: '🗄️',
      description: 'Monitora Microsoft SQL Server',
      sensor_type: 'service',
      default_name: 'service_MSSQLSERVER',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'mysql',
      name: 'MySQL',
      icon: '🐬',
      description: 'Monitora MySQL Server',
      sensor_type: 'service',
      default_name: 'service_MySQL',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'postgresql',
      name: 'PostgreSQL',
      icon: '🐘',
      description: 'Monitora PostgreSQL Server',
      sensor_type: 'service',
      default_name: 'service_postgresql',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'mongodb',
      name: 'MongoDB',
      icon: '🍃',
      description: 'Monitora MongoDB Server',
      sensor_type: 'service',
      default_name: 'service_mongod',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'oracle',
      name: 'Oracle Database',
      icon: '🔴',
      description: 'Monitora Oracle Database',
      sensor_type: 'service',
      default_name: 'service_OracleService',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'mariadb',
      name: 'MariaDB',
      icon: '🐬',
      description: 'Monitora MariaDB Server',
      sensor_type: 'service',
      default_name: 'service_mariadb',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'cassandra',
      name: 'Cassandra',
      icon: '💎',
      description: 'Monitora Apache Cassandra',
      sensor_type: 'service',
      default_name: 'service_cassandra',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'elasticsearch',
      name: 'Elasticsearch',
      icon: '🔍',
      description: 'Monitora Elasticsearch',
      sensor_type: 'service',
      default_name: 'service_elasticsearch',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    }
  ],

  // ===== SENSORES DE APLICAÇÃO =====
  application: [
    {
      id: 'docker',
      name: 'Docker Container',
      icon: '🐳',
      description: 'Monitora containers Docker',
      sensor_type: 'docker',
      default_name: 'Docker',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'redis',
      name: 'Redis',
      icon: '🔴',
      description: 'Monitora Redis Server',
      sensor_type: 'service',
      default_name: 'service_redis',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'rabbitmq',
      name: 'RabbitMQ',
      icon: '🐰',
      description: 'Monitora RabbitMQ Server',
      sensor_type: 'service',
      default_name: 'service_rabbitmq',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'kafka',
      name: 'Apache Kafka',
      icon: '📨',
      description: 'Monitora Apache Kafka',
      sensor_type: 'service',
      default_name: 'service_kafka',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'tomcat',
      name: 'Apache Tomcat',
      icon: '🐱',
      description: 'Monitora Apache Tomcat',
      sensor_type: 'service',
      default_name: 'service_tomcat',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'jenkins',
      name: 'Jenkins',
      icon: '🔧',
      description: 'Monitora Jenkins CI/CD',
      sensor_type: 'service',
      default_name: 'service_jenkins',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'gitlab',
      name: 'GitLab',
      icon: '🦊',
      description: 'Monitora GitLab Server',
      sensor_type: 'service',
      default_name: 'service_gitlab',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'kubernetes',
      name: 'Kubernetes',
      icon: '☸️',
      description: 'Monitora cluster Kubernetes',
      sensor_type: 'kubernetes',
      default_name: 'Kubernetes',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'memcached',
      name: 'Memcached',
      icon: '💾',
      description: 'Monitora Memcached Server',
      sensor_type: 'service',
      default_name: 'service_memcached',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    },
    {
      id: 'varnish',
      name: 'Varnish Cache',
      icon: '⚡',
      description: 'Monitora Varnish Cache',
      sensor_type: 'service',
      default_name: 'service_varnish',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      }
    }
  ],

  // ===== STORAGE =====
  storage: [
    {
      id: 'dell_equallogic',
      name: 'Dell EqualLogic',
      icon: '💿',
      description: 'Monitora Dell EqualLogic SAN via SNMP',
      sensor_type: 'snmp',
      default_name: 'Dell EqualLogic',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      snmp_oids: {
        volume_usage: '1.3.6.1.4.1.12740.5.1.7.1.1.8',
        volume_name: '1.3.6.1.4.1.12740.5.1.7.1.1.9',
        pool_usage: '1.3.6.1.4.1.12740.5.1.7.7.1.8',
        raid_status: '1.3.6.1.4.1.12740.2.1.1.1.9'
      }
    },
    {
      id: 'netapp',
      name: 'NetApp Filer',
      icon: '💿',
      description: 'Monitora NetApp Storage via SNMP',
      sensor_type: 'snmp',
      default_name: 'NetApp',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'emc_vnx',
      name: 'EMC VNX',
      icon: '💿',
      description: 'Monitora EMC VNX Storage',
      sensor_type: 'snmp',
      default_name: 'EMC VNX',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'hp_3par',
      name: 'HP 3PAR',
      icon: '💿',
      description: 'Monitora HP 3PAR Storage',
      sensor_type: 'snmp',
      default_name: 'HP 3PAR',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'synology_nas',
      name: 'Synology NAS',
      icon: '💿',
      description: 'Monitora Synology NAS via SNMP',
      sensor_type: 'snmp',
      default_name: 'Synology NAS',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'qnap_nas',
      name: 'QNAP NAS',
      icon: '💿',
      description: 'Monitora QNAP NAS via SNMP',
      sensor_type: 'snmp',
      default_name: 'QNAP NAS',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    }
  ],

  // ===== CLOUD =====
  cloud: [
    {
      id: 'aws_ec2',
      name: 'AWS EC2 Instance',
      icon: '☁️',
      description: 'Monitora instância EC2 da AWS',
      sensor_type: 'cloud',
      default_name: 'AWS EC2',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'aws_rds',
      name: 'AWS RDS Database',
      icon: '☁️',
      description: 'Monitora banco de dados RDS da AWS',
      sensor_type: 'cloud',
      default_name: 'AWS RDS',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    },
    {
      id: 'gcp_compute',
      name: 'Google Compute Engine',
      icon: '☁️',
      description: 'Monitora VM do Google Cloud',
      sensor_type: 'cloud',
      default_name: 'GCP Compute',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      }
    }
  ],

  // ===== MICROSOFT AZURE =====
  azure: [
    {
      id: 'azure_vm',
      name: 'Azure Virtual Machine',
      icon: '☁️',
      description: 'Monitora máquina virtual do Azure',
      sensor_type: 'azure',
      default_name: 'Azure VM',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['CPU', 'Memory', 'Disk', 'Network']
    },
    {
      id: 'azure_webapp',
      name: 'Azure Web App',
      icon: '🌐',
      description: 'Monitora Azure Web App (App Service)',
      sensor_type: 'azure',
      default_name: 'Azure Web App',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['CPU', 'Memory', 'HTTP Requests', 'Response Time']
    },
    {
      id: 'azure_sql',
      name: 'Azure SQL Database',
      icon: '🗄️',
      description: 'Monitora Azure SQL Database',
      sensor_type: 'azure',
      default_name: 'Azure SQL',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['DTU', 'Storage', 'Connections', 'Deadlocks']
    },
    {
      id: 'azure_storage',
      name: 'Azure Storage Account',
      icon: '💾',
      description: 'Monitora Azure Storage Account',
      sensor_type: 'azure',
      default_name: 'Azure Storage',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['Capacity', 'Transactions', 'Availability', 'Latency']
    },
    {
      id: 'azure_aks',
      name: 'Azure Kubernetes Service (AKS)',
      icon: '☸️',
      description: 'Monitora cluster AKS do Azure',
      sensor_type: 'azure',
      default_name: 'Azure AKS',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['Node CPU', 'Node Memory', 'Pod Count', 'Node Status']
    },
    {
      id: 'azure_function',
      name: 'Azure Functions',
      icon: '⚡',
      description: 'Monitora Azure Functions',
      sensor_type: 'azure',
      default_name: 'Azure Function',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 5000,
        unit: 'ms'
      },
      metrics: ['Executions', 'Duration', 'Errors', 'Success Rate']
    },
    {
      id: 'azure_backup',
      name: 'Azure Backup',
      icon: '💾',
      description: 'Monitora Azure Backup Vault',
      sensor_type: 'azure',
      default_name: 'Azure Backup',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      },
      metrics: ['Backup Status', 'Last Backup', 'Backup Size', 'Failed Jobs']
    },
    {
      id: 'azure_loadbalancer',
      name: 'Azure Load Balancer',
      icon: '⚖️',
      description: 'Monitora Azure Load Balancer',
      sensor_type: 'azure',
      default_name: 'Azure LB',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['Health Probe Status', 'Data Path Availability', 'Throughput']
    },
    {
      id: 'azure_appgateway',
      name: 'Azure Application Gateway',
      icon: '🚪',
      description: 'Monitora Azure Application Gateway',
      sensor_type: 'azure',
      default_name: 'Azure App Gateway',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['Throughput', 'Response Time', 'Failed Requests', 'Healthy Hosts']
    },
    {
      id: 'azure_cosmosdb',
      name: 'Azure Cosmos DB',
      icon: '🌍',
      description: 'Monitora Azure Cosmos DB',
      sensor_type: 'azure',
      default_name: 'Azure Cosmos DB',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['RU Consumption', 'Storage', 'Availability', 'Latency']
    },
    {
      id: 'azure_redis',
      name: 'Azure Cache for Redis',
      icon: '🔴',
      description: 'Monitora Azure Cache for Redis',
      sensor_type: 'azure',
      default_name: 'Azure Redis',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['CPU', 'Memory', 'Connected Clients', 'Cache Hits']
    },
    {
      id: 'azure_servicebus',
      name: 'Azure Service Bus',
      icon: '🚌',
      description: 'Monitora Azure Service Bus',
      sensor_type: 'azure',
      default_name: 'Azure Service Bus',
      requires_discovery: false,
      thresholds: {
        warning: 1000,
        critical: 5000,
        unit: 'messages'
      },
      metrics: ['Active Messages', 'Dead Letter Messages', 'Throttled Requests']
    },
    {
      id: 'azure_eventhub',
      name: 'Azure Event Hub',
      icon: '📡',
      description: 'Monitora Azure Event Hub',
      sensor_type: 'azure',
      default_name: 'Azure Event Hub',
      requires_discovery: false,
      thresholds: {
        warning: 80,
        critical: 95,
        unit: '%'
      },
      metrics: ['Incoming Messages', 'Outgoing Messages', 'Throttled Requests', 'Capture Backlog']
    },
    {
      id: 'azure_keyvault',
      name: 'Azure Key Vault',
      icon: '🔐',
      description: 'Monitora Azure Key Vault',
      sensor_type: 'azure',
      default_name: 'Azure Key Vault',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'status'
      },
      metrics: ['API Hits', 'API Latency', 'Availability', 'Saturation']
    },
    {
      id: 'azure_monitor',
      name: 'Azure Monitor Alerts',
      icon: '🔔',
      description: 'Monitora alertas do Azure Monitor',
      sensor_type: 'azure',
      default_name: 'Azure Monitor',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'alerts'
      },
      metrics: ['Active Alerts', 'Fired Alerts', 'Resolved Alerts']
    }
  ],

  // ===== SENSORES PERSONALIZADOS =====
  custom: [
    {
      id: 'custom_script',
      name: 'Script Personalizado',
      icon: '📜',
      description: 'Execute scripts customizados',
      sensor_type: 'custom',
      default_name: 'Custom Script',
      requires_discovery: false,
      thresholds: {
        warning: 0,
        critical: 0,
        unit: 'value'
      }
    }
  ]
};

// Helper function to get all templates
export const getAllTemplates = () => {
  const all = [];
  Object.keys(sensorTemplates).forEach(category => {
    sensorTemplates[category].forEach(template => {
      all.push({ ...template, category });
    });
  });
  return all;
};

// Helper function to get templates by category
export const getTemplatesByCategory = (category) => {
  return sensorTemplates[category] || [];
};

// Helper function to get recommended templates
export const getRecommendedTemplates = () => {
  return getAllTemplates().filter(t => t.recommended);
};

// Helper function to get auto-created templates
export const getAutoCreatedTemplates = () => {
  return getAllTemplates().filter(t => t.auto_created);
};
