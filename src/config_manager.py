import json
import os
import glfw # Para os códigos das teclas

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "volume": 0.5,
            "key_bindings": {
                "move_forward": 87,    # W
                "move_backward": 83,   # S
                "move_left": 65,       # A
                "move_right": 68,      # D
                "jump": 32             # SPACE
            },
            "enable_corner_lights": True
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Garante que todas as teclas padrão existam
                if 'key_bindings' not in config:
                    config['key_bindings'] = self.default_config['key_bindings']
                else:
                    # Adiciona qualquer tecla padrão que esteja faltando
                    for key, value in self.default_config['key_bindings'].items():
                        if key not in config['key_bindings']:
                            config['key_bindings'][key] = value
                return config
        except FileNotFoundError:
            return self.default_config.copy()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_volume(self):
        return self.config.get('volume', 0.5)

    def set_volume(self, volume):
        self.config['volume'] = max(0.0, min(1.0, volume))
        self.save_config()

    def get_key_binding(self, action):
        return self.config['key_bindings'].get(action)

    def set_key_binding(self, action, key):
        self.config['key_bindings'][action] = key
        self.save_config()

    def get_enable_corner_lights(self):
        return self.config.get('enable_corner_lights', True)

    def set_enable_corner_lights(self, enable):
        self.config['enable_corner_lights'] = enable
        self.save_config() 