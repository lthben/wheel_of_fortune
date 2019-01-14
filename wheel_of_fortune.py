import serial
import tkinter as tk
import time 

ser = serial.Serial('/dev/ttyACM0',baudrate=9600)

#Parse the text file
tips_file = open("/home/pi/wheel_of_fortune/data/List of 17 SDG tips .txt")
long_string = tips_file.read()
split_long_string = long_string.split('\n\n') #split into the 17 SDGs

sdg_str = [] #list of 17 strings for 17 SDGs

for string in split_long_string:
    sdg_str.append(string.split('*')) #split into individual tips

for string in sdg_str:
    string.remove(string[0]) #remove the first line title string for each SDG

#print(sdg_str[11][3])

#Global variables
LATCH_TIME = 0 #num of seconds that will register a counter change for SDG tips when wheel stops spinning
IDLE_TIME = 30 #num of seconds after wheel stops spinning before the idle screen instruction to spin wheel is shown
sdg_tip_text = sdg_str[0][0] #the text tip currently being shown
sdg_index = 0 #tracks which index is being pointed at by the wheel
old_sdg_index = -99
sdg_tip_index = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #keeps track of which tip index is shown for each sdg
has_changed = False #tracks whether the sdg_tip_index has changed
change_time = time.clock() #time when the sdg index changes
is_idle = False #whether the wheel has been idle for IDLE_TIME
idle_screen_text= 'Spin the wheel to get a tip for a Sustainable Development Goal!'
is_idle_screen_updated = False #helps to ensure the idle screen is only activated once, else the text will flicker if gui updates continuously

#Tkinter
root = tk.Tk()
root.attributes("-fullscreen", True)
root.config(cursor='none')
screen_width = root.winfo_screenwidth() #1824
screen_height = root.winfo_screenheight() #984

#see SDG visual guidelines
image1 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-001.gif")
image2 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-002.gif")
image3 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-003.gif")
image4 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-004.gif")
image5 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-005.gif")
image6 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-006.gif")
image7 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-007.gif")
image8 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-008.gif")
image9 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-009.gif")
image10 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-010.gif")
image11 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-011.gif")
image12 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-012.gif")
image13 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-013.gif")
image14 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-014.gif")
image15 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-015.gif")
image16 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-016.gif")
image17 = tk.PhotoImage(file="/home/pi/wheel_of_fortune/data/SDG-017.gif")
images = [image1,image2,image3,image4,image5,image6,image7,image8,image9,image10,image11,image12,image13,image14,image15,image16,image17]

logobg = ['#%02x%02x%02x' % (image1.get(1,1)), #get pixel color at 1,1 from logo image and set the corresponding background color, converts from rgb to hex
          '#%02x%02x%02x' % (image2.get(1,1)),
          '#%02x%02x%02x' % (image3.get(1,1)),
          '#%02x%02x%02x' % (image4.get(1,1)),
          '#%02x%02x%02x' % (image5.get(1,1)),
          '#%02x%02x%02x' % (image6.get(1,1)),
          '#%02x%02x%02x' % (image7.get(1,1)),
          '#%02x%02x%02x' % (image8.get(1,1)),
          '#%02x%02x%02x' % (image9.get(1,1)),
          '#%02x%02x%02x' % (image10.get(1,1)),
          '#%02x%02x%02x' % (image11.get(1,1)),
          '#%02x%02x%02x' % (image12.get(1,1)),
          '#%02x%02x%02x' % (image13.get(1,1)),
          '#%02x%02x%02x' % (image14.get(1,1)),
          '#%02x%02x%02x' % (image15.get(1,1)),
          '#%02x%02x%02x' % (image16.get(1,1)),
          '#%02x%02x%02x' % (image17.get(1,1))]

#initial config
logo = tk.Label(root, borderwidth=0, highlightthickness=0, image=images[0])
msg = tk.Message(root, text=sdg_tip_text)
msg.config(justify=tk.CENTER, bg=logobg[0], fg="white", font=('Helvetica', int(screen_width/50), 'bold'), width=int(0.67*screen_width))

def update_gui():
#updates the gui based on serial data
    global is_idle
    
    if (is_idle == True):
        root.config(bg="black")
        logo.pack(padx=screen_width,pady=int(0.08*screen_height)) #hack to hide it by pushing the logo off the screen
        msg.config(text=idle_screen_text, bg="black")
        msg.pack()
   
    else:
        root.config(bg=logobg[sdg_index])
        logo.config(image=images[sdg_index])    
        logo.pack(padx=0,pady=int(0.08*screen_height))
        msg.config(text=sdg_tip_text, bg=logobg[sdg_index])
        msg.pack()

def readSerial():
##reads serial every few ms and update the GUI for any changes to the sgd_index

    global sdg_index, old_sdg_index, sdg_tip_text, has_changed, LATCH_TIME, change_time, is_idle, is_idle_screen_updated
    
    if (ser.in_waiting>0):
        line = ser.readline()
        find_sdg_index(line); #updates the sdg_index
        is_idle_screen_updated = False

        if (old_sdg_index != sdg_index):
            old_sdg_index = sdg_index
##            print(sdg_index)
            sdg_tip_text = sdg_str[sdg_index][sdg_tip_index[sdg_index]]
            change_time = time.clock()
            has_changed = False
            is_idle = False
            update_gui() #only called when sdg_index changes

    elif (time.clock() - change_time > LATCH_TIME and has_changed == False): #when no data is being sent, the wheel has stopped
        sdg_tip_index[sdg_index] = sdg_tip_index[sdg_index] + 1 #increment the counter to show next unique tip for that sdg
        sdg_tip_index[sdg_index] = sdg_tip_index[sdg_index] % len(sdg_str[sdg_index]) #start to 0 again if the last tip is shown
        has_changed = True

    elif (time.clock() - change_time > IDLE_TIME and has_changed == True and is_idle_screen_updated == False):
        is_idle = True
        is_idle_screen_updated = True
        update_gui()

    root.after(1, readSerial)

def find_sdg_index(raw_value):
##updates the global sdg_index to between 1 and 17 based on the rotary encoder reading
    global sdg_index
    
    value = int(raw_value);
    if (value <= 0): ##clockwise
        value = abs(value) 
        value = value%1600        
    else: ##anti-clockwise
        value = 1600 - value%1600
    value = int(value/94.12)
    sdg_index = value

#run once 
root.after(100, readSerial)

#needed Tkinter event loop
root.mainloop() 






    
