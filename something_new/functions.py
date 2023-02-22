import string
import secrets
import sys
import subprocess

def RandomPassword(pwd_length, Symbols, Numbers, Letters, Upper, Lower, noambiguous, nosimilar):
    digits = ''
    special_chars = ''
    
    if Symbols == True:
        special_chars = string.punctuation
    if Numbers == True:
        digits = string.digits
    if Letters == True:
        letters = string.ascii_letters
    if Upper == True:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if Lower == True:
        letters = "abcdefghijklmnopqrstuvwxyz"
    if Upper == True and Lower == True:
        letters = string.ascii_letters
    if noambiguous == True:
        special_chars = '!#$%&*+-.:=?@'
    if nosimilar == True:
        letters = "abcdfhjkmnpqrstuvwxyzABCDEFGHJKMNOPQRSTUVWXYZ"
        digits = "23456789"
    
        

    alphabet = letters + digits + special_chars
    pwd = ''
    for i in range(pwd_length):
        pwd += ''.join(secrets.choice(alphabet))

    return(pwd)

def OulookSignature(email):
    command = """$appid = "730bcbdb-aa50-45b6-877a-02a76b398e0b"
Connect-ExchangeOnline -AppId $appid -CertificateThumbprint "47A891A1A3771D90137B091D271F22D1C9AD5F22" -Organization "Mynster9361.onmicrosoft.com"
get-MailboxMessageConfiguration -Identity "Morten@Mynster-IT.dk" | Select-Object -ExpandProperty SignatureHtml"""
    subprocess.Popen(["powershell","& {" + command+ "}"], stdin=subprocess.PIPE,stdout=subprocess.PIPE, shell=True)
    stdout_value = process.communicate()[0]
    return stdout_value
    #cmd = ["PowerShell", "-ExecutionPolicy", "Unrestricted", "-File", ".\\lookupsignature.ps1", email]  # Specify relative or absolute path to the script
    #ec = subprocess.call(cmd)
    #print("Powershell returned: {0:d}".format(ec))
    #return("")
    
