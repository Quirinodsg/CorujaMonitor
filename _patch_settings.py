content = open('frontend/src/components/Settings.js', 'r', encoding='utf-8').read()

# Add import
old_import = "import TestTools from './TestTools';"
new_import = "import TestTools from './TestTools';\nimport DefaultSensorProfiles from './DefaultSensorProfiles';"
content = content.replace(old_import, new_import, 1)

# Add tab button before thresholds tab
marker = "activeTab === 'thresholds' ? 'active' : ''"
idx = content.find(marker)
if idx != -1:
    # Find the start of that button block
    btn_start = content.rfind('<button', 0, idx)
    insert_text = """        <button
          className={`tab ${activeTab === 'sensor-profiles' ? 'active' : ''}`}
          onClick={() => setActiveTab('sensor-profiles')}
        >
          \U0001f4e1 Sensores Padr\u00e3o
        </button>
        """
    content = content[:btn_start] + insert_text + content[btn_start:]

# Add tab content render
old_render = "{activeTab === 'thresholds' && <ThresholdConfig />}"
new_render = "{activeTab === 'sensor-profiles' && <DefaultSensorProfiles />}\n        {activeTab === 'thresholds' && <ThresholdConfig />}"
content = content.replace(old_render, new_render, 1)

open('frontend/src/components/Settings.js', 'w', encoding='utf-8').write(content)
print('OK - lines:', content.count('\n'))
