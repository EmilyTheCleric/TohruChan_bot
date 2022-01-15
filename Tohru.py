import discord
from discord.ext import commands,tasks
import os
import emoji
from secret import TOKEN
from datetime import datetime, timedelta


####following from: https://stackoverflow.com/questions/36216665/find-there-is-an-emoji-in-a-string-in-python3
from emoji import UNICODE_EMOJI_ENGLISH  

def is_emoji(s):
    return s in UNICODE_EMOJI_ENGLISH.keys()
####end code


if(not os.path.exists('prefixes.txt')):
  file=open("prefixes.txt",'w', encoding='utf-8')
  file.close()

if(not os.path.exists('role_messages.txt')):
  file=open("role_messages.txt",'w', encoding='utf-8')
  file.close()

if(not os.path.exists('events.txt')):
  file=open("events.txt",'w', encoding='utf-8')
  file.close()

if(not os.path.exists('event_channels.txt')):
  file=open("event_channels.txt",'w', encoding='utf-8')
  file.close()

class ReactRoleMessages:
  def __init__(self, message_id,pairs):
    self.messageID=message_id
    self.pairs=pairs
  def add_emoji_role_pair(self,emoji,role):
    self.pairs[emoji]=role
  def __str__(self):
    string = self.messageID
    for e,r in self.pairs.items():
      string+=','+e+','+r
    return string+'\n'

def getRoleMessages():
  lst = []
  file = open('role_messages.txt','r', encoding='utf-8')
  lines=file.read().split('\n')
  file.close()
  for line in lines:
    # try:
      data=line.split(',')
      pairs={}
      for i in range(1,len(data),2):
        pairs[data[i]]=data[i+1]
      lst.append(ReactRoleMessages(data[0],pairs)) 
    # except:
    #   print(line)
  return lst

def getEventChannels():
  file=open('event_channels.txt','r')
  lines = file.read().split('\n')
  file.close()
  dic={}
  for line in lines:
    try:
      data=line.split(',')
      dic[data[0]]=data[1]
    except:
      print(line)
  return dic

def addRoleMessages(obj):
  file = open('role_messages.txt','a', encoding='utf-8')
  file.write(obj.__str__())
  file.close()

def appendFile(fname,line):
  file=open(fname,'r',encoding='utf-8')
  lines = file.read().split('\n')
  file.close()

  gid=line.split(',')[0]

  write=[]
  replaced=False
  for l in lines:
    their_gid=l.split(',')[0]
    if their_gid == gid:
      write.append(line)
      replaced=True
      break;
    else:
      write.append(l)

  if not replaced:
    write.append(line)

  file=open(fname,'w',encoding="utf-8")
  file.write('\n'.join(write))
  file.close()

def getEventChannel(gid):
  try:
    return event_channels[gid]
  except:
    return -1

###MM/DD/YY starting at 6:42pm
def prettifyDate(dtime):
  string=''
  string+=str(dtime.month)+'/'+str(dtime.day)+'/'+str(dtime.year) +' starting at '
  time_stamp='am'
  hour=dtime.hour
  if(hour>12):
    hour-=12
    time_stamp='pm'
  minute = dtime.minute
  if minute<10:
    minute = '0'+str(minute)
  string+=str(hour)+':'+str(minute)+str(time_stamp) 
  return string



##############################################BOT INITIALIZATION CODE########################
##########Following code based on: https://stackoverflow.com/questions/56796991/discord-py-changing-prefix-with-command

def read_prefixes():
    file = open("prefixes.txt",'r', encoding='utf-8')
    lines=file.read().split('\n')
    file.close()
    prefixes={}
    for line in lines:
        try:
            gid = int(line.split(',')[0])
            prefix=line.split(',')[1]
            prefixes[gid]=prefix
        except:
            print(line)
    return prefixes
              
custom_prefixes = read_prefixes()


#You'd need to have some sort of persistance here,
#possibly using the json module to save and load
#or a database                
default_prefixes = ['!']

async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        return custom_prefixes.get(guild.id, default_prefixes)
    else:
        return default_prefixes

#set up the bot with intents and whatnot
intents = discord.Intents.all()
client = commands.Bot(intents=intents,command_prefix=determine_prefix)

@client.command(brief="sets a custom prefix for the server",
                help="""syntax:
                            setprefix <prefix>       sets the bot to use a custom prefix for this server""")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, *, prefixes=""):
    if(not len(prefixes.split(" "))==1):
       await ctx.send("Error, prefixes can not have spaces")
       return
    alterPrefixFile(ctx.guild.id,(prefixes.split() or default_prefixes)[0])
    custom_prefixes[ctx.guild.id] = prefixes.split() or default_prefixes
    await ctx.send("Prefix set!")

def alterPrefixFile(gid,prefix):
    file = open("prefixes.txt",'r')
    lines=file.read().split('\n')#get lines
    file.close()
    found = False
    for line in lines:#iterate through lines
        data=line.split(',')
        if data[0] == str(gid):#if we found the guild id
            found=True
            lines.remove(line)
            data[1]=prefix
            lines.append(",".join(data))#change the prefix
            break
    if not found:#otherwise add it to the end
        lines.append(str(gid)+','+prefix)
    newFile='\n'.join(lines)
    file=open('prefixes.txt','w')#write a new file
    file.write(newFile)
    file.close()
    
######################End taken code########################################

role_messages=getRoleMessages();
event_channels=getEventChannels();

##############################################END BOT INITIALIZATION CODE########################

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


################################################ROLE REACT COMMANDS###############################

#!make_react_roles channel message_content
# aight, please do emoji @role to add role
#  :girl: she/her
# added, say done for done, or add more
#  :boy: he/him
# added, say done for done, or add more
@client.command(brief="Sends a role react message to a specified channel",
                help="""syntax:
                            make_react_roles <channel> [message content]""")
async def make_react_roles(ctx,*args):
  channel=args[0].strip('<').strip('#').strip('>')
  message_content=' '.join(args[1:])
  print(channel)
  try:
    channel=client.get_channel(int(channel))
  except:
    await ctx.send("please make sure you do #channel-name")
    return
  if(not channel):
    await ctx.send("error could not find channel "+channel)
    return
  await ctx.send("gotcha, now please enter the emoji role combo you want in the following format:\n:emoji: @role")
  pairs = await ask_for_pair(ctx,True,{})
  if pairs == -1:
    return
  message_content +='\n'
  for e,r in pairs.items():
    message_content+= e+': <@&'+r+'>\n'
  message = await channel.send(message_content)
  for emoji in pairs.keys():
    await message.add_reaction(emoji)
  obj = ReactRoleMessages(str(message.id),pairs)
  addRoleMessages(obj)
  role_messages.append(obj)

#before calling this function ask user to input stuff
async def ask_for_pair(ctx,first,pairs):
  def check(m): #check to see if user is typing
    return ctx.message.author == m.author

  try:
    msg = await client.wait_for('message', timeout=120.0,check=check) #set up message
  except asyncio.TimeoutError:
    await ctx.send('Error, timeout, please restart if you wish to try again')#time out error
    return -1
  
  else:
    if('done' in msg.content): #if user is done
      return pairs#base case good path, returns dic

    data=msg.content.split(' ')#the emoji role pair (hopefully)

    if(not is_emoji(data[0])):#not an emoji
      message="error, not an emoji, please use the format:\n:emoji: @role"
      if(not first):
        message+='\n or say done if finished'
      await ctx.send(message)
      return await ask_for_pair(ctx,first,pairs)
    else:
      roleId=data[1].strip('<').strip('>').strip('@').strip('&')
      try:
        role=ctx.guild.get_role(int(roleId))
      except: #role not good
        message="error, could not find that role, please use the format:\n:emoji: @role"
        if(not first):
          message+='\n or say done if finished'
        await ctx.send(message)
        return await ask_for_pair(ctx,first,pairs)
      if(not role):#error finding role
        message="error, could not find that role, please use the format:\n:emoji: @role"
        if(not first):
          message+='\n or say done if finished'
        await ctx.send(message)
        return await ask_for_pair(ctx,first,pairs)
      pairs[data[0]]=roleId#actually add to dict
      await ctx.send("added, say done for done, or add more")
      return await ask_for_pair(ctx,False,pairs)

#store in file, 
#message id,emoji,role,emoji,role
@client.event
async def on_raw_reaction_add(payload):
  global role_messages
  if(payload.member.bot):
    print('is bot')
    return
  react_message=payload.message_id
  our_obj = None
  for obj in role_messages:
    if  obj.messageID == str(react_message):
      our_obj = obj
  if not our_obj:
    print('no matching ids')
    return
  if not payload.emoji.is_unicode_emoji():
    print('not a unicode emoji')
    return
  print(our_obj)
  role = our_obj.pairs[payload.emoji.name]
  member = payload.member
  guildid=payload.guild_id
  Guild = client.get_guild(guildid)
  if not Guild:
    print('guild not found')
    return
  print(role)
  r=Guild.get_role(int(role))
  if not r:
    print('role not found')
    return
  await member.add_roles(r)
  #its a react message
    
@client.event
async def on_raw_reaction_remove(payload):
  global role_messages
  guildid=payload.guild_id
  Guild = client.get_guild(guildid)
  member=Guild.get_member(payload.user_id)
  if(member.bot):
    print('is bot')
    return
  react_message=payload.message_id
  our_obj = None
  for obj in role_messages:
    if  obj.messageID == str(react_message):
      our_obj = obj
  if not our_obj:
    print('no matching ids')
    return
  if not payload.emoji.is_unicode_emoji():
    print('not a unicode emoji')
    return
  print(our_obj)
  role = our_obj.pairs[payload.emoji.name]
  if not Guild:
    print('guild not found')
    return
  print(role)
  r=Guild.get_role(int(role))
  if not r:
    print('role not found')
    return
  await member.remove_roles(r)
  #its a react message

###########################END REACTION MESSAGES#####################################

##################Event Stuff##########################################

@client.command()
async def set_event_channel(ctx,channel):
  global event_channels
  print(event_channels)
  channelId=channel.strip('<').strip('#').strip('>')
  try:
    channel=client.get_channel(int(channelId))
    if channel:
      appendFile('event_channels.txt',str(ctx.guild.id)+','+channelId)
      event_channels[str(ctx.guild.id)]=channelId
      await channel.send("message will appear here")
    else:
        await ctx.send("unable to find channel "+channelId)
  except:
    await ctx.send("unable to find channel "+channelId)

#!make_event event name at 12-8-21 6pm for @interests/baking @interests/sewing
@client.command()
async def make_event(ctx,*args):
  event_channel_id = getEventChannel(str(ctx.guild.id))

  if event_channel_id == -1:
    await ctx.send("Error, event channel not set up, please do: \n!set_event_channel #channel\n first")
    return
  channel=ctx.guild.get_channel(int(event_channel_id))
  if not channel:
    print('no channel found')
    print(event_channel_id)
    return

  args=list(args) #lists r easier to work with than tuples

  syntax = validateSyntax(args)
  if syntax == -1:
    await ctx.send("error, please use the following syntax:\n!make_event event name at MM-DD-YYYY HH:MM for @interest1 @interest2")
    return
  (name,date,roles)=syntax

  

  event_datetime = ValidateDate(date)

  if event_datetime==-1:
    await ctx.send("error, please input date in format MM-DD-YYYY")
  elif event_datetime==-1:
    await ctx.send("error, please input time as HH:MM")
  
  def check(m): #check to see if user is typing
      return ctx.message.author == m.author

  role_ids=[]
  good_roles=[]
  for role in roles:
    msg=""
    roleId=role.strip('<').strip('>').strip('@').strip('&')
    try:
      r=ctx.guild.get_role(int(roleId))
      if r:
        role_ids.append(r)
        good_roles.append(role)
        #good
      else:
        msg+="Error finding: "+role+'\n'
    except:
      #error2, electric boogaloo
      msg+="Error finding: "+role+'\n'
  if msg:
    await ctx.send(msg+'continue anyways? (y/n)')
    
    try:
      msg = await client.wait_for('message', timeout=120.0,check=check) #set up message
    except asyncio.TimeoutError:
      await ctx.send('no response, aborting')#time out error
      return
    if not ('y'in msg.content or 'Y' in msg.content):
      await ctx.send('aborting event set up')
      return
  msg =""
  msg+="gotcha, I will notify:\n"
  for role in good_roles:
    msg+=role+'\n'
  msg += 'about: '+name+'\n'
  msg += 'right now, a day before, and an hour before ' +prettifyDate(event_datetime) +'\n'
  await ctx.send(msg+'does that sound good? (y/n)')

  try:
    msg = await client.wait_for('message', timeout=120.0,check=check) #set up message
  except asyncio.TimeoutError:
    await ctx.send('no response, aborting')#time out error
    return
  if not ('y'in msg.content or 'Y' in msg.content):
    await ctx.send('aborting event set up')
    return
  

  day_reminder = event_datetime-timedelta(days=1)
  hour_reminder = event_datetime-timedelta(hours=1)



  event_notif = name+' at '+prettifyDate(event_datetime)+' '
  day_notif=event_notif
  for role in good_roles:
    event_notif += role
  
  await channel.send(event_notif)
  
  data=[str(ctx.guild.id) +','+day_notif+','+ str(channel.id) +','+ str(day_reminder),str(ctx.guild.id) +','+event_notif+','+ str(channel.id) +','+ str(hour_reminder)] #gather all data to be stored
  #now to put it into a file
  #guildid,event_channelid,event_name,roles_to_ping
  # nth_reminder = str(ctx.guild.id)+','+
  file=open("reminders.txt","a")
  file.write('\n'+"\n".join(data))
  file.close()

def validateSyntax(args):
  try:
    at_index=len(args) - 1 - args[::-1].index('at')
    for_index=len(args) - 1 - args[::-1].index('for')
  except:
    return -1;
  name=' '.join(args[:at_index])
  date = args[at_index+1:for_index]
  roles = args[for_index+1:]
  return(name,date,roles)

def ValidateDate(date):
  print(date)
  MDY = date[0] #Month/Day/Year
  splitters=['-','/','\\','|']
  for split in splitters:
    test = MDY.split(split)
    print(test)
    if(len(test)==3):
      MDY=MDY.split(split)
      break
  if len(MDY)<3 and not type(MDY)==list:
    return -1

  HMT = date[1] #Hour Minute Timestamp
  if('pm'in HMT or 'am' in HMT):#We have a timestamp
    time_stamp=HMT[-2:]
    HM=HMT[:-2]
    timeStampDict={"pm":12,"am":0}
    hours = int(HM.split(':')[0])+timeStampDict[time_stamp]
    if(':' in HM):#if minutes exist
      minutes= int(HM.split(':')[1])
    else:
      minutes=0
  else:
    HM=HMT
    hours = int(HM.split(':')[0])
    if(':' in HM):#if minutes exist
      minutes= int(HM.split(':')[1])
    else:
      minutes=0
  
  try:
    return  datetime(int(MDY[2]),int(MDY[0]),int(MDY[1]),hours,minutes)
  except:
    return -2;
###runs every second, checks to see if any reminders need to be sent
###removes sent reminders from file
@tasks.loop(seconds=1)  
async def send_messages():

    file = open('reminders.txt','r')
    reminders = file.read().split('\n')
    file.close()

    sent_reminders = []

    for i in range(len(reminders)):
      try:
         data = reminders[i].split(',') #author id, reminder text, server id, channel id, time to send, Days;Hours;Minutes;Seconds
        
         time = data[3] #datetime stored as yyyy-mm-dd hh:mm:ss.ssssss

##         print(time)

         YMD = time.split(' ')[0].split('-') #year month and day

##         print(YMD)

         HMS = time.split(' ')[1].split(':') # hour minute and seconds

##         print(HMS)

         remind_time = datetime(int(YMD[0]),int(YMD[1]),int(YMD[2]),int(HMS[0]),int(HMS[1]),int(HMS[2]))#make date time for reminder time

         if datetime.today() >= remind_time:  #compare to see if its time to remind  
             for guild in client.guilds: #for every guild the bot is connected in
                 if guild.id == int(data[0]): #if the guild id matches
                     for channel in guild.channels: #look at all the channels in the guild
                         if channel.id == int(data[2]): #if the channel id matches
                             sent_reminders.append(i) #mark reminder for deletion
##                             print("data sent")
                             await channel.send(data[1]) #send the reminder

      except:
          pass
##         print(reminders[i])


    sent_reminders.reverse() #to not mess up order (pop list end to start)
    for i in sent_reminders:
     reminders.pop(i) #delete reminders

    file = open('reminders.txt','w') #write new list, excluding sent reminders
    file.write('\n'.join(reminders))
    file.close()




send_messages.start() ##start the loop



client.run(TOKEN);
