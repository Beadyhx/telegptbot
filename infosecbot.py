import config
from telebot.async_telebot import AsyncTeleBot
import json
import openai
import os
from os import listdir
from os.path import isfile, isdir, join
import uuid
import asyncio
import contexts

new_context_content = contexts.INFOSEC
bot_username = config.BOTNICKNAME

def list_contexts(message):
	'''This function prints all variables from contexts.py along with their corresponding
	numbers and lets the user assign a new value to one of the variables based on their choice.'''
	var_names = [i for i in dir(contexts) if not callable(getattr(contexts, i)) 
                 and not i.startswith("__")]  # get all variable names in contexts.py
	contextsmessage = []
	for idx, name in enumerate(var_names):
		contextsmessage.append(f"{idx + 1}. {name}"+'\n')
	return ''.join(contextsmessage)
    

def assign_context(message):
	var_names = [i for i in dir(contexts) if not callable(getattr(contexts, i)) 
                 and not i.startswith("__")]
	var_num = int(message.text.split(' ')[1])-1
	if var_num < 0 or var_num > len(var_names) - 1:  # handle invalid input
		print(f"{var_num + 1} is not a valid variable number.")
		return
	var_to_assign = var_names[var_num]
	try:
		new_value = input(f"Enter a new value for {var_to_assign}: ")
		setattr(config, var_to_assign, new_value)  # set new value for the chosen variable
		print(f"{var_to_assign} has been assigned a new value: {new_value}")
	except AttributeError:  # handle invalid attribute names
		print(f"{var_to_assign} is not a valid variable name.")
        

openai.api_key = config.OPENAIKEY
bot = AsyncTeleBot(config.TOKEN)

def sendcontext(user_id, context_id, user_message):
	file = open('users/{}/{}.txt'.format(user_id, context_id), 'r')
	context = json.load(file)
	file.close()
	user_message_to_append = json.dumps({ "role":"user", "content":user_message})
	context.append(json.loads(user_message_to_append))
	try:
		response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=context)
		# print('RESPONSE:',response)
		gptreply = response['choices'][0]['message']['content']
		gpt_message_to_append = json.dumps({ "role":"assistant", "content":gptreply})
		context.append(json.loads(gpt_message_to_append))
		# print('GPTREPLY:',gptreply)
		file = open('users/{}/{}.txt'.format(user_id, context_id), 'w')
		json.dump(context,file)
		file.close()
		return gptreply
	except Exception as err:
		gptreply = "Unexpected {}, {}".format(err,type(err))
		return gptreply

def checkuser(user_id, userinfo):
	folders = [d for d in listdir('users') if isdir(join('users', d))]
	# print(folders)
	if user_id in folders:
		pass
		# print('This user already in list')
	else:
		os.makedirs('users/{}'.format(user_id))
		with open('users/{}/userinfo.txt'.format(user_id),'w') as userfile:
			userfile.write(userinfo)
			# print(userinfo)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi!\
You can use following commands:\n\
/reset\n\
reset current conversation context\n\
/list\n\
list all conversations\n\
/new\n\
create new conversation\n\
/delete # or /remove #\n\
delete conversation\n\
/select #\n\
select conversation\n\
/show\n\
show available system prompt presets\n\
/use #\n\
use system preset\n\
""")

async def listconversations(message):
	user_id = str(message.chat.id)
	userfiles = [f for f in listdir('users/{}'.format(user_id)) if isfile(join('users/{}'.format(user_id), f))]
	# print(userfiles)
	responsemessage = []
	current_context = open('users/{}/currentcontext.txt'.format(user_id),'r')
	context_id = str(current_context.read().rstrip())
	current_context.close()
	nameandcontent = {}
	for filename in userfiles:
		
		if filename != 'currentcontext.txt' and filename != 'userinfo.txt' and filename != '{}.txt'.format(context_id):
			# print(filename)
			file = open('users/{}/{}'.format(user_id, filename))
			context = json.load(file)
			if len(context) == 1:
				nameandcontent[filename] = 'Blank conversation'+'\n'
				file.close()
			elif len(context) > 1:
				nameandcontent[filename] = context[1]['content']+'\n'
				file.close()
			else:
				nameandcontent[filename] = 'Error happened, send me screenshot @peka_boyarin'
				file.close()
		elif filename == '{}.txt'.format(context_id):
			file = open('users/{}/{}'.format(user_id, filename))
			context = json.load(file)
			if len(context) == 1:
				nameandcontent[filename] = 'Blank conversation'+' [X]'+'\n'
				file.close()
			elif len(context) > 1:
				nameandcontent[filename] = context[1]['content']+' [X]'+'\n'
				file.close()
			else:
				nameandcontent[filename] ='Error happened, send me screenshot @peka_boyarin'
				file.close()
	enumcontent = list(enumerate(nameandcontent, start = 1))
	y=0
	for x in nameandcontent:
		responsemessage.append(str(enumcontent[y][0])+'. ')
		if len(nameandcontent[x]) > 25:
			responsemessage.append(nameandcontent[x][0:24]+'... '+nameandcontent[x][-4:-1]+'\n')
		elif len(nameandcontent[x]) <= 25:
			responsemessage.append(nameandcontent[x])
		y+=1
	# print(enumcontent)
	# print(nameandcontent)
	# await bot.reply_to(message,'You have {} conversations.'.format(len(nameandcontent))+'\n'+'\n'+''.join(responsemessage))
	return enumcontent, nameandcontent, responsemessage

@bot.message_handler(commands=['delete','remove'])
async def delete_context(message):
	# print('Listing conversations...')
	enumcontent, nameandcontent, null = await listconversations(message)
	# print(enumcontent)
	# print(message.text)
	try:
		deletenum = int(message.text.split(' ')[1])-1
	except:
		deletenum = 'error'
	if isinstance(deletenum, int) == True:
		user_id = str(message.chat.id)
		
		# print('context_id:',context_id)
		try:
			if deletenum in range(0,len(nameandcontent)):
				context_id = enumcontent[deletenum][1]
				# print(deletenum)
				# print(enumcontent[deletenum],nameandcontent[enumcontent[deletenum][1]]+' will be deleted')
				if deletenum == 0:
					if len(nameandcontent) == 1:
						context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
						context_file.write(new_context_content)
						context_file.close()
					elif len(nameandcontent) > 1:
						# print('we are here at one')
						os.remove('users/{}/{}'.format(user_id,context_id))
						new_context_id = enumcontent[deletenum+1][1].split('.')[0]
						# print('new_context_id',new_context_id)
						current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
						current_context.write(str(new_context_id))
						current_context.close()
						# await listconversations(message)
						# записать его в currentcontext.txt
				elif deletenum > 0:
					# print('we are here at two')
					os.remove('users/{}/{}'.format(user_id,context_id))
					new_context_id = enumcontent[deletenum-1][1].split('.')[0]
					# print('new_context_id',new_context_id)
					current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
					current_context.write(str(new_context_id))
					current_context.close()
					# await listconversations(message)
					pass			
			else:
				await bot.reply_to(message, """# of conversation to delete must be from 1 to {}""".format(len(nameandcontent)))
		except:
			await bot.reply_to(message, """Some error during conversation delete. Make shure your message was like /delete # where # is number of conversation to delete and number you want to delete is in bounds""")
	else:
		await bot.reply_to(message, """# of conversation to delete must be instance, not {}""".format(type(deletenum)))
	null, nameandcontent, responsemessage = await listconversations(message)
	await bot.reply_to(message,'You have {} conversations.'.format(len(nameandcontent))+'\n'+'\n'+''.join(responsemessage))

@bot.message_handler(commands=['list'])
async def list_conversations(message):
	# print('Listing conversations...')
	enumcontent, nameandcontent, responsemessage = await listconversations(message)
	await bot.reply_to(message,'You have {} conversations.'.format(len(nameandcontent))+'\n'+'\n'+''.join(responsemessage))

@bot.message_handler(commands=['select'])
async def select_context(message):
	try:
		selectnum = int(message.text.split(' ')[1])-1
	except:
		selectnum = 'error'
	enumcontent, nameandcontent, null = await listconversations(message)
	if isinstance(selectnum, int) == True:
		user_id = str(message.chat.id)
		try:
			if selectnum in range(0,len(nameandcontent)):
				context_id = enumcontent[selectnum][1].split('.')[0]
				current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
				current_context.write(str(context_id))
				current_context.close()
				null, nameandcontent, responsemessage = await listconversations(message)
				await bot.reply_to(message,'Conversation {} selected'.format(selectnum+1)+'\n\n'+''.join(responsemessage))
			else:
				await bot.reply_to(message, """# of conversation to select must be from 1 to {}""".format(len(nameandcontent)))
		except:
			await bot.reply_to(message, """Some error during conversation selection. Send me screenshot @peka_boyarin""")
	else:
		await bot.reply_to(message, """# of conversation to select must be instance, not {}""".format(type(selectnum)))

@bot.message_handler(commands=['reset'])
async def reset_context(message):
	user_id = str(message.chat.id)
	current_context = open('users/{}/currentcontext.txt'.format(user_id),'r')
	context_id = current_context.read()
	current_context.close()
	context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
	context_file.write(new_context_content)
	context_file.close()
	await bot.reply_to(message, """Conversation context has been reset!""")

@bot.message_handler(commands=['new'])
async def reset_context(message):
	user_id = str(message.chat.id)
	context_id = uuid.uuid4()
	current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
	current_context.write(str(context_id))
	current_context.close()
	context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
	context_file.write(new_context_content)
	context_file.close()
	await bot.reply_to(message, """Conversation context has been reset, previous conversation saved. Use /list command to check your conversations!""")
    
@bot.message_handler(commands=['show'])
async def show_contexts(message):
	contextsmessage = list_contexts(message)
	await bot.reply_to(message,'You can select any of following prompts presets, try /use # command:'+'\n'+'\n'+''.join(contextsmessage))

@bot.message_handler(commands=['use'])
async def use_context(message):
	user_id = str(message.chat.id)
	current_context = open('users/{}/currentcontext.txt'.format(user_id),'r')
	context_id = current_context.read()
	current_context.close()
	contextsmessage = list_contexts(message)
	var_names = [i for i in dir(contexts) if not callable(getattr(contexts, i)) and not i.startswith("__")]  # get all variable names in contexts.py
	print("Variables in contexts.py:")
	for idx, name in enumerate(var_names):
		print(f"{idx + 1}. {name}")  # print variable names with corresponding numbers
	var_num = int(message.text.split(' ')[1])-1
	if var_num < 0 or var_num > len(var_names) - 1:  # handle invalid input
		responsemessage = (f"{var_num + 1} is not a valid variable number.")
		await bot.reply_to(message, responsemessage)
	var_to_assign = var_names[var_num]
	new_value = getattr(contexts, var_to_assign)  # get value of the chosen variable
	responsemessage = f"{var_to_assign} was selected"
	context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
	context_file.write(new_value)
	context_file.close()
	await bot.reply_to(message, responsemessage)


@bot.message_handler(func=lambda message: True)
async def chatgpt_reply(message):
	userinfo = str(message.chat)
	user_id = str(message.chat.id)
	checkuser(user_id, userinfo)
	userfiles = [f for f in listdir('users/{}'.format(user_id)) if isfile(join('users/{}'.format(user_id), f))]
	print('USER_ID:',user_id)
	
	if user_id[0] == '-' and bot_username in message.text:
		print(message.text)
		if 'currentcontext.txt' in userfiles:
			current_context = open('users/{}/currentcontext.txt'.format(user_id),'r')
			context_id = str(current_context.read().rstrip())
			# print('currentcontext.txt exist, currentcontext is',context_id)
			current_context.close()
		else:
			# print('There is no file with currentcontext, creating one...')
			context_id = uuid.uuid4()
			current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
			current_context.write(str(context_id))
			current_context.close()
			context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
			context_file.write(new_context_content)
			context_file.close()
		gptreply = sendcontext(user_id, context_id, message.text)
		print(gptreply)
		await bot.reply_to(message, gptreply)
	elif user_id[0] == '-':
		pass
	else:
		if 'currentcontext.txt' in userfiles:
			current_context = open('users/{}/currentcontext.txt'.format(user_id),'r')
			context_id = str(current_context.read().rstrip())
			current_context.close()
		else:
			context_id = uuid.uuid4()
			current_context = open('users/{}/currentcontext.txt'.format(user_id),'w')
			current_context.write(str(context_id))
			current_context.close()
			context_file = open('users/{}/{}.txt'.format(user_id, str(context_id)),'w')
			context_file.write(new_context_content)
			context_file.close()
		gptreply = sendcontext(user_id, context_id, message.text)
		await bot.reply_to(message, gptreply)



	

asyncio.run(bot.polling())