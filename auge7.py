# -*- coding: utf-# Projekt AUGE STEUERT ROLLSTUHL
# Eyetracking mit openCV
#
# Bundeswettbewerb Jugend forscht
# Myrijam Stoetzer & Paul Foltin
# https://zerozeroonezeroonezeroonezero.wordpress.com
# 


import numpy as np
import cv2
import time
from pyfirmata import Arduino, util
from espeak import espeak


board = Arduino('/dev/ttyUSB0')  # mit Arduino-IDE überprüfen, ob das der USB-Anschluss ist

richtungsausgabe = False
zeit = time.time()

espeak.set_voice("de")

espeak.synth("bitte einen Moment warten")


def stop ():
    board.digital[8].write(0) #Motorrichtung A beide Pins
    board.digital[9].write(0)
    board.digital[10].write(0)#Motorrichtung B beide Pins
    board.digital[11].write(0)
    time.sleep(1)


# in diesen Funktionen werden die Motoren angeschaltet - diesmal über Relais, nicht mehr H-Brücke
def motoren (richtung):
    if richtung == "B":
       board.digital[8].write(0) #Motorrichtung A beide Pins
       board.digital[9].write(1)
       board.digital[10].write(1)#Motorrichtung B beide Pins
       board.digital[11].write(0)
       while taster.read() == False:
             print "B"
       print "MOTOR STOP!"
       espeak.synth("STOP")
       stop()
             
    if richtung == "F":
       board.digital[8].write(1) #Motorrichtung A beide Pins
       board.digital[9].write(0)
       board.digital[10].write(0)#Motorrichtung B beide Pins
       board.digital[11].write(1)
       while taster.read() == False:
             print "F"
       print "MOTOR STOP!"
       espeak.synth("STOP")
       stop()
        
    if richtung == "L":
       board.digital[8].write(1) #Motorrichtung A beide Pins
       board.digital[9].write(0)
       board.digital[10].write(1)#Motorrichtung B beide Pins
       board.digital[11].write(0)
       while taster.read() == False:
             print "L"
       print "MOTOR STOP!"
       espeak.synth("STOP")
       stop()

    if richtung == "R":
       board.digital[8].write(0) #Motorrichtung A beide Pins
       board.digital[9].write(1)
       board.digital[10].write(0)#Motorrichtung B beide Pins
       board.digital[11].write(1)
       while taster.read() == False:
             print "R"
       print "MOTOR STOP!"
       espeak.synth("STOP")
       stop()

    return

# hiermit liefert der Arduino über Firmata die Daten der AD-Wandler

it = util.Iterator(board)
it.start()


# die entsprechenden PINs am Arduino-Board zuweisen

pin0 = board.get_pin('a:0:i')
pin1 = board.get_pin('a:1:i')
pin2 = board.get_pin('a:2:i')
pin4 = board.get_pin('a:3:i')
pin3 = board.get_pin('a:4:i')
taster = board.get_pin('d:12:i')


# abwarten, bis über Firmata sinnvolle Werte zurückkommen

while pin0.read() is None:
    pass

while pin1.read() is None:
    pass

while pin2.read() is None:
    pass

while pin3.read() is None:
    pass

while pin4.read() is None:
    pass




# Videocapture zuweisen, Höhe 320 Pixel, Breite = 240

cap = cv2.VideoCapture(0)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

# Zähler, falls die Geschwindigkeit in fps ermittelt werden soll

frames = 0



#if cap.isOpened() == False : cap.open()


# diese Schleife läuft immer

while(True):

    # abwarten, bis ein Bild von der Kamera fertig eingelesen wurde
    video = False
    while video == False:
        video, frame = cap.read()
        
        
    # Hier beginnt die Filterkaskade

    # Das Bild wird gefiltert -- Farbe nach graustufe


    # die Bereiche, in denen die Blick-Befehle liegen, werden durch Grenzlinien markiert
    # die über die Potis eingestellt werden. Hier werden die Koordinaten der Linien ermittelt.

    y1 = int(120*pin2.read())
    y2 = int(120*pin4.read())+120
    x1 = int(160*pin0.read())
    x2 = int(160*pin1.read())+160

    # Das Bild wird gefiltert -- Farbe (Bild-Variable "frame" nach graustufe (Bildvaribale „grau“)

    grau = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Einzeichnen der Linien, die die Bildbereiche/Befehle trennen
    # Es wird das Bild "Frame" genommen und die Linien eingezeichnet, das Zielbild (Variable) heisst "test"
    test = cv2.line(frame, (0,y1), (319,y1), (255,0,0),1)
    test = cv2.line(frame, (0,y2), (319,y2), (255,0,0),1)
    test = cv2.line(frame, (x1,0), (x1,319), (255,0,0),1)
    test = cv2.line(frame, (x2,0), (x2,319), (255,0,0),1)

    # nun wird das Bild leicht unscharf gemacht, damit Bildrauschen reduziert wird
    grau_entrauscht = cv2.GaussianBlur(grau, (5, 5), 0)

    # anschließend wird das graue, entrauschte Bild nach Schwarz/Weiß gewandelt
    # dabei wird der Trennwert aus dem POTI-Wert ermittelt (über Arduino)

    ret, cut = cv2.threshold(grau_entrauscht, 80+80*pin3.read(), 255, cv2.THRESH_BINARY)

    # das Bild liegt in der Zielvariablen "cut"


    # hier wird ein "Filterbild" erzeugt, d.h. ein Feld mit 3x3 Punkten und 8Bit Auflösung - wie die Kamerabilder
    # das Array dient zum Filtern des S/W-Bildes, bei dem offene Bereiche geschlossen werden.
    # damit werden zB offene Halbkreise (schräge Perspektive auf die Iris) geschlossen

    kernel = np.ones((3, 3), np.uint8)
    gestalt_schliessen = cv2.morphologyEx(cut, cv2.MORPH_CLOSE, kernel, iterations=2)

    # für die nächsten Schritte muss das Bild invertiert werden, dann kopieren da contours das Bild verändert

    gestalt_schliessen = (255-gestalt_schliessen)
    gestalt2 = gestalt_schliessen.copy()

    # nun werden Konturen, d.h. zusammenhängende Bildbereiche gesucht.
    # Bei guter Einstellung der Parameter ist das ausschließlich die Iris
    
    konturen, hierarchy = cv2.findContours(gestalt2, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    #größte Contour finden -- besser wäre es eine Kontur der Groesse der Iris zu finden
    #die Größe der Iris müsste man empirisch ermitteln

    max_flaeche = 0
    for zaehler in konturen:
            
        #der größte Wert wird überschrieben

        flaeche = cv2.contourArea(zaehler)
            
        if flaeche > max_flaeche:
            max_flaeche = flaeche
            max_zaehler = zaehler
        # testausgabe der pupillenkontur: empirische werte zw 300 und 1300
        # suche nach größtem wert geht aber auch
        # print (max_area)

    # in der Varibalen wird die Kontur/der Bildbereich gespeichert, der ermittelt wurde

    M = cv2.moments(max_zaehler)

    # nun werden die X- und Y-Koordinaten ermittelt ("Schwerpunkt der Fläche“) und ein Kreis eingezeichnet
    cx,cy = int(M['m10']/ M['m00']),int(M['m01']/ M['m00'])
    cv2.circle(frame,(cx,cy),5,255, -1)
            

    # das ist das SW-Bild, das nur noch die Pupille als Fleck zeigen soll
    cv2.imshow("Pupille", cut)

        
    # das ist das Webcam-Bild, in dem die Pupille markiert wird und die Begrenzungslinien eingezeichnet sind
    cv2.imshow('Eyetracker', frame)

    # hier wird nach Stop-Befehlen geguckt (ESC-Taste) oder ob die Pupillen-Kontur gespeichert werden soll
    # um später mal diese Größen zu nehmen und nicht die größte Kontur zu suchen

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("auge.jpg", gestalt_schliessen)

    # Überprüfen, ob die Koordinaten der Pupille in den jeweiligen Befehlsbereichen liegen
    # F=forward; b=back; L=left; R=right

    if (cy < y1) & (cx > x1) & (cx < x2) :
        if taster.read() == True:
            if richtungsausgabe == False:
                print "Nach vorne fahren?"
                espeak.synth("vorwärts?")
                richtungsausgabe = True
                zeit = time.time()
            if richtungsausgabe == True & ((time.time()-zeit) > 2): richtungsausgabe = False 

            
        if (richtungsausgabe == True) & (taster.read()== False) & ((time.time()- zeit) <2) :
            richtungsausgabe = False
            motoren("F")

    if (cy > y2) & (cx > x1) & (cx < x2):
        if taster.read() == True:
            if richtungsausgabe == False:
                print "Nach hinten fahren?"
                espeak.synth("rückwärts?")
                richtungsausgabe = True
                zeit = time.time()
            if richtungsausgabe == True & ((time.time()-zeit) > 2): richtungsausgabe = False 

            
        if (richtungsausgabe == True) & (taster.read()== False) & ((time.time()- zeit) <2) :
            richtungsausgabe = False
            motoren("B")


    if (cy > y1) & (cy < y2) & (cx < x1) :
        if taster.read() == True:
            if richtungsausgabe == False:
                print "Nach rechts fahren?"
                espeak.synth("rechts?")
                richtungsausgabe = True
                zeit = time.time()
            if richtungsausgabe == True & ((time.time()-zeit) > 2): richtungsausgabe = False 

            
        if (richtungsausgabe == True) & (taster.read()== False) & ((time.time()- zeit) <2) :
            richtungsausgabe = False
            motoren("R")




    if (cy > y1) & (cy < y2) & (cx > x2) :

        if taster.read() == True:
            if richtungsausgabe == False:
                print "Nach links fahren?"
                espeak.synth("links?")
                richtungsausgabe = True
                zeit = time.time()
            if richtungsausgabe == True & ((time.time()-zeit) > 2): richtungsausgabe = False 

            
        if (richtungsausgabe == True) & (taster.read()== False) & ((time.time()- zeit) <2) :
            richtungsausgabe = False
            motoren("L")

    # Ausgabe der position, Taster
    #print "X", cx, "   Y", cy, taster.read(), richtungsausgabe, time.time()



# Ende, falls ESC gedrückt wurde
cap.release()
cv2.destroyAllWindows()
stop()
