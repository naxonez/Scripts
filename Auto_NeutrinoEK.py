#!/usr/bin/env python
# coding=utf8

#Special thanks to morbith for patience and help

"""
Auto_NeutrinoEK.py

Herramienta para extraer el JSON de forma automática los flash hechos con el EK Neutrino
"""

import os
import subprocess
import magic
import re
import sys
import shutil

def exec_process(cmdline, silent, input=None, **kwargs):
	try:
		sub = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
		stdout, stderr = sub.communicate(input=input)
		if not silent :
			if stderr:
				print "Error en el comando %s" % cmdline
				print stderr
				sys.exit()
			print stdout

	except OSError as e:
		if e.errno == 2:
			raise RuntimeError('"%s" no está presente en el sistema' % cmdline[0])
		sys.exit()

def decrypt_rc4(param1,param2):
    if isinstance(param1,bytearray):
        if isinstance(param2,bytearray):
            if len(param1) > len(param2):
                key  = param2
                data = param1
            else:
                key  = param1
                data = param2
        else:
             if isinstance(param2,str):
                  key = param2
                  data = param1
             else:
                  print "[*] Error, param2 is not a valid input"
                  sys.exit()
    else:
        if isinstance(param1,str):
              if isinstance(param2,bytearray):
                  key  = param1
                  data = param2
              else:
                  if len(param1) > len(param2):
                      key  = param2
                      data = param1
                  else:
                      key  = param1
                      data = param2
        else:
            print "[*] Error, param1 is not a valid input"
            sys.exit()

    temp_ba1 = bytearray()
    temp_ba2 = bytearray()

    temp_1 = 0
    while(temp_1 < 256):
        temp_ba1.append(temp_1)
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    while(temp_1 < 256):
        if isinstance(key,str):
             temp_2 = temp_2 + temp_ba1[temp_1] + ord(key[temp_1 % len(key)]) & 255
        else:
             temp_2 = temp_2 + temp_ba1[temp_1] + key[temp_1 % len(key)] & 255

        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_1 += 1

    temp_1 = 0
    temp_2 = 0
    temp_4 = 0

    while(temp_4 < len(data)):
        temp_1 = temp_1 + 1 & 255
        temp_2 = temp_2 + temp_ba1[temp_1] & 255
        temp_3 = temp_ba1[temp_1]
        temp_ba1[temp_1] = temp_ba1[temp_2]
        temp_ba1[temp_2] = temp_3
        temp_ba2.append(data[temp_4] ^ temp_ba1[temp_ba1[temp_1] + temp_ba1[temp_2] & 255])
        temp_4 += 1

    return temp_ba2

def decrypt_json(json_file, passwd):
	file = open(json_file, "rb")
	rawdata = file.read()
	offset = int(rawdata[:3],16)
	param1 = bytearray(rawdata[3:][:offset])
	data = decrypt_rc4(param1, passwd)
	return data


def main(argv,results,scripts_path,ffdec_bin):

	flash_in     = "decrypt.swf"
	flash_out    = "decryptvalid.swf"
	output_path  = scripts_path.split("/")[0]+"/"

	if not os.path.exists(results):
		os.makedirs(results)

	#Limpiamos Output
	shutil.rmtree(output_path, ignore_errors=True)

	#Volcamos BinaryData
	export_bins = [ffdec_bin,'-export','binaryData',output_path,sys.argv[1]]
	exec_process(export_bins, True, input=None)

	#Volcamos el action script
	get_sctipts = [ffdec_bin,'-format','script:text:plain','-export','script',output_path,sys.argv[1]]
	exec_process(get_sctipts, True, input=None)

	action_scripts = [f for f in os.listdir(scripts_path) if os.path.isfile(os.path.join(scripts_path, f))]

	pattern = re.compile("_loc\\d{1,3}_ = this.")
	keyscript = ''

	for script in action_scripts:
		lines = open(scripts_path+script).readlines()
		for line in lines:
			match = pattern.search(line)
			if match:
				keyvar    = (line.split("(")[1]).split(",")[0]
				keyscript = script
				break
		if match:
			break

	if keyscript != '':
		pattern = re.compile(keyvar+':ByteArray = new ')
		lines = open(scripts_path+keyscript).readlines()
		for line in lines:
			match = pattern.search(line)
			if match:
				rc4Key = (line.split("(")[0]).strip().split(" ")[4]
				break
	else:
		print "[*] Error, no hemos encontrado el fichero con la clave RC4"
		sys.exit()

	#JSON
	jsonvar = ''
	pattern = re.compile(".et\(")
	for line in lines:
		match = pattern.search(line)
		if match:
			jsonvar = (line.split("(")[1]).split(")")[0]
			break
	if jsonvar != '':
		pattern = re.compile(jsonvar+':ByteArray = new')
		for line in lines:
			match = pattern.search(line)
			if match:
				json = (line.split("(")[0]).strip().split(" ")[4]
				break
	else:
		print "[*] Error, no hemos encontrado el fichero con el json"
		sys.exit()

	#Obtenemos el Flash interior
	flash_combo = []
	pattern = re.compile("writeBytes\(new")
	for line in lines:
		match = pattern.search(line)
		if match:
			flash_combo.append((line.split("(")[1]).split(" ")[1])


	bin_files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]

	flash_combo_files = {}
	for bin_file in bin_files:
		if rc4Key in bin_file:
			rc4keyfile = bin_file
		if json in bin_file:
			jsonfile = bin_file
		try:
			index = flash_combo.index(bin_file.split('.')[1])
			flash_combo_files[index] = bin_file
		except:
			pass

	#Juntamos Flash Dividido
	flash_data  = bytearray()
	for file_part, value in flash_combo_files.iteritems():
		for byte in bytearray(open(output_path + value,"rb").read()):
			flash_data.append(byte)

	#Hacemos rc4 del flash combinado
	print "[*] Decrypt del flash interno ..."
	k = bytearray(open(output_path + rc4keyfile).read())

	data = decrypt_rc4(k , flash_data )
	f = open(output_path+flash_in, "wb")
	f.write(data)
	f.close()

	#Comprobamos el flash extraido
	if magic.from_file(output_path+flash_in,mime=True) == 'application/octet-stream':
		#Corregimos identificadores inválidos del flash resultante
		invalid_ident = [ffdec_bin,'-renameInvalidIdentifiers','typeNumber',output_path+flash_in,output_path+flash_out]
		exec_process(invalid_ident, True, input=None)

		#Obtenemos el action script del nuevo flash
		export_scripts = [ffdec_bin,'-format','script:text:plain','-export','script',output_path,output_path+flash_out]
		exec_process(export_scripts, True, input=None)
	else:
		print sys.argv[1] + " no es un fichero flash válido"
		sys.exit()

	print "[*] Extract JSON"

	#Buscamos la key rc4 del json
	action_scripts = [f for f in os.listdir(scripts_path) if os.path.isfile(os.path.join(scripts_path, f))]

	pattern = re.compile("this\.var_\\d{1,3} = \"")

	for script in action_scripts:
		lines = open(scripts_path+script).readlines()
		for line in lines:
			match = pattern.search(line)
			if match:
				jsonkey    = line.split("\"")[1]
				break
		if match:
			break

	#Hacemos decrypt con la key obtenida
	print "[*] Decrypt with key: %s " % jsonkey
	data = decrypt_json(output_path + jsonfile,jsonkey)

	#Mostramos por pantalla
	print "[*] JSON in clear Text"
	print data

	#Guardamos Fichero

	parts = sys.argv[1].split("/")
	if len(parts) > 1:
			output = parts[len(parts)-1]
	else:
		output = sys.argv[1]

	f = open(results+output+"-decrypted.json", "wb")
 	f.write(data)
	f.close()

if __name__ == '__main__':

	ffdec_bin    = "ffdec"
	scripts_path = "Output/scripts/"
	results      = "Results/"

	try:

		if magic.from_file(sys.argv[1],mime=True) == 'application/octet-stream':
			print "[*] Procesando fichero %s" % sys.argv[1]
			main(sys.argv,results,scripts_path, ffdec_bin)
		else:
			print sys.argv[1] + " no es un fichero flash válido"
	except:
		print "Uso : %s fichero.swf" % sys.argv[0]
