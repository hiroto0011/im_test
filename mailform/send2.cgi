#!/usr/bin/perl

## SYNCKGRAPHICA Mailform 6.8 / UPDATE::2014-05-02

use Jcode;

########################################################################
##一般的な設定##########################################################
########################################################################

#00.テスト時の誤送信を制御 / 0にしないとメールが飛びません
$conf{'debug'} = 0;

#03.スパムブロック([URL]や[LINK]、<a>タグが含まれた送信をブロック) 1:ON / 0:OFF
$conf{'spam_block'} = 1;

#03-01.送信文字列にURLが含まれる場合に送信をブロック 1:ON / 0:OFF
$conf{'spam_url_block'} = 1;

#03-02.スパム判定時に表示されるメッセージ
$conf{'spam_message'} = 'スパム行為の可能性があるため、送信できません。<br />送信内容にURLを含める事はできません。';

#04.sendmailのパス(サーバ会社へお問い合わせ下さい)
$conf{'sendmail'} = '/usr/sbin/sendmail';

#06.設置者のアドレス(カンマ区切り)
$conf{'mailto'} = 'info@illust-market.com';

#07.送信完了時にリダイレクトするサンクスページ
$conf{'thanks'} = '../index.html';

#08.設置者に届くメールの件名
$conf{'subject'} = '「illust-market」採用情報から';

#09.送信者に届くメールの件名
$conf{'res_subject'} = '採用エントリーありがとうございました';

#10.送信者に届くメールの本文
$conf{'res_body'} = <<'__res_body_eof__';
この度は、採用エントリーいただきまして、誠にありがとうございました。

─ご送信内容の確認─────────────────
<resbody>
──────────────────────────

このメールに心当たりの無い場合は、お手数ですが
下記のメールアドレスまでお問い合わせください。

この度はお問い合わせ重ねてお礼申し上げます。
━━━━━━━━━━━━━━━━━━━━━━━━━━
Illust Market
営業時間/平日１０時～１９時
定休日　/土日祝
☎TEL　０３-６４１３-８４２８
📠FAX　０３-６４１３-８４２９
━━━━━━━━━━━━━━━━━━━━━━━━━━
__res_body_eof__


#11.Yahooジオシティーズ ジオプラス用設定 1:ON / 0:OFF
$conf{'geoplus'} = 0;

########################################################################
##高度な設定############################################################
########################################################################

#01.リファラーによるスパムチェック 1:ON / 0:OFF
$conf{'domain_check'} = 1;

#01.リファラー(送信元)のURLの一部か全部
$conf{'domain'} = $ENV{'SERVER_NAME'};

#02.HTML側での設定を無効化(タダ乗り対策) 1:ON / 0:OFF
$conf{'html_vals_disabled'} = 1;

#03.全てが英文の送信を拒否 1:ON / 0:OFF
$conf{'language_check'} = 1;

#04.Javascript非動作スパムチェック 1:ON / 0:OFF
$conf{'javascript'} = 0;

#11.通し番号保存用のファイルのパス
$conf{'serial_file'} = 'count1.dat';

#12.件名に通し番号を付ける 1:ON / 0:OFF
$conf{'subject_serial'} = 1;

#12.送信履歴保存用ファイルとダウンロードパスワード
$conf{'log_file'} = 'register2.csv';
$conf{'log_passwd'} = 'sucseed';

#13.送信文字コード
$conf{'charset'} = 'ISO-2022-JP';
$conf{'lang'} = 1;

#無変換設定
$conf{'charset'} = 'UTF-8';
$conf{'lang'} = 0;


########################################################################
##MAIN##################################################################
########################################################################
($sec,$min,$hour,$day,$mon,$year) = localtime(time);$mon++;$year += 1900;
$posted_body = sprintf("%04d-%02d-%02d %02d:%02d:%02d\n\n",$year,$mon,$day,$hour,$min,$sec);
$conf{'download_file_name'} = sprintf("%04d-%02d-%02d.csv",$year,$mon,$day,$hour,$min,$sec);
push @field, "DATE";
push @record, sprintf("%04d-%02d-%02d %02d:%02d:%02d",$year,$mon,$day,$hour,$min,$sec);

$spam{"lang"} = 1;
$spam{"link"} = 0;

@construct_utf = ("－","～");
#@construct_utf = ("\xef\xbc\x8d","\xE3\x80\x9C");
@construct_jis = ("\x1b\x24B\x21\x5d\x1b\x28J","\x1b\x24B\x21A\x1b\x28J");
@construct_sjis = ("\x81\x7c","\x81\x60");

&getQuery;
&main;
exit;
sub main {
	if($ENV{'QUERY_STRING'} eq 'download' && $conf{'log_passwd'} eq $form{'password'} && $conf{'log_passwd'} ne $null){
		&download;
	}
	elsif($ENV{'QUERY_STRING'} eq 'download'){
		&downloadscreen;
	}
	else {
		&send;
	}
}
sub send {
	if(&spamcheck){
		if(!$conf{'debug'}){
			@mailto = split(/\,/,$conf{'mailto'});
			if(@mailto > 0){
				&serials;
				if($mailfrom =~ /[^a-zA-Z0-9\.\@\-\_\+]/ || split(/\@/,$mailfrom) != 2){
					$mailfrom = $mailto[0];
				}
				$conf{'subject'} = &charcodeExchange($conf{'subject'},"jis");
				$conf{'subject'} = &mimeenc($conf{'subject'});
				$admin_posted_body = &charcodeExchange($admin_posted_body,"jis");
				for($cnt=0;$cnt<@mailto;$cnt++){
					&sendmail($mailto[$cnt],$mailfrom,$conf{'subject'},$admin_posted_body);
				}
				$conf{'res_subject'} = &charcodeExchange($conf{'res_subject'},"jis");
				$conf{'res_subject'} = &mimeenc($conf{'res_subject'});
				$conf{'res_body'} = &charcodeExchange($conf{'res_body'},"jis");
				if($mailfrom ne $mailto[0] && $conf{'res_subject'} ne $null && $conf{'res_body'} ne $null){
					&sendmail($mailfrom,$mailto[0],$conf{'res_subject'},$conf{'res_body'});
				}
				&logfileCreate;
				&refresh($conf{'thanks'});
			}
		}
		else {
			&debug;
		}
	}
	else {
		&spamerror;
	}
}
sub spamcheck {
	if(($spam{"lang"}) && $conf{'language_check'}){
		return 0;
	}
	elsif(($spam{"link"}) && ($conf{'spam_block'})){
		return 0;
	}
	elsif(($spam{"url"}) && ($conf{'spam_url_block'})){
		return 0;
	}
	elsif(($spam{"javascript"}) && ($conf{'javascript'})){
		return 0;
	}
	elsif(index($ENV{'HTTP_REFERER'},$conf{'domain'}) == -1 && ($conf{'domain_check'})){
		return 0;
	}
	else {
		return 1;
	}
}
sub serials {
	if(-f $conf{"serial_file"}){
		$serial = &loadline($conf{"serial_file"});
		$serial_number = sprintf("%04d",$serial);
		push @field, "SERIAL";
		push @csv, $serial_number;
		$form{"serial"} = $serial_number;
		$conf{"subject"} = "\[" . $serial_number . "\] " . $conf{"subject"};
		if($conf{'subject_serial'}){
			$conf{"res_subject"} = "\[" . $serial_number . "\] " . $conf{"res_subject"};
		}
		$serial++;
		&saveline($conf{"serial_file"},$serial);
	}
}
sub charcodeExchange {
	my($str,$charset) = @_;
	if($conf{'lang'}){
		if($charset eq "jis"){
			return &encodeJIS($str);
		}
		else {
			return &encodeSJIS($str);
		}
	}
	else {
		return $str;
	}
}
sub mimeenc {
	my($str) = @_;
	if($conf{'lang'}){
		return Jcode->new($str)->mime_encode;
	}
	else {
		return $str;
	}
}
sub encodeJIS {
	my($str) = @_;
	for(my $cnt=0;$cnt<@construct_utf;$cnt++){
		$str =~ s/$construct_utf[$cnt]/<\_hotfix${cnt}\_>/g;
	}
	Jcode::convert(\$str,'jis');
	$str = &charhotfix_unescape_jis($str);
	return $str;
}
sub encodeSJIS {
	my($str) = @_;
	for(my $cnt=0;$cnt<@construct_utf;$cnt++){
		$str =~ s/$construct_utf[$cnt]/<\_hotfix${cnt}\_>/g;
	}
	Jcode::convert(\$str,'sjis');
	$str = &charhotfix_unescape_sjis($str);
	return $str;
}
sub charhotfix_unescape_jis {
	my($str) = @_;
	for(my $cnt=0;$cnt<@construct_utf;$cnt++){
		$str =~ s/<\_hotfix${cnt}\_>/$construct_jis[$cnt]/g;
	}
	return $str;
}
sub charhotfix_unescape_sjis {
	my($str) = @_;
	for(my $cnt=0;$cnt<@construct_utf;$cnt++){
		$str =~ s/<\_hotfix${cnt}\_>/$construct_sjis[$cnt]/g;
	}
	return $str;
}
sub getQuery {
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}
	else {
		$buffer = $ENV{'QUERY_STRING'};
	}
	$spam{"javascript"} = 1;
	@pairs = split(/&/, $buffer);
	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair);
		$name =~ tr/+/ /;
		$name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		if($name eq "email"){
			$posted_body .= "\n\[ ${name} \] ${value}";
			push @field,$name;
			push @record,$value;
			$mailfrom = $value;
			$mailfrom =~ s/ //ig;
			$mailfrom =~ s/\t//ig;
			$mailfrom =~ s/\n//ig;
		}
		elsif($name ne $null && $name ne "Submit" && $name ne "confirm_email" && $name ne "x" && $name ne "y" && $name ne "javascriptcheck"){
			if($name ne $prev_name){
				$crr = "";
				if(index($value,"\n") > -1){
					$crr = "\n";
				}
				$posted_body .= "\n\[ ${name} \] ${crr}${value}${crr}";
				push @field,$name;
				push @record,$value;
			}
			else {
				$form{$name} .= "、";
				$posted_body .= "、${value}";
				$record[-1] .= "、${value}";
			}
			if(!($value !~ /[\x80-\xff]/)){
				$spam{"lang"} = 0;
			}
			if($value =~ /\[\/url\]/si || $value =~ /\[\/link\]/si || $value =~ /\<\/a\>/si){
				$spam{"link"} = 1;
			}
			if($value =~ /http\:\/\//si || $value =~ /https\:\/\//si){
				$spam{"url"} = 1;
			}
		}
		elsif($name eq 'javascriptcheck' && $value eq 'enabled'){
			$spam{"javascript"} = 0;
		}
		$check_values .= $value;
		$form{$name} .= $value;
		$prev_name = $name;
	}
	my($ip_address) = $ENV{'REMOTE_ADDR'};
	my(@addr) = split(/\./, $ip_address);
	my($packed_addr) = pack("C4", $addr[0], $addr[1], $addr[2], $addr[3]);
	my($name, $aliases, $addrtype, $length, @addrs);
	($name, $aliases, $addrtype, $length, @addrs) = gethostbyaddr($packed_addr, 2);
	$admin_posted_body .= "\n\n\[ HOST NAME \] ${name}\n";
	$admin_posted_body .= "\[ IP ADDRESS \] $ENV{'REMOTE_ADDR'}\n";
	$admin_posted_body .= "\[ USER AGENT \] $ENV{'HTTP_USER_AGENT'}\n";
	$admin_posted_body .= "\[ HTTP REFERER \] $ENV{'HTTP_REFERER'}";
	$admin_posted_body = $posted_body . $admin_posted_body;
	$conf{'res_body'} =~ s/<resbody>/$posted_body/g;
	push @field,"HOST NAME";
	push @record,$name;
	push @field,"IP ADDRESS";
	push @record,$ENV{'REMOTE_ADDR'};
	push @field,"USER AGENT";
	push @record,$ENV{'HTTP_USER_AGENT'};
	push @field,"HTTP REFERER";
	push @record,$ENV{'HTTP_REFERER'};
	$field = "\"" . join("\"\,\"",@field) . "\"\n";
	$record = "\"" . join("\"\,\"",@record) . "\"\n";
	$field .= $record;
}

sub refresh {
	my($refreshurl) = @_;
	print "Location: ${refreshurl}\n\n";
}

sub logfileCreate {
	if($conf{"log_file"} ne $null && $conf{"log_passwd"} ne $null){
		$size = -s $conf{"log_file"};
		if(-f $conf{"log_file"} && $size > 0){
			chmod 0777, $conf{"log_file"};
			$put_field = &encodeSJIS($record);
			flock(FH, LOCK_EX);
				open(FH,">>".$conf{"log_file"});
					print FH $put_field;
				close(FH);
			flock(FH, LOCK_NB);
			chmod 0600, $conf{"log_file"};
		}
		else{
			$put_field = &encodeSJIS($field);
			flock(FH, LOCK_EX);
				open(FH,">".$conf{"log_file"});
					print FH $put_field;
				close(FH);
			flock(FH, LOCK_NB);
			chmod 0600, $conf{"log_file"};
		}
	}
}

sub sendmail {
	my($mailto,$mailfrom,$subject,$body) = @_;
	if($conf{'geoplus'}){
		$mailfrom = $conf{'mailto'};
		sleep(3);
	}
	open(MAIL,"| $conf{'sendmail'} -f $mailfrom -t");
		print MAIL "To: $mailto\n";
		print MAIL "Errors-To: $mailto\n";
		print MAIL "From: $mailfrom\n";
		print MAIL "Subject: $subject\n";
		print MAIL "MIME-Version:1.0\n";
		print MAIL "Content-type:text/plain; charset=$conf{'charset'}\n";
		print MAIL "Content-Transfer-Encoding:7bit\n";
		print MAIL "X-Mailer:Web Mail Delivery System\n\n";
		print MAIL "$body\n";
	close(MAIL);
}

sub loadline {
	my($path) = @_;
	chmod 0777, $path;
	flock(FH, LOCK_EX);
		open(FH,$path);
			my($str) = <FH>;
		close(FH);
	flock(FH, LOCK_NB);
	chmod 0600, $path;
	return $str;
}
sub saveline {
	my($path,$str) = @_;
	chmod 0777, "${path}";
	flock(FH, LOCK_EX);
		open(FH,">${path}");
			print FH $str;
		close(FH);
	flock(FH, LOCK_NB);
	chmod 0600, "${save}";
}
sub saveaddline {
	my($path,$str) = @_;
	chmod 0777, "${path}";
	flock(FH, LOCK_EX);
		open(FH,">>${path}");
			print FH $str;
		close(FH);
	flock(FH, LOCK_NB);
	chmod 0600, "${save}";
}
sub spamerror {
	print "Content-type: text/html\n\n";
	print "<html>\n";
	print "\t<head>\n";
	print "\t\t<title>SPAM BLOCK</title>\n";
	print "\t</head>\n";
	print "\t<body>\n";
	print "\t\t<h1>SPAM BLOCK</h1>\n";
	print "\t\t<p>$conf{'spam_message'}</p>\n";
	print "</body></html>\n";
}
sub debug {
	print "Content-type: text/html\n\n";
	print "<html>\n";
	print "\t<head>\n";
	print "\t\t<title>DEBUG</title>\n";
	print "\t</head>\n";
	print "\t<body>\n";
	print "\t\t<h1>DEBUG</h1>\n";
	print "</body></html>\n";
}
sub downloadscreen {
	print "Content-type: text/html\n\n";
	print "<html>\n";
	print "\t<head>\n";
	print "\t\t<title>mode::logfile download</title>\n";
	print "\t\t<style type=\"text/css\">\n";
	print "\t\t<!--\n";
	print "\t\t* {\n";
	print "\t\t\tfont-family: \"Arial\", \"Helvetica\", \"sans-serif\";font-size: 12px;\n";
	print "\t\t}\n";
	print "\t\t-->\n";
	print "\t\t</style>\n";
	print "\t</head>\n";
	print "\t<body>\n";
	print "\t\t<h1 style=\"font-size: 21px;color: #232323;\">mode::logfile download</h1>\n";
	print "\t\t<form name=\"getLogs\" action=\"\" method=\"POST\">\n";
	print "\t\t\tPASSWORD <input type=\"password\" name=\"password\" style=\"ime-mode: disabled;width: 300px;\"><input type=\"submit\" value=\"GET LOG FILE\">\n";
	print "\t\t</form></body></html>\n";
}

sub download {
	chmod 0777, $conf{'log_file'};
	print "Content-type: application/octet-stream; name=\"$conf{'log_file'}\"\n";
	print "Content-Disposition: attachment; filename=\"$conf{'download_file_name'}\"\n\n";
	open(IN,$conf{'log_file'});
	print <IN>;
	chmod 0600, $conf{'log_file'};
}
1;