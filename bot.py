import os
import pickle
import time
import asyncio
from datetime import date
import datetime as dt

import discord
from discord.ext import commands,tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_ID2 = os.getenv('CHANNEL_ID2')

client = discord.Client()
channel = client.get_channel(CHANNEL_ID)
channel2 = client.get_channel(CHANNEL_ID2)

#Loading dictionary
fileName = "birthdays.txt"

def loadFile(fileName):
    inFile = open(fileName,"rb")
    try:
        birthdaysDict = pickle.load(inFile)
        if birthdaysDict == None:
            birthdaysDict = {}
    except:
        print("Couldn't load pickle file")
        birthdaysDict = {}
    print("Orginal birthday dictionary: ", birthdaysDict)
    inFile.close()
    return birthdaysDict

def leapYear(year): #Checks if leap year
    if (year % 4) == 0:  
        if (year % 100) == 0:  
            if (year % 400) == 0:  
                return True 
            else:  
                return False  
        else:  
            return True  
    else:  
        return False  

def checkMonth(date): #Checks for the maximum month date
    longMonth = ["01","03","05","07","08","10","12"]
    shortMonth = ["04","06","09","11"]
    leapMonth = ["02"]
    if date[:2] in leapMonth:
        isLeapYear = leapYear(int(date[6:10]))
        if isLeapYear == True:
            return 29
        else:
            return 28
    elif date[:2] in longMonth:
        return 31
    elif date[:2] in shortMonth:
        return 30
    else:
        return False

def getUserInfo(userInfo):
    newUserInfo = userInfo.split(",")
    userName = newUserInfo[0]
    userName = userName.strip()
    newUserInfo[1] = newUserInfo[1].replace(" ","")
    maxDate = checkMonth(newUserInfo[1]) #Gets max date
    if maxDate == False: #If max date isn't correct
        return False
    if len(newUserInfo[1]) != 10: #If user input isn't correct format
        return False
    elif newUserInfo[1][:2] < "01" or newUserInfo[1][:2] > "12": #If month isn't a correct month
        return False
    elif newUserInfo[1][3:5] < "1" or newUserInfo[1][3:5] > str(maxDate): #If date isn't a correct date
        return False
    elif newUserInfo[1][6:10] < "0": #if year isn't propper
        return False
    else:
        userBirthday = newUserInfo[1]
        userBirthday = userBirthday.strip()
        userBirthdayTest = userBirthday.replace("/","")
        if len(userBirthdayTest) != 8: #Checks if date is correct format
            return False
        try:
            checkUserBirthday = int(userBirthdayTest) #Checks if birthday only uses numbers
        except:
            return False
    return [userName,userBirthday]

def saveUserInfo(userInfo,addUser):
    if addUser == True: #To add a user
        if userInfo[0] in birthdaysDict:
            return False
        else:
            birthdaysDict[userInfo[0]] = userInfo[1]
    if addUser == False: #To delete a user
        if userInfo in birthdaysDict:
            birthdaysDict.pop(userInfo,None)
        else:
            print("User not in dictionary")

    outFile = open(fileName,"wb")
    pickle.dump(birthdaysDict,outFile)
    outFile.close()

def getDate():
    today = date.today()
    month = today.strftime("%m")
    day = today.strftime("%d")
    year = today.strftime("%y")
    combinedDate = month + "/" + day 
    print(combinedDate)
    return(combinedDate)

def checkDict(): #Checks if there is a birthday
    print("In checkDict")
    userNames = []
    birthdaysDict = loadFile(fileName)
    today = getDate()
    for keys in birthdaysDict:
        if birthdaysDict[keys][:5] == today:
            print("Birthday is found")
            userNames.append(keys)
            print(userNames)
    return userNames

def findUser(dictionary,user): #Finds user
    for key in dictionary:
        if user == key:
            return dictionary[key]
    return False

birthdaysDict = loadFile(fileName) #Get's dictionary

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    happyBirthday.start()

@client.event
async def on_message(message):
    id = client.get_guild(CHANNEL_ID)

    if message.content.startswith("-birthdayhelp"):
        await message.channel.send("To add a birthday in form xx/xx/xxxx" + "\n" + "-birthdayadd @user,month/day/year" + "\n" + "-bda @user,month/day/year")
        await message.channel.send("To delete a birthday" + "\n" + "-birthdaydelete @user" + "\n" + "-bdd @user")
        await message.channel.send("To find a birthday" + "\n" + "-birthdaylist @user" + "\n" + "bdl @user")
    
    elif message.content.startswith("-bdh"):
        await message.channel.send("To add a birthday in from xx/xx/xxxx" + "\n" + "-birthdayadd @user,month/day/year" + "\n" + "-bda @user,month/day/year")
        await message.channel.send("To delete a birthday" +"\n" + "-birthdaydelete @user" +"\n" + "-bdd @user")
        await message.channel.send("To find a birthday" + "\n" + "-birthdaylist @user" + "\n" + "-bdl @user")

    if message.content.startswith("-birthdayadd"):
        if message.content[13:] != "": #Makes sure user inoutted something
            userInput = message.content[13:]
            print(userInput)
            userInfo = getUserInfo(userInput)
            print (userInfo)
            if userInfo == False:
                await message.channel.send("Incorrect birthday format")
            else:
                saveUserInfo(userInfo, True)
                print (birthdaysDict)
                await message.channel.send("User Birthday Added: " + userInfo[0] + ", " + userInfo[1])
        else:
            await message.channel.send("Add a birthday by typing in '@user,month/date/year'")

    elif message.content.startswith("-bda"):
        if message.content[5:] != "": #Makes sure user inoutted something
            userInput = message.content[5:]
            print(userInput)
            userInfo = getUserInfo(userInput)
            print (userInfo)
            if userInfo == False:
                await message.channel.send("Incorrect birthday format")
            else:
                saveUserInfo(userInfo, True)
                print (birthdaysDict)
                await message.channel.send("User Birthday Added: " + userInfo[0] + ", " + userInfo[1])
        else:
            await message.channel.send("Add a birthday by typing in '@user,month/date/year'")
        
    if message.content.startswith("-birthdaydelete"):
        if message.content[16:] != "":
            userInput = message.content[16:]
            userName = userInput.strip()
            saveUserInfo(userName, False)
            print (birthdaysDict)
            await message.channel.send(userName + " Birthday Deleted")
        else:
            await message.channel.send("Delete a birthday by typing in '@user'")
    
    elif message.content.startswith("-bdd"):
        if message.content[5:] != "":
            userInput = message.content[5:]
            userName = userInput.strip()
            saveUserInfo(userName, False)
            print (birthdaysDict)
            await message.channel.send(userName + " Birthday Deleted")
        else:
            await message.channel.send("Delete a birthday by typing in '@user'")
    
    if message.content.startswith("-bdl"):
        if message.content[5:] != "":
            userInput = message.content[5:]
            userName = userInput.strip()
            birthday = findUser(birthdaysDict,userName)
            if birthday != False:
                await message.channel.send(userName + " Birthday is: " + birthday)
            else:
                await message.channel.send("User doesn't exist")
        else:
            await message.channel.send("Find a birthday by using '-bdl @user'")
             
    if message.content.startswith("-birthdaylist"):
        if message.content[14:] != "":
            userInput = message.content[14:]
            userName = userInput.strip()
            birthday = findUser(birthdaysDict,userName)
            if birthday != False:
                await message.channel.send(userName + " Birthday is: " + birthday)
            else:
                await message.channel.send("User doesn't exist")
        else:
            await message.channel.send("Find a birthday by using '-birthdaylist @user'")
            
@tasks.loop(hours=24)
async def happyBirthday():
    await client.wait_until_ready()
    channel2 = client.get_channel(int(CHANNEL_ID2))
    birthdays = checkDict()
    print("Here are the birthdays", birthdays)
    for user in birthdays:
        print(user)
        await channel2.send("Happy Birthday" + user + "!")

@happyBirthday.before_loop
async def before_happyBirthday():
    for i in range (60*60*24):
        if dt.datetime.now().hour == 12+10:
            print("it is time")
            return
        await asyncio.sleep(1)

client.run(TOKEN)