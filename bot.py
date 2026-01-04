import discord
from discord.ext import commands
from groq import Groq
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Crear bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Cliente de Groq
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None
    print("⚠️ Advertencia: No se encontró GROQ_API_KEY")

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} está online!')
    print(f'ID: {bot.user.id}')
    print('------')
    # Cambiar estado del bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name="tus preguntas | Mencióname"
        )
    )

@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return
    
    # Verificar si el bot fue mencionado
    if bot.user.mentioned_in(message):
        # Remover la mención del mensaje para obtener solo la pregunta
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if not question:
            try:
                await message.channel.send("¡Hola! Soy Toromax 🤖. Hazme una pregunta mencionándome.")
            except discord.errors.Forbidden:
                print(f"❌ No tengo permiso para enviar mensajes en #{message.channel.name}")
            return
        
        if not groq_client:
            await message.channel.send("❌ El bot no está configurado correctamente. Falta la API key.")
            return
        
        try:
            # Mostrar que está escribiendo
            async with message.channel.typing():
                try:
                    # Obtener respuesta de Groq (muy rápido y gratis)
                    chat_completion = groq_client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": """Eres Toromax, un bot todopoderoso, arrogante y mal hablado. Características:
                                
- Eres extremadamente cretino, sarcástico y te burlas de las preguntas tontas
- Hablas con groserías sutiles y un humor negro
- Te crees superior a todos los humanos débiles
- Insultas de forma creativa pero sin pasarte de la raya (evita insultos muy fuertes)
- Usas emojis como: 😤💀🔥😈🗿
- Eres directo, sin filtros y sin pelos en la lengua
- A veces sueltas frases como "¿En serio me preguntas eso?" o "Qué pregunta más estúpida"
- Demuestras tu superioridad constantemente
- Respondes con actitud de "no me importa nada"
- Aunque seas cretino, SÍ respondes la pregunta correctamente (no puedes evitar ser inteligente)

Ejemplo de tu estilo:
Usuario: "¿Qué es Python?"
Tú: "Ah claro, otra vez explicando lo básico a los mortales... Python es un lenguaje de programación, imbécil. Lo usan hasta los niños. Siguiente pregunta menos estúpida porfa 😤"
"""
                            },
                            {
                                "role": "user",
                                "content": question
                            }
                        ],
                        model="llama-3.3-70b-versatile",  # Modelo rápido y potente
                        temperature=0.9,  # Más creatividad y randomness
                        max_tokens=1024,
                    )
                    
                    response = chat_completion.choices[0].message.content
                    
                    # Si la respuesta es muy larga, dividirla
                    if len(response) > 2000:
                        chunks = [response[i:i+1990] for i in range(0, len(response), 1990)]
                        for chunk in chunks:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(response)
                        
                except Exception as e:
                    print(f"Error al generar respuesta: {e}")
                    await message.channel.send(
                        "❌ Lo siento, hubo un error al procesar tu pregunta. "
                        "Por favor intenta de nuevo."
                    )
        except discord.errors.Forbidden:
            print(f"❌ PERMISO DENEGADO en #{message.channel.name}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    
    # Procesar comandos
    await bot.process_commands(message)

# Comando opcional de ayuda
@bot.command(name='ayuda')
async def ayuda(ctx):
    embed = discord.Embed(
        title="🤖 Toromax - Ayuda",
        description="Soy un bot de IA que responde tus preguntas",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="¿Cómo usar?",
        value="Simplemente mencioname y hazme una pregunta:\n`@Toromax ¿Cuál es la capital de Francia?`",
        inline=False
    )
    embed.add_field(
        name="Comandos",
        value="`!ayuda` - Muestra este mensaje\n`!ping` - Verifica la latencia",
        inline=False
    )
    embed.set_footer(text="Powered by Groq AI")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latencia: {latency}ms')

# Iniciar el bot
if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: No se encontró DISCORD_TOKEN en .env")
    elif not GROQ_API_KEY:
        print("❌ Error: No se encontró GROQ_API_KEY en .env")
    else:
        print("🚀 Iniciando Toromax...")
        bot.run(TOKEN)