import subprocess

#import app_config
#completed = subprocess.run(["powershell", "-Command", "$secpasswd = ConvertTo-SecureString -String \'N9wjM3&B&"nz"5x#\' -AsPlainText -Force; $o365cred = New-Object System.Management.Automation.PSCredential (\'SVC.OMSEXCH_M@bestseller.com\', $secpasswd); Connect-ExchangeOnline -credential $o365cred; Get-Mailbox morten.kristensen@bestseller.com | Get-MailboxMessageConfiguration | select SignatureHtml -ExpandProperty SignatureHtml'], capture_output=True)

completed = subprocess.run(["powershell", "-Command", 'Import-Module Microsoft.PowerShell.Security; import-module ExchangeOnlineManagement; $secpasswd = ConvertTo-SecureString -String "N9wjM3&B&\"nz\"5x#" -AsPlainText -Force; $o365cred = New-Object System.Management.Automation.PSCredential ("SVC.OMSEXCH_M@bestseller.com", $secpasswd); Connect-ExchangeOnline -credential $o365cred; Get-Mailbox morten.kristensen@bestseller.com | Get-MailboxMessageConfiguration | select SignatureHtml -ExpandProperty SignatureHtml'], capture_output=True)
print(completed)
