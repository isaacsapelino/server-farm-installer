'''
Installer.Py
A simple script for installing DHCP, NFS, LAMP, DNS FTP
for Debian-based distribution

Made by Isaac Sapelino
'''

import curses
import curses.textpad
import os
import subprocess
import sys
import crypt

menu = ['Install NFS', 'Exit Setup']

def print_menu(screen, selected_row):
	screen.clear()
	print_center(screen, 'Welcome to Installer.Py', 0, -9)
	print_center(screen, 'Made by Isaac', 0, -8)
	for i, row in enumerate(menu):
		h, w = screen.getmaxyx()
		x = w//2 - len(row)//2
		y = h//2 - len(menu)//2 + i
		if i == selected_row:
			screen.attron(curses.color_pair(1))
			screen.addstr(y,x,row)
			screen.attroff(curses.color_pair(1))
		else:
			screen.addstr(y,x,row)
	screen.refresh()
	return


def print_center(screen, text, x, y):
	h, w = screen.getmaxyx()
	x = w//2 - len(text)//2 + x
	y = h//2 + y
	screen.addstr(y,x,text)
	screen.refresh()
	return	

def create_textbox(screen, h, w, y, x, placeholder="", deco=None, textColorPair=0, decoColorPair=0):
	underlineChr=curses.ACS_HLINE
	new_win = curses.newwin(h,w,y,x)
	text_box = curses.textpad.Textbox(new_win)
	if deco == "frame":
		screen.attron(decoColorPair)
		curses.textpad.rectangle(screen,y-1,x-1,y+h,x+w)
		screen.attroff(decoColorPair)
	elif deco == "underline":
		screen.hline(y+1,x,underlineChr,w,decoColorPair)
		
	new_win.addstr(0,0,placeholder,textColorPair)
	new_win.attron(textColorPair)
	screen.refresh()
	return text_box
	
def create_user(screen, user, password):
	password = crypt.crypt(password, "22")
	os.system('clear')
	file = open('log_inst.txt', 'w')
	iUser = subprocess.run(['useradd', '-p', password, '-m','-s','/bin/bash', user], capture_output=True, text=True)
	file.write(iUser.stderr)
	file.close()
	if iUser.returncode != 0:
		return 1
	
	return 0		
	
def append_file(path, text):
	path = str(path.strip().strip('\n').strip('\t').strip('\''))
	try:
		f = open(path, 'a', encoding='utf-8')
		f.write(text)
	finally:
		f.close()
	return 0
	
def clean_str(text, flag):
	if flag == 'n':
		return str(text.strip().strip('\n').strip('\t').strip('\''))
	elif flag == 'o':
		return str(text.strip('\n').strip('\t').strip('\''))
	return 0
	
def create_dir(path):
	path = str(path.strip().strip('\n').strip('\t').strip('\''))
	directory = subprocess.run(['mkdir', '-p', path], capture_output=True, text=True)
	if directory.returncode != 0:
		return 1
	return 0

def check_package(screen, package):
	screen.clear()
	print_center(screen, 'Checking packages', 0, -9)	
	apt_get = subprocess.Popen('dpkg -l | grep' + ' ' + package, shell=True)
	apt_get.wait()
	return_code = apt_get.poll()
	if return_code == 1:
		apt_update = subprocess.Popen('apt update', shell=True)
		apt_update.wait()
		apt_install = subprocess.Popen('apt install' + ' ' + package, shell=True)
		apt_install.wait()
		if apt_install.poll() == 0:
			screen.clear()
			print_center(screen, package + ' ' + 'has been installed to the system.', 0,0)
			print_center(screen, 'Press any key to continue.', 0,1)
			screen.getch()
			return
		else:
			print_center(screen, 'Package has encountered a problem.', 0,0)
			screen.getch()
			return
	return

def exit_text_box(x):
	if x == 10:
		return 7
		
	return x

def nfs_install(screen):
	screen.clear()
	print_center(screen, 'NFS Setup', 0, -9)
	check_package(screen, 'nfs-kernel-server')
	screen.clear()
	curses.curs_set(1)
	print_center(screen, 'How many users do you want to create?', 0, -5)
	text = create_textbox(screen, 1, 40, 10, 20, deco="underline", decoColorPair=curses.color_pair(2))
	text_counter = text.edit()
	
	counter = 0
	while counter != int(text_counter):
		screen.clear()
		user = 0
		password = 0
			
		print_center(screen, 'Create a user', 0, -5)
		print_center(screen, 'User count: ' + str(counter), 0, 4)
		print_center(screen, 'Press Ctrl+G to exit', 0,6)
		text_box = create_textbox(screen, 1, 40, 10, 20, deco="underline", decoColorPair=curses.color_pair(2))
		user = text_box.edit(exit_text_box)
		if not user:
			return
		screen.clear()
		print_center(screen, "Create user's password", 0, -5)
		password_box = create_textbox(screen, 1, 40, 10, 20, deco="underline", decoColorPair=curses.color_pair(2))
		password = password_box.edit(exit_text_box)
		status = create_user(screen, clean_str(user, 'n'), clean_str(password, 'n'))
		counter += 1
		if status != 0:
			print_center(screen, 'Error: Account creation has an unexpected error.', 0, -5)
			screen.getch()
			return
	screen.clear()
	print_center(screen, 'Create an NFS export directory', 0, -5)
	text = create_textbox(screen, 1, 40, 10, 20, deco="underline", decoColorPair=curses.color_pair(2))
	text_input = text.edit()
	status = create_dir(text_input)
	if status != 0:
		screen.clear()
		print_center(screen, 'Error: Cannot create directory.', 0, -5)
		return
	screen.clear()
	own = subprocess.run(['chown', '-R', 'nobody:nogroup', clean_str(text_input, 'n')], capture_output=True, text=True)
	perm = subprocess.run(['chmod', '777', clean_str(text_input, 'n')], capture_output=True, text=True)
	screen.clear()
	print_center(screen, 'Enter NFS server access', 0, -5)
	text = create_textbox(screen, 1, 60, 10, 10, deco="underline", decoColorPair=curses.color_pair(2))
	nfs_access = text.edit()
	append_file('/etc/exports', clean_str(nfs_access, 'o'))
	screen.clear()
	print_center(screen, 'Enter subnet', 0, -5)
	text = create_textbox(screen, 1, 60, 10, 10, deco="underline", decoColorPair=curses.color_pair(2))
	subnet = clean_str(text.edit(), 'n')
	sub = subprocess.run(['ufw', 'allow', 'from', subnet, 'to', 'any', 'port', 'nfs'], capture_output=True, text=True)
	sub_enable = subprocess.run(['ufw', 'enable'], capture_output=True, text=True)
	screen.clear()
	print_center(screen, 'Setting up NFS Server.', 0, -5)
	run_e = subprocess.run(['exportfs', '-a'], capture_output=True, text=True)
	restart_daemon = subprocess.run(['systemctl', 'restart', 'nfs-kernel-server'], capture_output=True, text=True)
	
	if restart_daemon != 0:
		screen.clear()
		print_center(screen, 'An error has occured.', 0, -5)
		return 1
		
	screen.clear()
	print_center(screen, 'NFS has been installed successfully', 0, -5)
		
	curses.curs_set(0)
	return
	

def window(screen):
	screen.clear()
	curses.curs_set(0)
	screen.box()
	
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
	
	print_center(screen, 'Welcome to Installer.Py', 0, -9)
	print_center(screen, 'Made by Isaac', 0, -8)
	current_row = 0
	
	print_menu(screen, current_row)
	
	while True:
		key = screen.getch()
		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
		elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
			current_row += 1
		elif key == curses.KEY_ENTER or key in [10, 13]:
			if current_row == 0:
				nfs_install(screen)
			elif current_row == 1:
				break
			elif current_row == len(menu)-1:
				break
				
		print_menu(screen, current_row)

def main():
	curses.wrapper(window)

if __name__ == '__main__':
	main()