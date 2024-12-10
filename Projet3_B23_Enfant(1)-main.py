from microbit import *
import time
import radio


radio.on()
radio.config(channel=2)
microkey= "ahfurixkrunwcsuflency"  

# Variables for dose and settings
doses = 0
max_doses = 10

# Maximum inactivity time in milliseconds
MAX_INACTIVITY_TIME = 30000  # 30 seconds
last_activity_time = time.ticks_ms()  # Record last activity time
lightsOn = True  # Variable to control the display state (on/off)

# Function to display doses
def afficher_doses():
    if doses == 0:
        display.clear()  # Clear display if no doses
    else:
        display.show(str(doses))  # Show the number of doses

# Function to add a dose
def ajouter_dose():
    global doses
    if doses < max_doses:
        doses += 1
    afficher_doses()

# Function to remove a dose
def supprimer_dose():
    global doses
    if doses > 0:
        doses -= 1
    afficher_doses()

# Function to reset doses
def reinitialiser_doses():
    global doses
    doses = 0
    display.clear()  # Clear display when doses are reset
    afficher_doses()

# Function to handle inactivity (turn off display if idle)
def check_inactivity():
    global last_activity_time, lightsOn
    if time.ticks_ms() - last_activity_time >= MAX_INACTIVITY_TIME:
        if lightsOn:  # If display is on
            display.clear()  # Turn off display
            lightsOn = False  # Update screen status
    else:
        if not lightsOn:  # If display is off but there's activity
            lightsOn = True  # Turn display back on
            afficher_doses()  # Show doses

# Function to reset inactivity timer
def reset_inactivity_timer():
    global last_activity_time
    last_activity_time = time.ticks_ms()  # Reset activity timer
def create_tlv_message(type_id, value): # create a tlv message
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
def parse_tlv_message(data): # transform a tlv in an array [type,length of the message, message]
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
# Vigenère cipher for encryption and decryption
def vigenere(message, key, decryption=False): # encrypte and decrypte a message
    text = ""
    key_length = len(key)
    key_as_int = [ord(k) for k in key]

    for i, char in enumerate(str(message)):
        if char.isalpha():  # Encrypt/Decrypt alphabetic characters
            key_index = i % key_length
            if decryption:
                modified_char = chr((ord(char.upper()) - key_as_int[key_index] + 26) % 26 + ord('A'))
            else:
                modified_char = chr((ord(char.upper()) + key_as_int[key_index] - 26) % 26 + ord('A'))
            if char.islower():
                modified_char = modified_char.lower()
            text += modified_char
        elif char.isdigit():  # Encrypt/Decrypt numeric characters
            key_index = i % key_length
            if decryption:
                modified_char = str((int(char) - key_as_int[key_index]) % 10)
            else:
                modified_char = str((int(char) + key_as_int[key_index]) % 10)
            text += modified_char
        else:
            text += char
    return text

# Function to measure the temperature
def measure_temperature():
    return temperature()
# function to know the state of the baby
def baby_state():
    # Check if the sound level is low (0 <= sound_level < 80)
    if 0 <= sound_level < 80:
        return "calm"     
    
    # Check if the sound level is moderate (80 <= sound_level < 150)
    elif 80 <= sound_level < 200:
        return "normal"
    # Check if the sound level is high (sound_level >= 150)
    else:
        return "angry"  

# Main loop
while True:
    # Check inactivity
    check_inactivity()

    # Handle button presses
    if button_a.is_pressed() and button_b.is_pressed():
        start_time = time.ticks_ms()  # Start time when both buttons are pressed
        while button_a.is_pressed() and button_b.is_pressed():
            if time.ticks_ms() - start_time >= 1000:  # If held for 1 second
                reinitialiser_doses()  # Reset doses
                break
        reset_inactivity_timer()  # Reset inactivity timer
        sleep(500)  # Wait to avoid multiple button presses

    elif button_a.is_pressed():
        ajouter_dose()  # Add a dose when Button A is pressed
        reset_inactivity_timer()  # Reset inactivity timer
        sleep(500)  # Wait to avoid multiple presses

    elif button_b.is_pressed():
        supprimer_dose()  # Remove a dose when Button B is pressed
        reset_inactivity_timer()  # Reset inactivity timer
        sleep(500)  # Wait to avoid multiple presses

    # If logo is touched, show temperature
    if pin_logo.is_touched():
        display.scroll(temperature())

    # Automatically reset doses if max is reached
    if doses == max_doses:
        reinitialiser_doses()

    # Radio message handling
    msg = radio.receive_bytes()
    if msg:  #if a message was received
        msg =parse_tlv_message(msg) # transform it into an array
        if msg: # if the array isn't empty
            msg[2]=msg[2].decode('utf-8') # decode the message
            if (msg[0]==2): # if the message is a string
                msg[2]=vigenere(msg[2],"ahfurixkrunwcsuflency",True) #decrypte te message
                if msg[2]== 'milk': #if the message is "milk"
                    msg=vigenere(str(doses),microkey,False) # get the number of doses and encrypt it
                    msg=create_tlv_message(0x04,msg) # create at tlv from the encrypted message
                    radio.send_bytes(msg) # send the message to the parent
                if msg[2]== 'state':#if the message is "state"
                    msg=vigenere(baby_state(),microkey,False) # get the state of the baby
                    msg=create_tlv_message(0x02,msg) # create at tlv from the encrypted message
                    radio.send_bytes(msg) # send the message to the parent
                if msg[2]== 'temperature': # if the message is "temperature"
                    msg=vigenere(str(temperature())[:2]+'°',microkey,False) # encrypt the temperature
                    msg=create_tlv_message(0x03,msg) # transform it to a tlv
                    radio.send_bytes(msg) # send the message to the parent
            else:
                display.show(int(msg[2]))  # Show received dose number on display

    # Always update display if lights are on
    if lightsOn:
        afficher_doses()

    
    sound_level = microphone.sound_level() # the sound level of the baby

    if(sound_level>200): # if the baby is lound
        msg=vigenere("angry",microkey,False) # encrypt the string "angry"
        msg=create_tlv_message(0x02,msg) # transform it into a string
        radio.send_bytes(msg) # send the message to the parent
    if(int(str(temperature())[:2])>30 or (int(str(temperature())[:2])<18)): # if it's too cold/hot for the baby
        msg=vigenere(str(temperature())[:2]+"°",microkey,False) # encrypt the temperature
        msg=create_tlv_message(0x03,msg) # transform it into a tlv 
        radio.send_bytes(msg) # send the message
        
    
        
        
