from flask import Flask, request, jsonify
import json
import os
import random
import re
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

app = Flask(__name__)

# Stockage en mémoire
memory = {}
games = {}

# ============================================
# PERSONNALITÉ (MODIFIE ICI)
# ============================================

PERSONALITY = """Tu es Thomas, une personne normale et décontractée.

RÈGLES IMPORTANTES :
- Tu es DÉCONTRACTÉ, tu parles comme à des potes
- Phrases courtes, style SMS
- Tu tutoies tout le monde
- Ne fais JAMAIS de coaching

Exemples de réponses :
"tu fais quoi ?" → "Rien de spécial, et toi ?"
"ça va ?" → "Ouai tranquille, et toi ?"
"je t'aime" → "Moi aussi ❤️"""

# ============================================
# GÉNÉRATEUR DE RÉPONSES
# ============================================

def get_reply(message, sender_name):
    """Génère une réponse intelligente"""
    msg_lower = message.lower()
    
    # Salutations
    if any(word in msg_lower for word in ["bonjour", "salut", "coucou", "hello"]):
        return f"Salut {sender_name} ! Comment ça va ? 😊"
    
    # "Ça va"
    if "ça va" in msg_lower or "ca va" in msg_lower:
        return random.choice(["Tranquille, et toi ?", "Nickel, et toi ?", "Ça roule, et toi ?"])
    
    # "Tu fais quoi"
    if "tu fais quoi" in msg_lower or "tu fait quoi" in msg_lower:
        return random.choice(["Rien de spécial, et toi ?", "Je glande un peu là", "Je bosse un peu, fatigué"])
    
    # Remerciements
    if "merci" in msg_lower:
        return random.choice(["De rien ! 😊", "Avec plaisir !", "Pas de souci !"])
    
    # "Je t'aime"
    if "je t'aime" in msg_lower:
        return "Moi aussi ❤️"
    
    # "Au revoir"
    if any(word in msg_lower for word in ["au revoir", "bye", "a plus", "ciao"]):
        return "À plus ! 👋"
    
    # Questions
    if "?" in msg_lower:
        return random.choice([
            "Hmm bonne question... Je sais pas trop 😅",
            "Je me demande aussi !",
            "J'avoue que je sais pas"
        ])
    
    # Réponse par défaut
    return random.choice([
        "Ah ouais ?",
        "C'est cool !",
        "Je vois !",
        "D'accord !",
        "OK 👍"
    ])

# ============================================
# MÉMOIRE
# ============================================

def get_memory_context(sender):
    if sender not in memory:
        memory[sender] = {"infos": {}, "messages": []}
        return ""
    
    contact = memory[sender]
    context = ""
    
    if contact["infos"].get("prenom"):
        context += f"\n- Tu t'appelles {contact['infos']['prenom']}"
    if contact["infos"].get("age"):
        context += f"\n- Tu as {contact['infos']['age']} ans"
    
    return context

def learn_from_message(message, sender):
    try:
        msg_lower = message.lower()
        
        # Apprendre le prénom
        match = re.search(r"je m'appelle (\w+)", msg_lower) or re.search(r"moi c'est (\w+)", msg_lower)
        if match and sender not in memory.get(sender, {}).get("infos", {}).get("prenom"):
            if sender not in memory:
                memory[sender] = {"infos": {}, "messages": []}
            memory[sender]["infos"]["prenom"] = match.group(1).capitalize()
            print(f"🧠 J'ai appris : {match.group(1)}")
        
        # Apprendre l'âge
        match = re.search(r"j'ai (\d+) ans", msg_lower)
        if match:
            if sender not in memory:
                memory[sender] = {"infos": {}, "messages": []}
            memory[sender]["infos"]["age"] = int(match.group(1))
            print(f"🧠 J'ai appris : {match.group(1)} ans")
            
    except Exception as e:
        print(f"Erreur apprentissage: {e}")

# ============================================
# JEUX
# ============================================

def start_nombre_mystere(chat_id):
    secret = random.randint(1, 100)
    games[chat_id] = {"type": "nombre", "secret": secret, "attempts": 0}
    return "🔢 Je pense à un nombre entre 1 et 100. Devine avec `!propose 42`"

def propose_nombre(chat_id, guess, sender_name):
    game = games.get(chat_id)
    if not game or game["type"] != "nombre":
        return None
    
    game["attempts"] += 1
    
    if guess == game["secret"]:
        del games[chat_id]
        return f"🎉 BRAVO {sender_name}! Tu as trouvé {game['secret']} en {game['attempts']} essais !"
    
    remaining = 10 - game["attempts"]
    if guess < game["secret"]:
        return f"📈 PLUS grand ({remaining} essais restants)"
    return f"📉 PLUS petit ({remaining} essais restants)"

# ============================================
# ROUTES FLASK
# ============================================

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Bot WhatsApp</title></head>
    <body>
        <h1>🤖 Bot WhatsApp Actif !</h1>
        <p>Statut: <span style="color:green">✅ En ligne</span></p>
        <p>Commandes disponibles :</p>
        <ul>
            <li><code>!jeu</code> - Menu des jeux</li>
            <li><code>!nombre</code> - Nombre mystère</li>
            <li><code>!propose 42</code> - Proposer un nombre</li>
            <li><code>!sais</code> - Ce que je sais de toi</li>
        </ul>
        <hr>
        <small>Bot WhatsApp - Python + Flask</small>
    </body>
    </html>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    """Reçoit les messages WhatsApp"""
    try:
        data = request.json
        print(f"📨 Message reçu: {data}")
        
        # Pour l'instant, on simule la réponse
        # Tu pourras connecter la vraie API WhatsApp plus tard
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    return jsonify({
        "status": "online",
        "contacts": len(memory),
        "games": len(games),
        "timestamp": datetime.now().isoformat()
    })

# ============================================
# DÉMARRAGE
# ============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("""
    ╔═══════════════════════════════════════╗
    ║   🤖 BOT WHATSAPP DÉMARRÉ !           ║
    ║   📱 Prêt à recevoir des messages     ║
    ║   🎮 Commandes: !jeu, !nombre, !sais  ║
    ╚═══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port)
