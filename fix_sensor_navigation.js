// Patch para corrigir navegação de sensor
// Adicionar console.logs no useEffect

const patchCode = `
  useEffect(() => {
    // Se também foi passado um sensor específico, destacá-lo após os sensores serem carregados
    if (selectedSensorId && sensors.length > 0) {
      console.log('🎯 DEBUG: Navegando para sensor ID:', selectedSensorId);
      console.log('📊 DEBUG: Total de sensores carregados:', sensors.length);
      console.log('📋 DEBUG: IDs dos sensores:', sensors.map(s => s.id));
      
      // Encontrar o sensor e expandir seu grupo
      const sensor = sensors.find(s => s.id === selectedSensorId);
      if (sensor) {
        console.log('✅ DEBUG: Sensor encontrado:', sensor.name, 'Tipo:', sensor.sensor_type);
        
        // Determinar qual grupo o sensor pertence
        let groupKey = null;
        const type = sensor.sensor_type;
        
        if (['ping', 'cpu', 'memory', 'disk', 'system', 'network'].includes(type)) {
          groupKey = 'system';
        } else if (type === 'docker') {
          groupKey = 'docker';
        } else if (type === 'service') {
          groupKey = 'services';
        } else if (['hyperv', 'kubernetes'].includes(type)) {
          groupKey = 'applications';
        } else if (['http', 'port', 'dns', 'ssl', 'snmp'].includes(type)) {
          groupKey = 'network';
        }
        
        // Expandir o grupo do sensor
        if (groupKey) {
          console.log('📂 DEBUG: Expandindo grupo:', groupKey);
          setExpandedSensorGroups(prev => ({
            ...prev,
            [groupKey]: true
          }));
        }
      } else {
        console.log('❌ DEBUG: Sensor NÃO encontrado na lista!');
        console.log('🔍 DEBUG: Procurando por ID:', selectedSensorId, 'Tipo:', typeof selectedSensorId);
      }
      
      setHighlightedSensorId(selectedSensorId);
      
      // Rolar até o sensor após um delay maior para garantir que o grupo foi expandido
      setTimeout(() => {
        const sensorElement = document.getElementById(\`sensor-\${selectedSensorId}\`);
        if (sensorElement) {
          console.log('📜 DEBUG: Rolando até o sensor');
          sensorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          // Remover destaque após 3 segundos
          setTimeout(() => {
            setHighlightedSensorId(null);
          }, 3000);
        } else {
          console.log('❌ DEBUG: Elemento DOM não encontrado para sensor-' + selectedSensorId);
        }
      }, 800);
    } else {
      if (selectedSensorId) {
        console.log('⏳ DEBUG: Aguardando sensores... selectedSensorId:', selectedSensorId, 'sensors.length:', sensors.length);
      }
    }
  }, [selectedSensorId, sensors]);
`;

console.log('Código do patch:');
console.log(patchCode);
