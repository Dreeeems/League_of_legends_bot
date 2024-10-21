import os
import requests
import discord
from dotenv import load_dotenv
import random

# URLs des champions et des runes

version = "https://ddragon.leagueoflegends.com/api/versions.json"
fetchinUrl = "https://ddragon.leagueoflegends.com/cdn/14.20.1/data/fr_FR/champion.json"
runeUrl = "https://ddragon.leagueoflegends.com/cdn/12.6.1/data/fr_FR/runesReforged.json"
base_image_url = "https://ddragon.leagueoflegends.com/cdn/img/"

def get_latest_version():
    versions = fetch(version)
    if versions:
        return versions[0]  # Retourne la première version
    return None

def fetch(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def searchRune(url):
    latest_version = get_latest_version()
    runesUrl = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/fr_FR/runesReforged.json"
    données = fetch(runesUrl)
    if données:
        # Sélectionner un arbre principal et un arbre secondaire aléatoires
        primary_tree = random.choice(données)
        secondary_tree = random.choice([tree for tree in données if tree != primary_tree])  # S'assurer que ce n'est pas le même arbre

        # Sélectionner toutes les runes de chaque slot de l'arbre primaire
        primary_runes = []
        for slot in primary_tree["slots"]:
            primary_rune = random.choice(slot["runes"])  # Sélectionner une rune aléatoire par slot
            primary_runes.append((primary_rune["name"]))

        # Sélectionner toutes les runes de chaque slot de l'arbre secondaire (deux slots)
        secondary_runes = []
        secondary_runes = []
        available_runes = []
        for slot in secondary_tree["slots"][-3:]:  # Limité aux trois derniers slots
            available_runes.extend(slot["runes"])  # Ajouter toutes les runes disponibles

        # Sélectionner deux runes aléatoires parmi les runes disponibles
        selected_runes = random.sample(available_runes, 2)
        for rune in selected_runes:
            secondary_runes.append((rune["name"]))

        # Retourner les informations des runes
        return {
            "primary_tree": primary_tree["name"],
            "primary_runes": primary_runes,
            "secondary_tree": secondary_tree["name"],
            "secondary_runes": secondary_runes
        }
    return None

def searchChamp(url):

    latest_version = get_latest_version()
    champ_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/fr_FR/champion.json"
    données = fetch(champ_url)
    if données:
        champions = list(données["data"].keys())
        champ = random.choice(champions)
        return données["data"][champ]
    return None

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialiser le bot Discord
intents = discord.Intents.all()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="Créateur dreems"))
    for guild in client.guilds:
        print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
        )

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if "!random" in message.content:
        champ = searchChamp(version)
        runes = searchRune(version)

        if champ and runes:
            # Construire le message à envoyer avec les données du champion et des runes
            champion_name = champ["name"]
            champion_title = champ["title"]
            primary_tree = runes["primary_tree"]
            primary_runes = "\n".join([f"{name} !" for name in runes["primary_runes"]])
            secondary_tree = runes["secondary_tree"]
            secondary_runes = "\n".join([f"{name} !" for name in runes["secondary_runes"]])
            embed = discord.Embed(title=f"Champion : {champion_name}")
            embed.add_field(name="Arbre principal : ",value=primary_tree, inline=False)
            embed.add_field(name="Runes principales : ",value=primary_runes,inline=False)
            embed.add_field(name="Arbre secondaire : ",value=secondary_tree,inline=False)
            embed.add_field(name="Runes secondaires : ",value=secondary_runes,inline=False)

            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Erreur lors de la récupération des données.")

client.run(TOKEN)
