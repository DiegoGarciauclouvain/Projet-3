# Imports go at the top
from microbit import *
import radio
import music
import time
import random
microkey="ahfurixkrunwcsuflency"
radio.config(channel=2) #allume la radio pour pouvoir communiquer
radio.on()

def hashing(string): # fonction donnée qui permet de hasher
	"""
	Hachage d'une chaîne de caractères fournie en paramètre.
	Le résultat est une chaîne de caractères.
	Attention : cette technique de hachage n'est pas suffisante (hachage dit cryptographique) pour une utilisation en dehors du cours.

	:param (str) string: la chaîne de caractères à hacher
	:return (str): le résultat du hachage
	"""
	def to_32(value):
		"""
		Fonction interne utilisée par hashing.
		Convertit une valeur en un entier signé de 32 bits.
		Si 'value' est un entier plus grand que 2 ** 31, il sera tronqué.

		:param (int) value: valeur du caractère transformé par la valeur de hachage de cette itération
		:return (int): entier signé de 32 bits représentant 'value'
		"""
		value = value % (2 ** 32)
		if value >= 2**31:
			value = value - 2 ** 32
		value = int(value)
		return value

	if string:
		x = ord(string[0]) << 7
		m = 1000003
		for c in string:
			x = to_32((x*m) ^ ord(c))
		x ^= len(string)
		if x == -1:
			x = -2
		return str(x)
	return ""
def create_tlv_message(type_id, value): # fonction pour transformer un message en TLV
    """
    Crée un message TLV.
    :param type_id: Type de la donnée (int)
    :param value: Valeur (str ou bytes)
    :return: Message TLV sous forme de bytes
    """
    if isinstance(value, str):
        value = value.encode('utf-8')  # Convertir en bytes si nécessaire
    length = len(value)
    return bytes([type_id, length]) + value
def parse_tlv_message(data): # transformer un message tlv en un tableau [type,longueur du message, message crypté]
    """
    Analyse un message TLV reçu.
    :param data: Données reçues (bytes)
    :return: Tuple (type, length, value)
    """
    if len(data) < 2:
        return None  # Message invalide
    type = data[0]
    length = data[1]
    value = data[2:2+length]
    return [type, length, value]   
def vigenere(message, key, decryption=False): # fonction pour crypté/décrypté(dépendant d'un Boolean) un message
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        #Letters encryption/decryption
        if char.isalpha():
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else : 
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            #Put back in lower case if it was
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        #Digits encryption/decryption
        elif char.isdigit():
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:  
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text










# Code in a 'while True:' loop repeats forever
display.show(Image('05550:'
                   '05005:'
                   '05005:'
                   '05550:'
                   '05000:'
                   '05000:'
                  ))
display.scroll('Parent') #affiche P puis fais scroller parent sur l'écran
sleep(1000)

while True:
    if button_a.is_pressed() and button_b.is_pressed():  # les deux boutons pressé en même temps
        start_time = time.ticks_ms()  
        while button_a.is_pressed() and button_b.is_pressed():  # si on appye sur les deux boutons en même temps pendant
    
            if time.ticks_ms() - start_time >= 1000:            # plus d'une seconde
                display.clear()                                 # on clear l'affichage
    if button_a.was_pressed(): # si le bouton de gauche est pressé, on encrypte le message
        msg=vigenere("state",microkey,False) # encrypte "state"
        msg=create_tlv_message(0x02,msg) # on le transforme en TLV de type string
        radio.send_bytes(msg) # on l' envoie au micro-bit bébé
    if button_b.was_pressed(): # si le bouton de droite est pressé
        msg=vigenere("milk",microkey,False) # encrypte "milk"
        msg=create_tlv_message(0x02,msg) # on le transforme en TLV de type string
        radio.send_bytes(msg) #on l' envoie au micro-bit bébé
    if pin_logo.is_touched(): # si le logo est touché on fais comme pour les boutons mais avec "temperature"
        msg=vigenere("temperature",microkey,False)
        msg=create_tlv_message(0x02,msg)
        radio.send_bytes(msg)
    msg=radio.receive_bytes()
    if msg: # si on recoie un message
        msg=parse_tlv_message(msg) # on le transforme en tableau
        if msg: # si ce tableau n'est pas vide
            msg[2]=msg[2].decode('utf-8')# on récupère le message
                
            if (msg[0]==2): # si le message est un string
                msg[2]=vigenere(msg[2],microkey,True) # on le decrypte
                if(msg[2]=="angry"): # si c'est angry
                    music.play(music.RINGTONE) #on joue une musique
                    display.show(msg[2]) # et on affiche l'état du bébé
                    sleep(10000)
                else:
                    display.show(msg[2]) # on affiche l'état du bébé       
            elif (msg[0]==3 and ("°" or "?" in msg[2])): # si le message est une température
                msg[2]=vigenere(msg[2],microkey,True) # on le decrypte
                msg[2].replace("°","") # on elève "?" et "°"
                msg[2].replace("?","")
                degré=int(str(temperature())[:2]) # on prend qu'une partie de la température(23.56->23)
                display.scroll(degré) # on affiche la température
                sleep(10000) # éteint l'écran
                if(degré>30 or degré<18): # si trop chaud ou trop froid
                    music.play(music.NYAN) # on joue une musique
            elif(msg[0]== 4): # si le message est un entier
                msg[2]=vigenere(msg[2],microkey,True) # on le decrypte
                display.show(int(msg[2])) # on affiche le nombre de dose de lait 
            else:
                
                sleep(10000) # éteint l'écran
    
        

    

      