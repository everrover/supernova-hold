def suggest_command(cmd):
    suggestions = {
        'encry': 'encrypt xor',
        'decry': 'decrypt xor',
        'hlp': 'help',
        'quit': 'exit'
    }
    return suggestions.get(cmd, None)
