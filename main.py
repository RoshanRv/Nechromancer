import pygame
from pygame import mixer
import os
import random
import csv
import button
import ctypes


pygame.init()
mixer.init()
clock = pygame.time.Clock()
FPS = 90

#Window
user32 = ctypes.windll.user32 
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)
screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption("")

#game variable
move_left = False
move_right= False
GRAVITY = 0.75
shoot = False
ROWS =16
COLS = 150
level =1
TILE_SIZE = HEIGHT//ROWS
TILE_TYPES =21
scroll=0
SCROLL_THRES =300
screen_scroll=0
bg_scroll=0
start_game = False
MAX_LEVEL = 2

#load music
jump_fx =pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shoot_fx = pygame.mixer.Sound('audio/shot.wav')
shoot_fx.set_volume(0.5)
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0,5000)





#load img
start_btn= pygame.image.load('Resouces/start_btn.png').convert_alpha()
quit_btn= pygame.image.load('Resouces/exit_btn.png').convert_alpha()
restart_btn= pygame.image.load('Resouces/restart_btn.png').convert_alpha()

pine1_img= pygame.image.load('Resouces/BG/bg6.png').convert_alpha()
pine2_img= pygame.image.load('Resouces/BG/bg7.png').convert_alpha()
mountain_img= pygame.image.load('Resouces/BG/bg1.png').convert_alpha()
mountain1_img= pygame.image.load('Resouces/BG/bg2.png').convert_alpha()
mountain2_img= pygame.image.load('Resouces/BG/bg3.png').convert_alpha()
mountain3_img= pygame.image.load('Resouces/BG/bg4.png').convert_alpha()
mountain4_img= pygame.image.load('Resouces/BG/bg5.png').convert_alpha()



mountain_img=pygame.transform.scale(mountain_img , (700,195))
sky_cloud_img= pygame.image.load('Resouces/BG/bg.png').convert_alpha()
star_img= pygame.image.load('Resouces/BG/bg_star.png').convert_alpha()

sky_cloud_img=pygame.transform.scale(sky_cloud_img , (700,HEIGHT))




img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'Resouces/Tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img , (TILE_SIZE,TILE_SIZE))
	img_list.append(img)



bullet_img = pygame.image.load('Resouces/Icon/bullet.png').convert_alpha()
ammo_box_img = pygame.image.load('Resouces/Icon/ammo_box.png').convert_alpha()
health_box_img = pygame.image.load('Resouces/Icon/health_box.png').convert_alpha()

item_list = {
	
	'health' : health_box_img,
	'ammo' : ammo_box_img

}




white = (255,255,255)
red = (255,0,0)
green =(0,255,0)
black = (0,0,0)

font = pygame.font.SysFont('Times New Roman',30)

def draw_text(text,font,text_col,x,y):
	img = font.render(text,True,text_col)
	screen.blit(img ,(x,y))

def draw_bg():
	screen.fill(white)
	wid = pine1_img.get_width()

	for x in range(20):
		screen.blit(sky_cloud_img,((x*wid)-scroll *0.5,0))
		screen.blit(star_img,((x*wid)-scroll *0.6,HEIGHT - star_img.get_height() - 360))
		screen.blit(mountain_img,((x*wid)-scroll *0.6,HEIGHT - mountain_img.get_height() - 310))
		screen.blit(mountain1_img,((x*wid )-scroll *0.7,HEIGHT - mountain1_img.get_height() - 280))
		screen.blit(mountain2_img,((x*wid )-scroll *0.8,HEIGHT - mountain2_img.get_height() - 230))
		screen.blit(mountain4_img,((x*wid )-scroll *0.9,HEIGHT - mountain4_img.get_height() - 190))
		screen.blit(pine1_img,((x*wid)-scroll *0.9,HEIGHT - pine1_img.get_height() - 160))
		screen.blit(pine2_img,((x*wid)-scroll *1,HEIGHT - pine2_img.get_height() - 130))


def restart_lvl():
	enemy_group.empty()
	decoration_group.empty()
	bullet_group.empty()
	water_group.empty()
	item_group.empty()
	exit_group.empty()

	data=[]
	for row in range(ROWS):
		r = [-1]*COLS
		data.append(r)


	return data



class Soldier(pygame.sprite.Sprite):
	def __init__(self,x,y,PLAYER_SIZE,speed,char_type,ammo):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.speed = speed
		self.flip = False
		self.direction =1
		self.animation_list = []
		self.frame_index = 0
		self.update_time = pygame.time.get_ticks()
		self.action = 0
		self.jump = False
		self.in_air = True
		self.vel_y=0
		self.shoot_cooldown = 0
		self.ammo = ammo
		self.start_ammo = ammo
		self.health =100
		self.max_health = self.health
		#AI
		self.move_counter=0
		self.idling = False
		self.idling_counter =0
		self.vision = pygame.Rect(0,0,320,20)
		animation_types = ['Idle', 'Run' , 'Jump' , 'Dead']
		for animation in animation_types:
			temp_list=[]
			num_of_frames = len(os.listdir(f'Resouces/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img = pygame.image.load(f'Resouces/{self.char_type}/{animation}/{i}.png')
				img = pygame.transform.scale(img,(img.get_width()*PLAYER_SIZE,img.get_height()*PLAYER_SIZE)).convert_alpha()
				temp_list.append(img)
			self.animation_list.append(temp_list)
		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center=(x,y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()


	def update_action(self,new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def shoot(self):
		if self.shoot_cooldown==0 and self.ammo > 0:
			self.shoot_cooldown = 40
			bullet = Bullet(self.rect.centerx + (0.8 *self.rect.size[0] * self.direction) , self.rect.centery , self.direction)
			bullet_group.add(bullet)
			self.ammo -=1
			shoot_fx.play()

		

	def update(self):
		self.check_alive()
		self.update_animation()
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -=1

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1,200)==1:
				self.update_action(0)
				self.idling = True
				self.idling_counter=50
			if self.vision.colliderect(player.rect):
				self.update_action(0)
				self.shoot()
			else:
				if self.idling == False: 
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right=False
					ai_moving_left  = not ai_moving_right
					self.move(ai_moving_left,ai_moving_right)
					self.update_action(1)
					self.move_counter +=1
					self.vision.center = (self.rect.centerx + 165 *self.direction , self.rect.centery-20)
					#pygame.draw.rect(screen,red,self.vision,1)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter*=-1
				else:
					self.idling_counter-=1
					if self.idling_counter <=0:
						self.idling = False


		#scroll
		self.rect.x += screen_scroll

	def move(self,move_left,move_right):
		screen_scroll=0
		dy=0
		dx=0
		if player.alive:
			if move_right :
				dx = self.speed
				self.flip = False
				self.direction =1

				

			if move_left:
				dx = -self.speed
				self.flip = True
				self.direction = -1
				

			if self.jump==True and self.in_air==False:
				self.vel_y = -13
				#self.jump = False
				self.in_air=True

			self.vel_y +=GRAVITY
			if self.vel_y >10:
				self.vel_y

			dy +=self.vel_y 


			#collision with water
			if pygame.sprite.spritecollide(self,water_group,False):
				self.health = 0

			#collision with nxt lvl
			level_complete = False
			if pygame.sprite.spritecollide(self,exit_group,False):
				level_complete = True


			#out of world
			if self.rect.bottom > HEIGHT:
				self.health=0

			#check Collision
			for tile in world.obstacle_list:
				#check collision in x direction
				if tile[1].colliderect(self.rect.x+dx , self.rect.y , self.width , self.height):
					dx=0
					#for ai to change direction if they collide with block
					if self.char_type =='enemy':
						self.direction *=-1
						self.move_counter = 0
				#check collision in y direction
				if tile[1].colliderect(self.rect.x , self.rect.y+dy , self.width , self.height):
					#check below ground i.e : jumping
					if self.vel_y <0:
						self.vel_y=0
						dy= tile[1].bottom - self.rect.top
					#check above ground i.e : falling
					elif self.vel_y >=0:
						self.vel_y=0
						self.in_air = False
						dy= tile[1].top - self.rect.bottom


			if self.char_type == 'player':
				if self.rect.left + dx < 0 or self.rect.right+dx > WIDTH:
					dx = 0
			

			self.rect.x += dx
			self.rect.y +=dy

			if self.char_type == 'player':
				if (self.rect.right > WIDTH - SCROLL_THRES and scroll <(world.level_length*TILE_SIZE)- WIDTH)\
				 or (self.rect.left <	SCROLL_THRES and bg_scroll > abs(dx)):
					self.rect.x -=dx
					screen_scroll = -dx

			return screen_scroll, level_complete


	def update_animation(self):
		ANIMATION_COOLDOWN = 80

		self.image = self.animation_list[self.action][self.frame_index]


		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index+=1

		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action ==3:
				self.frame_index = len(self.animation_list[self.action])- 1
			else:
				self.frame_index = 0

	def check_alive(self):

		if self.health <= 0:
			self.health=0
			self.speed=0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self,data):
		self.level_length = len(data[0])
		for y,row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >=0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x*TILE_SIZE
					img_rect.y = y*TILE_SIZE
					tile_data = (img,img_rect)
					if tile >= 0 and tile <=8:
						self.obstacle_list.append(tile_data)
					elif tile >=9 and tile <=10:
						water = Water(img,x*TILE_SIZE,y*TILE_SIZE)
						water_group.add(water)
					elif tile >=11 and tile <=14:
						decoration = Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
						decoration_group.add(decoration)
					elif tile ==15:
						player = Soldier(x*TILE_SIZE,y*TILE_SIZE,1,5,'player',15)
						health_bar = HealthBar(10,10,player.health,player.max_health)
					elif tile ==16:
						enemy = Soldier(x*TILE_SIZE,y*TILE_SIZE,1,3,'Enemy',100)
						enemy_group.add(enemy)
					elif tile ==17:#ammo_box
						item= ItemBox(x*TILE_SIZE,y*TILE_SIZE,'ammo')
						item_group.add(item)
					elif tile ==18:#grenade_box
						pass
					elif tile ==19:#health_box
						item= ItemBox(x*TILE_SIZE,y*TILE_SIZE,'health')
						item_group.add(item)
					elif tile==20:
						exit = Exit(img,x*TILE_SIZE,y*TILE_SIZE)
						exit_group.add(exit)

		return player,health_bar
	def draw(self):

		for tile in self.obstacle_list:
			tile[1][0] +=screen_scroll
			screen.blit(tile[0],tile[1])

class Decoration(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2,y+(TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2,y+(TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2,y+(TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
	def __init__(self,x,y,item_type):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_list[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE//2,y+(TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self,player):
			if self.item_type == 'health' :
				player.health +=25
				if player.health > player.max_health:
					player.health = player.max_health
			if self.item_type == 'ammo':
				player.ammo +=10

			self.kill()

class HealthBar():
	def __init__(self,x,y,health,max_health):
		self.x = x
		self.y = y
		self.health =health
		self.max_health =max_health

	def draw(self,health):
		self.health = health
		ratio = player.health/player.max_health
		pygame.draw.rect(screen,white,(self.x-2,self.y-2,150+4,20+4))
		pygame.draw.rect(screen,red,(self.x,self.y,150,20))
		pygame.draw.rect(screen,green,(self.x,self.y,150*ratio,20))

		

class Bullet(pygame.sprite.Sprite):
	def __init__(self,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 5
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)
		self.direction = direction

	def update(self):
		self.rect.x += (self.direction * self.speed)+screen_scroll
		if self.rect.right < 0 or self.rect.left > WIDTH :
			self.kill()

		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		if pygame.sprite.spritecollide(player,bullet_group,False):
			if player.alive:
				player.health -=5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy,bullet_group,False):
				if enemy.alive:
					enemy.health -=25
					self.kill()

class ScreenFade():
	def __init__(self,direction,colour,speed):
		self.direction =direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_completed = False
		self.fade_counter += self.speed
		pygame.draw.rect(screen,self.colour,(0,0,WIDTH,0+self.fade_counter))
		if self.fade_counter >= HEIGHT:
			fade_completed = True


		return fade_completed	



#creating fades
death_fade =ScreenFade(2,red,6)
complete_fade=ScreenFade(2,red,10)


#creating buton
start_button = button.Button(WIDTH//2-130,HEIGHT//2+180,start_btn,0.7)	
exit_button = button.Button(WIDTH//2-115,HEIGHT//2+280,quit_btn,0.7)	
restart_button = button.Button(WIDTH//2-135,HEIGHT//2+180,restart_btn,2)	



#group
item_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
decoration_group=pygame.sprite.Group()
water_group=pygame.sprite.Group()
exit_group=pygame.sprite.Group()



#load image
world_data = []
for row in range(ROWS):
	r = [-1]*COLS
	world_data.append(r)


with open(f'level{level}_data.csv', newline='')as csvfile:
	reader =csv.reader(csvfile,delimiter=',')
	for x,row in enumerate(reader):
		for y,tile in enumerate(row):
			world_data[x][y]=int(tile)

world = World()
player,health_bar = world.process_data(world_data)

run = True
while ( run):
	clock.tick(FPS)
	if start_game == False:
		strt = pygame.image.load('Resouces/strt.png')
		strt = pygame.transform.scale(strt,(WIDTH,HEIGHT))
		screen.blit(strt,(0,0))

		if start_button.draw(screen):
			start_game = True
		if exit_button.draw(screen):
			run = False
	else:
		draw_bg()
		world.draw()
		draw_text(f'Ammo : {player.ammo}',font,white,10,35)
		player.draw()

		player.update()

		for enemy in enemy_group:
			enemy.ai()
			enemy.draw()
			enemy.update()

		bullet_group.update()
		bullet_group.draw(screen)

		item_group.draw(screen)
		item_group.update()

		health_bar.draw(player.health)

		decoration_group.update()
		decoration_group.draw(screen)

		water_group.update()
		water_group.draw(screen)

		exit_group.update()
		exit_group.draw(screen)





		if player.alive :
			if shoot:
				player.shoot()
				
			if player.in_air ==True :
				player.update_action(2)
			elif move_right or move_left:
				player.update_action(1)		
			else:
				player.update_action(0)
			screen_scroll , level_complete = player.move(move_left,move_right)
			scroll -= screen_scroll
			if level_complete:
				level+=1
				scroll = 0
				
				if 	level <= MAX_LEVEL:
					world_data=restart_lvl()
					with open(f'level{level}_data.csv', newline='')as csvfile:
						reader =csv.reader(csvfile,delimiter=',')
						for x,row in enumerate(reader):
							for y,tile in enumerate(row):
								world_data[x][y]=int(tile)
					world = World()
					player,health_bar = world.process_data(world_data)
				else:
					player.speed = 0
					player.vel_y = 0
					scroll=0
					comp = pygame.image.load('Resouces/glow.png')
					comp = pygame.transform.scale(comp,(WIDTH,HEIGHT))
					screen.blit(comp,(0,0))

					if exit_button.draw(screen):
						run = False


		else:

			screen_scroll = 0
			if death_fade.fade():
				screen.blit(strt,(0,0))

				if restart_button.draw(screen):
					scroll = 0
					world_data=restart_lvl()
					death_fade.fade_counter = 0
					with open(f'level{level}_data.csv', newline='')as csvfile:
						reader =csv.reader(csvfile,delimiter=',')
						for x,row in enumerate(reader):
							for y,tile in enumerate(row):
								world_data[x][y]=int(tile)
					world = World()
					player,health_bar = world.process_data(world_data)
					
				if exit_button.draw(screen):
					run = False
		


	#QUIT
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		#Movement
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a and pygame.K_LEFT:
				move_left = True
			if event.key == pygame.K_d:
				move_right = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_LCTRL:
				shoot = True
			if event.key == pygame.K_ESCAPE:
				if start_game == True:
					start_game = False 
				else:
					start_game = True



		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				move_left = False
			if event.key == pygame.K_d:
				move_right = False
			if event.key == pygame.K_w and player.alive:
				player.jump = False
			if event.key == pygame.K_LCTRL:
				shoot = False
			



	pygame.display.update()


pygame.quit()
