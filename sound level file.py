while True:
    if 0< getSoundLevel() <80:
        display.show(Image.ASLEEP)
    
    elif 80< getSoundLevel() <150:
        display.show(Image.CONFUSED)
       
    else:
        display.show(Image.ANGRY)
