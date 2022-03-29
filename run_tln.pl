#-----------------------------------------------------------
# run_tln
# Get contents of Run key from NTUSER.DAT and SOFTWARE hive
#
# Change History
#   20220329 - Added TLN Style and Merge user_run & soft_run (@NaxoneZ)
#
#-----------------------------------------------------------
package run_tln;
use strict;

my %config = (hive          => "NTUSER\.DAT", "SOFTWARE",
              osmask        => 22,
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 1,
              version       => 20220329);

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	my @run = ("Software\\Microsoft\\Windows\\CurrentVersion\\Run",
	           "Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
	           "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
	           "Software\\Microsoft\\Windows\\CurrentVersion\\RunServices",
	           "Software\\Microsoft\\Windows\\CurrentVersion\\RunServicesOnce",
	           "Software\\Microsoft\\Windows NT\\CurrentVersion\\Terminal Server\\Install\\".
	           "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
	           "Software\\Microsoft\\Windows NT\\CurrentVersion\\Terminal Server\\Install\\".
	           "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
	           "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
                   "Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\Shell",
	           "Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
                   "Microsoft\\Windows\\CurrentVersion\\Run",
                   "Microsoft\\Windows\\CurrentVersion\\RunOnce",
                   "Microsoft\\Windows\\CurrentVersion\\RunServices",
                   "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
                   "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                   "Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
                   "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
                   "Microsoft\\Windows NT\\CurrentVersion\\Terminal Server\\Install\\Software\\Microsoft\\".
                   "Windows\\CurrentVersion\\Run",
                   "Microsoft\\Windows NT\\CurrentVersion\\Terminal Server\\Install\\Software\\Microsoft\\".
                   "Windows\\CurrentVersion\\RunOnce");
	
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	
	foreach my $key_path (@run) {
		my $key;
		if ($key = $root_key->get_subkey($key_path)) {
			my %vals = getKeyValues($key);
			if (scalar(keys %vals) > 0) {
				foreach my $v (keys %vals) {
					::rptMsg($key->get_timestamp()."|".$key_path."|||".$vals{$v});
				}
			}
		}
	}
}

sub getKeyValues {
	my $key = shift;
	my %vals;
	
	my @vk = $key->get_list_of_values();
	if (scalar(@vk) > 0) {
		foreach my $v (@vk) {
			next if ($v->get_name() eq "" && $v->get_data() eq "");
			$vals{$v->get_name()} = $v->get_data();
		}
	}
	else {
	
	}
	return %vals;
}
	
