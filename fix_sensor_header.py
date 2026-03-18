content = open('frontend/src/components/SensorLibrary.js', 'r', encoding='utf-8').read()

# Find and show the sensor-header section
idx = content.find('sensor-header')
print("Current sensor-header section:")
print(repr(content[idx:idx+400]))
print()

# Replace inline-styled sensor-header with clean CSS class version
old = '              <div className="sensor-header" style={{ display: \'flex\', alignItems: \'center\', gap: 8, marginTop: 4, paddingRight: 70 }}>\n                <span style={{ fontSize: 20, flexShrink: 0 }}>{getSensorIcon(sensor.category)}</span>\n                <h3 style={{ fontSize: 14, margin: 0, whiteSpace: \'nowrap\', overflow: \'hidden\', textOverflow: \'ellipsis\', minWidth: 0 }}>{sensor.name}</h3>\n              </div>'

new = '              <div className="sensor-header">\n                <span style={{ fontSize: 20, flexShrink: 0 }}>{getSensorIcon(sensor.category)}</span>\n                <h3>{sensor.name}</h3>\n              </div>'

if old in content:
    content = content.replace(old, new)
    open('frontend/src/components/SensorLibrary.js', 'w', encoding='utf-8').write(content)
    print('FIXED OK')
else:
    print('Pattern not found - trying alternate search')
    # Show what's actually there
    start = content.find('"sensor-header"')
    print(repr(content[start:start+500]))
