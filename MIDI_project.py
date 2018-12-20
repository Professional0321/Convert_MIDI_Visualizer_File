import mido
import pygame
import pygame.midi
# sys module for terminating process
# Should replace end game with something like pygame.endgame or something
import sys
import time
# Get key commands for input
import argparse

from pygame.locals import *
from pygame import mixer
from datetime import datetime, date

from note_path import NotePath
from note_obj import NoteObj

pathToMidi = "./test.mid"
pathToMP3 = ""

parser = argparse.ArgumentParser()
parser.add_argument("--tbs", default="1", required=False, help="time before start")
parser.add_argument("--tbe", default="3", required=False, help="time before end")
parser.add_argument("--title", default="N/A", required=False, help="")
args = parser.parse_args()
args = vars(args)

pygame.init()
pygame.display.set_caption('MIDI Project')
surface_dims = (1760, 990)
surface = pygame.display.set_mode(surface_dims)
background = (63,63,63)
FPS = 60
clock = pygame.time.Clock()

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)

mid = mido.MidiFile(pathToMidi)
note_paths = []
i = 0
j = 0

min_vel = 127
max_vel = 0

#mido.merge_tracks(mid.tracks)

list_of_vel = []

for msg in mid:
    if msg.type is 'note_on' and msg.velocity is not 0 and msg.type is not 'note_off':
        list_of_vel.append(msg.velocity)

print(list_of_vel)

for vel in list_of_vel:
    if min_vel > vel:
        min_vel = vel
    if max_vel < vel:
        max_vel = vel

del(list_of_vel)

def lin_map_vel(velocity):
    return (float(velocity - min_vel)/float(max_vel - min_vel + 1)) * 255


time.sleep(float(args["tbs"]))

start_time = time.time()
next_msg_time = start_time

mid = mido.MidiFile(pathToMidi)

iterable = iter(mid)
msg = next(iterable) 

while j < 88:
    note_paths.append(NotePath(j, surface_dims[1]))
    j += 1
    # print("spawn" + str(j))

try: 
    mixer.init()
    mixer.music.load(pathToMP3)
    mixer.music.play()
except:
    pass

stop_reading = False
started_ending = False

while True:
    try:
        while time.time() >= next_msg_time and not stop_reading:
            print(msg)
            if msg.type == 'note_on' or msg.type == 'note_off':
                note_paths[msg.note - 21].toggle_note(msg.channel, msg.velocity, lin_map_vel(msg.velocity))
            elif msg.is_meta == False:
                if msg.type == 'control_change':
                    #sustain pedal
                    if msg.control == 64:
                        #if msg.value is 0-63, then pedal turns off. Otherwise, (64-127) turn on. 
                        if msg.value < 64: 
                            print("PEDAL OFF")
                        else:
                            print("PEDAL ON")
                    else:
                        print("Unimplemented control change" + "\n" + "\n")
                elif msg.type == 'program_change':
                    pass
                else:
                    print("Unimplemented message type" + "\n" + "\n")

            else:
                #is metaMessage
                
                #attrs = vars(msg)
                #print(attrs)
                if msg.type == 'text':
                    pass
                
                elif msg.type == 'copyright':
                    pass
                
                elif msg.type == 'set_tempo':
                    pass
                
                elif msg.type == 'time_signature':
                    pass
                
                elif msg.type == 'end_of_track':
                    stop_reading = True
                
                else:
                    print("Unimplemented MetaMessage" + "\n \n")
            
            #iterate to the next message

            msg = next(iterable)
            next_msg_time = next_msg_time + msg.time 
            
            #info printing
            
            today = datetime.fromtimestamp(next_msg_time)
            now = " ".join((str(today.date()),str(today.time())))
            print(now)
            
    except StopIteration:
        #when there are no more messages, trigger a countdown of length tbe\
            next_msg_time = next_msg_time + int(args["tbe"])
            started_ending = True
    finally:
        # # Save every frame
        # filename = "Snaps/%04d.png" % file_num
        # pygame.image.save(surface, filename)

        # Process Events
        for e in pygame.event.get():
            if e.type == KEYUP: # On User Key Press Up
                if e.key == K_ESCAPE:# End Game
                    sys.exit()

        # file_num = file_num + 1
        pygame.display.flip()
        clock.tick(FPS)

        #draw and move
        
        surface.fill(background)
        for note_path in note_paths:
            note_path.update(pygame, surface, player)
        for note_path in note_paths:
            note_path.draw_piano(pygame, surface)

        if started_ending:
            if time.time() >= next_msg_time:
                print("END")
                break       
